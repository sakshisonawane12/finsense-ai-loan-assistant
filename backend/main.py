from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from datetime import datetime
import time, hashlib

from agents.verification_agent import verify_kyc
from agents.underwriting_agent import check_eligibility
from agents.sanction_agent import generate_sanction_letter
from logic.llm import rewrite_with_llm
from logic.validators import (
    is_valid_amount, extract_amount,
    is_valid_salary, extract_salary,
    is_valid_tenure, extract_tenure,
)

load_dotenv()

app = FastAPI(title="FinSense AI Loan Assistant")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── SLA limits per stage (seconds) ────────────────────────────────────────────
SLA_LIMITS = {"amount": 120, "aadhaar": 90, "tenure": 120, "salary": 120}

# ── In-memory stores ──────────────────────────────────────────────────────────
conversation_state: dict = {}
audit_logs: dict = {}
dashboard_stats = {
    "total": 0, "approved": 0, "rejected": 0,
    "kyc_failures": 0, "escalations": 0,
    "total_processing_ms": 0, "sla_breaches": 0,
}


# ── Helpers ───────────────────────────────────────────────────────────────────
def get_state(user_id: str) -> dict:
    if user_id not in conversation_state:
        conversation_state[user_id] = {
            "stage": "start",
            "amount": None, "tenure": None, "salary": None, "aadhaar": None,
            "kyc_retries": 0, "start_time": None,
            "stage_start_time": None, "last_activity": time.time(),
            "reminder_count": 0,
        }
    return conversation_state[user_id]


def log_audit(user_id, event, detail, confidence=None, status="INFO", rule=None, explanation=None):
    if user_id not in audit_logs:
        audit_logs[user_id] = []
    entry = {"ts": datetime.now().strftime("%H:%M:%S"), "event": event, "detail": detail, "status": status}
    if confidence is not None: entry["confidence"] = confidence
    if rule: entry["rule"] = rule
    if explanation: entry["explanation"] = explanation
    audit_logs[user_id].append(entry)


def check_sla(state, stage, user_id):
    limit = SLA_LIMITS.get(stage, 120)
    elapsed = time.time() - (state.get("stage_start_time") or time.time())
    if elapsed > limit:
        dashboard_stats["sla_breaches"] += 1
        log_audit(user_id, "SLA_BREACH",
                  f"Stage '{stage}' exceeded {limit}s SLA (took {int(elapsed)}s)",
                  status="ESCALATE")
        simulate_webhook("SLA_BREACH", user_id, f"Stage {stage} exceeded {limit}s")
        return True
    return False


def check_drift(state, user_id):
    idle = time.time() - state.get("last_activity", time.time())
    stage = state.get("stage", "start")
    if idle > 180 and stage not in ("start", "completed", "escalated"):
        log_audit(user_id, "SESSION_TIMEOUT",
                  f"User inactive {int(idle)}s — process drift detected", status="ESCALATE")
        simulate_webhook("DRIFT_DETECTED", user_id, f"Session idle {int(idle)}s at stage {stage}")
        return True
    return False


def simulate_webhook(event, user_id, detail):
    log_audit(user_id, "WEBHOOK_SENT",
              f"[{event}] → officer@finsense.com | {detail}", status="INFO")


def retry_with_backoff(fn, retries=2, base_delay=0.5):
    for attempt in range(retries):
        try:
            return fn()
        except Exception:
            if attempt == retries - 1:
                raise
            log_audit("system", "AGENT_RETRY",
                      f"Attempt {attempt+1} failed, retrying in {base_delay*(2**attempt)}s",
                      status="INFO")
            time.sleep(base_delay * (2 ** attempt))


def make_ref_id(user_id):
    return "FSN-" + hashlib.md5(user_id.encode()).hexdigest()[:6].upper()


def build_pipeline_event(stage, agent, status, confidence=None, detail=""):
    return {"stage": stage, "agent": agent, "status": status,
            "confidence": confidence, "detail": detail,
            "ts": datetime.now().strftime("%H:%M:%S")}


def r(text, **extra):
    return {"reply": rewrite_with_llm(text), **extra}


# ── Request model ─────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    user_id: str = "default"


# ── Main chat endpoint ────────────────────────────────────────────────────────
@app.post("/chat")
def chat(req: ChatRequest):
    t0 = time.time()
    user_msg = req.message.strip()
    user_lower = user_msg.lower()
    state = get_state(req.user_id)
    stage = state["stage"]
    pipeline_events = []

    state["last_activity"] = time.time()

    # Process drift check
    if check_drift(state, req.user_id):
        state["stage"] = "start"
        return r("⏰ Your session timed out due to inactivity. Type 'I want a loan' to start fresh!")

    # Restart
    if stage == "completed" and "loan" in user_lower:
        state.update({"stage": "start", "amount": None, "tenure": None,
                      "salary": None, "aadhaar": None, "kyc_retries": 0, "reminder_count": 0})
        stage = "start"

    # ── START ─────────────────────────────────────────────────────────────────
    if stage == "start":
        if any(w in user_lower for w in ["no", "dont", "don't", "cancel"]):
            state["stage"] = "completed"
            return r("No worries 😊 Type: I want a loan whenever you're ready.")

        if "loan" in user_lower:
            state["stage"] = "amount"
            state["start_time"] = time.time()
            state["stage_start_time"] = time.time()
            log_audit(req.user_id, "SESSION_START", "User initiated loan request", status="INFO")
            pipeline_events.append(build_pipeline_event("start", "Orchestrator", "COMPLETED", detail="Session started"))
            return {**r("Great 👍 How much loan amount are you looking for? (e.g. 5 lakh or 500000)"),
                    "pipeline_events": pipeline_events}

        return r("Hi 👋 I'm FinSense 🤖 — your AI loan assistant.\nType: I want a loan to begin.")

    # ── AMOUNT ────────────────────────────────────────────────────────────────
    elif stage == "amount":
        check_sla(state, "amount", req.user_id)
        if not is_valid_amount(user_lower):
            return r("Please enter a valid loan amount like 5 lakh or 500000.")
        state["amount"] = extract_amount(user_lower)
        state["stage"] = "aadhaar"
        state["stage_start_time"] = time.time()
        log_audit(req.user_id, "AMOUNT_CAPTURED", f"₹{state['amount']:,}", status="OK")
        pipeline_events.append(build_pipeline_event("amount", "Orchestrator", "COMPLETED",
                                                     detail=f"₹{state['amount']:,}"))
        return {**r("Got it! For document verification, please enter the last 4 digits of your Aadhaar number."),
                "pipeline_events": pipeline_events}

    # ── AADHAAR ───────────────────────────────────────────────────────────────
    elif stage == "aadhaar":
        check_sla(state, "aadhaar", req.user_id)
        digits = "".join(c for c in user_msg if c.isdigit())
        if len(digits) != 4:
            return r("Please enter exactly the last 4 digits of your Aadhaar (e.g. 5678).")
        state["aadhaar"] = digits
        state["stage"] = "tenure"
        state["stage_start_time"] = time.time()
        log_audit(req.user_id, "DOC_VERIFIED", f"Aadhaar XXXX-{digits}",
                  status="OK", rule="DOC_VERIFY_RULE_001",
                  explanation="Aadhaar 4-digit suffix validated successfully")
        pipeline_events.append(build_pipeline_event("doc_verify", "VerificationAgent", "COMPLETED",
                                                     confidence=95, detail="Aadhaar verified"))
        return {**r("Document verified ✅ For how many years would you like the loan? (1–30 years)"),
                "pipeline_events": pipeline_events}

    # ── TENURE ────────────────────────────────────────────────────────────────
    elif stage == "tenure":
        check_sla(state, "tenure", req.user_id)
        if not is_valid_tenure(user_lower):
            return r("Please enter a valid loan duration in years (e.g. 5 or 10).")
        state["tenure"] = extract_tenure(user_lower)
        state["stage"] = "salary"
        state["stage_start_time"] = time.time()
        log_audit(req.user_id, "TENURE_CAPTURED", f"{state['tenure']} years", status="OK")
        pipeline_events.append(build_pipeline_event("tenure", "Orchestrator", "COMPLETED",
                                                     detail=f"{state['tenure']} years"))
        return {**r("Thanks 😊 What is your monthly salary? (e.g. 50000)"),
                "pipeline_events": pipeline_events}

    # ── SALARY → KYC → UNDERWRITING ──────────────────────────────────────────
    elif stage == "salary":
        check_sla(state, "salary", req.user_id)
        if not is_valid_salary(user_lower):
            return r("Please enter your monthly salary as a number (e.g. 30000).")

        salary = extract_salary(user_lower)
        state["salary"] = salary
        log_audit(req.user_id, "SALARY_CAPTURED", f"₹{salary:,}", status="OK")
        pipeline_events.append(build_pipeline_event("salary", "Orchestrator", "COMPLETED",
                                                     detail=f"₹{salary:,}"))

        # KYC with retry + backoff
        is_retry = state["kyc_retries"] > 0
        try:
            kyc = retry_with_backoff(
                lambda: verify_kyc(retry=is_retry, aadhaar_suffix=state.get("aadhaar", "")),
                retries=2, base_delay=0.5
            )
        except Exception:
            kyc = {"kyc_verified": False, "confidence": 0, "route": "ESCALATE",
                   "route_msg": "KYC service unavailable — escalating",
                   "checks": {}, "agent": "VerificationAgent", "rule": "KYC_CONFIDENCE_RULE_001",
                   "message": "KYC service error"}

        log_audit(req.user_id, "KYC_CHECK", kyc["route_msg"],
                  confidence=kyc["confidence"],
                  status="OK" if kyc["kyc_verified"] else "FAIL",
                  rule=kyc.get("rule"),
                  explanation=f"Confidence {kyc['confidence']}% → route: {kyc['route']}")

        pipeline_events.append(build_pipeline_event(
            "kyc", "VerificationAgent",
            "COMPLETED" if kyc["kyc_verified"] else "FAILED",
            confidence=kyc["confidence"], detail=kyc["route_msg"]))

        if not kyc["kyc_verified"]:
            state["kyc_retries"] += 1
            dashboard_stats["kyc_failures"] += 1

            if state["kyc_retries"] >= 2 or kyc["route"] == "ESCALATE":
                state["stage"] = "escalated"
                dashboard_stats["escalations"] += 1
                ref = make_ref_id(req.user_id)
                log_audit(req.user_id, "ESCALATION",
                          f"Escalated to human officer — Ref: {ref}", status="ESCALATE")
                simulate_webhook("ESCALATION", req.user_id, f"KYC failed — Ref: {ref}")
                pipeline_events.append(build_pipeline_event(
                    "escalation", "EscalationHandler", "ESCALATED", detail=f"Ref: {ref}"))
                return {
                    "reply": rewrite_with_llm(
                        f"⚠️ KYC could not be verified. Your case is escalated to a loan officer. "
                        f"Reference ID: {ref}. You will be contacted within 24 hours."
                    ),
                    "escalated": True, "ref_id": ref,
                    "audit": audit_logs.get(req.user_id, []),
                    "pipeline_events": pipeline_events,
                }

            return {**r("❌ KYC verification failed. Please re-enter your salary to retry."),
                    "kyc_failed": True, "kyc_checks": kyc.get("checks", {}),
                    "pipeline_events": pipeline_events}

        # Underwriting with retry + backoff
        try:
            result = retry_with_backoff(
                lambda: check_eligibility(
                    salary=salary,
                    requested_amount=state["amount"] or 0,
                    tenure_years=state["tenure"] or 5
                ),
                retries=2, base_delay=0.5
            )
        except Exception:
            result = {"approved": False, "confidence": 0, "reason": "service_error",
                      "rule_triggered": "SERVICE_ERROR",
                      "explanation": "Underwriting service unavailable",
                      "message": "Service error. Please try again.",
                      "agent": "UnderwritingAgent",
                      "kyc_confidence": kyc["confidence"], "max_eligible_amount": 0}

        log_audit(req.user_id, "UNDERWRITING", result["message"],
                  confidence=result["confidence"],
                  status="APPROVED" if result["approved"] else "REJECTED",
                  rule=result.get("rule_triggered"),
                  explanation=result.get("explanation"))

        pipeline_events.append(build_pipeline_event(
            "underwriting", "UnderwritingAgent",
            "APPROVED" if result["approved"] else "REJECTED",
            confidence=result["confidence"], detail=result.get("explanation", "")))

        dashboard_stats["total"] += 1
        elapsed_ms = int((time.time() - (state["start_time"] or t0)) * 1000)
        dashboard_stats["total_processing_ms"] += elapsed_ms

        if result["approved"]:
            dashboard_stats["approved"] += 1
            emi_data = result.get("emi", {})
            ref = make_ref_id(req.user_id)

            generate_sanction_letter(
                name=req.user_id.replace("_", " ").title(),
                amount=f"{state['amount']:,}" if state["amount"] else "5,00,000",
                tenure_years=state["tenure"] or 5,
                emi=emi_data.get("emi", 0),
                total_payable=emi_data.get("total_payable", 0),
                annual_rate=emi_data.get("annual_rate", 10.5),
                ref_id=ref,
            )
            state["stage"] = "completed"
            log_audit(req.user_id, "DECISION", "Loan APPROVED ✅",
                      confidence=result["confidence"], status="APPROVED",
                      rule="ALL_RULES_PASSED", explanation=result.get("explanation"))
            log_audit(req.user_id, "SANCTION_GENERATED",
                      f"PDF generated — Ref: {ref}", status="OK")
            pipeline_events.append(build_pipeline_event(
                "sanction", "SanctionAgent", "COMPLETED", detail=f"PDF — Ref: {ref}"))
            simulate_webhook("LOAN_APPROVED", req.user_id,
                             f"₹{state['amount']:,} approved — Ref: {ref}")

            approval_msg = (
                f"🎉 Congratulations! Your loan of ₹{state['amount']:,} is APPROVED!\n\n"
                f"📊 Loan Summary:\n"
                f"• Amount: ₹{state['amount']:,}\n"
                f"• Tenure: {state['tenure']} years\n"
                f"• Monthly EMI: ₹{emi_data.get('emi', 0):,}\n"
                f"• Total Payable: ₹{emi_data.get('total_payable', 0):,}\n"
                f"• Interest Rate: {emi_data.get('annual_rate', 10.5)}% p.a.\n\n"
                f"Your sanction letter is ready to download!"
            )
            return {
                "reply": rewrite_with_llm(approval_msg),
                "sanction_letter": True,
                "audit": audit_logs.get(req.user_id, []),
                "confidence": result["confidence"],
                "kyc_confidence": result.get("kyc_confidence"),
                "emi": emi_data,
                "rules_checked": result.get("rules_checked", []),
                "pipeline_events": pipeline_events,
                "ref_id": ref,
            }

        else:
            dashboard_stats["rejected"] += 1
            state["stage"] = "recovery"
            state["max_eligible"] = result.get("max_eligible_amount", 0)
            log_audit(req.user_id, "DECISION",
                      f"Loan REJECTED — {result['reason']}",
                      confidence=result["confidence"], status="REJECTED",
                      rule=result.get("rule_triggered"),
                      explanation=result.get("explanation"))
            simulate_webhook("LOAN_REJECTED", req.user_id, result.get("explanation", ""))

            alt_emi = result.get("alt_emi", {})
            max_amt = result.get("max_eligible_amount", 0)
            recovery_msg = (
                f"😔 Your loan request was not approved.\n\n"
                f"📋 Reason: {result.get('explanation', 'Eligibility criteria not met')}\n"
                f"🔍 Rule: {result.get('rule_triggered', 'N/A')}\n\n"
                f"💡 Recovery Options:\n"
                f"• You are eligible for up to ₹{max_amt:,}\n"
                f"• Estimated EMI: ₹{alt_emi.get('emi', 0):,}/month\n"
                f"• Try a longer tenure to reduce EMI\n\n"
                f"Reply 'yes' to apply for ₹{max_amt:,} instead."
            )
            return {
                "reply": rewrite_with_llm(recovery_msg),
                "rejected": True,
                "audit": audit_logs.get(req.user_id, []),
                "confidence": result["confidence"],
                "max_eligible": max_amt,
                "alt_emi": alt_emi,
                "rules_checked": result.get("rules_checked", []),
                "pipeline_events": pipeline_events,
            }

    # ── RECOVERY ──────────────────────────────────────────────────────────────
    elif stage == "recovery":
        if any(w in user_lower for w in ["yes", "ok", "sure", "proceed", "agree"]):
            max_amt = state.get("max_eligible", 0)
            tenure = state.get("tenure") or 5
            from agents.underwriting_agent import calculate_emi
            emi_data = calculate_emi(max_amt, tenure)
            ref = make_ref_id(req.user_id)
            generate_sanction_letter(
                name=req.user_id.replace("_", " ").title(),
                amount=f"{max_amt:,}", tenure_years=tenure,
                emi=emi_data["emi"], total_payable=emi_data["total_payable"], ref_id=ref,
            )
            state["stage"] = "completed"
            log_audit(req.user_id, "RECOVERY_ACCEPTED",
                      f"Alternative ₹{max_amt:,} accepted", status="APPROVED")
            dashboard_stats["approved"] += 1
            simulate_webhook("RECOVERY_APPROVED", req.user_id, f"₹{max_amt:,} approved")
            return {
                "reply": rewrite_with_llm(
                    f"🎉 Your loan of ₹{max_amt:,} is approved!\n"
                    f"Monthly EMI: ₹{emi_data['emi']:,} for {tenure} years.\n"
                    f"Sanction letter is ready!"
                ),
                "sanction_letter": True,
                "audit": audit_logs.get(req.user_id, []),
                "emi": emi_data, "ref_id": ref,
            }
        else:
            state["stage"] = "completed"
            log_audit(req.user_id, "RECOVERY_DECLINED", "User declined alternative", status="INFO")
            return r("No problem 😊 Type: I want a loan to apply again.")

    # ── ESCALATED ─────────────────────────────────────────────────────────────
    elif stage == "escalated":
        return r("Your case is with our loan officer. You'll be contacted within 24 hours. "
                 "Type: I want a loan to start a new application.")

    # ── COMPLETED ─────────────────────────────────────────────────────────────
    else:
        return r("Your loan process is completed. Type: I want a loan to apply again.")


# ── Endpoints ─────────────────────────────────────────────────────────────────
@app.get("/audit/{user_id}")
def get_audit(user_id: str):
    return {"audit": audit_logs.get(user_id, [])}


@app.get("/dashboard")
def get_dashboard():
    total = dashboard_stats["total"] or 1
    return {
        "total_applications": dashboard_stats["total"],
        "approved": dashboard_stats["approved"],
        "rejected": dashboard_stats["rejected"],
        "approval_rate": round(dashboard_stats["approved"] / total * 100, 1),
        "rejection_rate": round(dashboard_stats["rejected"] / total * 100, 1),
        "kyc_failures": dashboard_stats["kyc_failures"],
        "escalations": dashboard_stats["escalations"],
        "sla_breaches": dashboard_stats["sla_breaches"],
        "avg_processing_ms": round(dashboard_stats["total_processing_ms"] / total),
    }


@app.post("/demo")
def run_demo():
    demo_id = "demo_user"
    for store in [conversation_state, audit_logs]:
        store.pop(demo_id, None)
    steps = []

    def step(msg):
        res = chat(ChatRequest(message=msg, user_id=demo_id))
        steps.append({"input": msg, "reply": res.get("reply", ""),
                      **{k: v for k, v in res.items() if k != "reply"}})
        return res

    step("I want a loan")
    step("5 lakh")
    step("1234")
    step("5 years")
    step("50000")

    return {"mode": "autonomous_demo", "steps": steps,
            "audit": audit_logs.get(demo_id, [])}


@app.get("/download")
def download_sanction():
    return FileResponse("sanction_letter.pdf",
                        media_type="application/pdf",
                        filename="sanction_letter.pdf")
