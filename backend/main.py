"""
main.py — FinSense AI Loan Assistant
Industry-standard MVP with all 13 fixes applied.
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from dotenv import load_dotenv
from datetime import datetime
import time, hashlib, threading, os

from database import (
    init_db, get_session, update_session, reset_session,
    log_audit, get_audit, save_application,
    increment_stat, get_stats, create_user, get_user,
)
from auth import hash_password, verify_password, create_token, decode_token
from agents.verification_agent import verify_kyc
from agents.underwriting_agent import check_eligibility, calculate_emi
from agents.sanction_agent import generate_sanction_letter, SANCTIONS_DIR
from logic.llm import rewrite_with_llm
from logic.validators import (
    is_valid_amount, extract_amount,
    is_valid_salary, extract_salary,
    is_valid_tenure, extract_tenure,
)

load_dotenv()
init_db()

app = FastAPI(title="FinSense AI Loan Assistant")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

bearer = HTTPBearer(auto_error=False)

# ── SLA limits per stage (seconds) ────────────────────────────────────────────
SLA_LIMITS = {"amount": 120, "aadhaar": 90, "tenure": 120, "salary": 120}
DRIFT_TIMEOUT = 180   # 3 min idle → session reset


# ── Auth helpers ──────────────────────────────────────────────────────────────
def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer)) -> str | None:
    if not creds:
        return None
    return decode_token(creds.credentials)


# ── Helpers ───────────────────────────────────────────────────────────────────
def make_ref_id(user_id: str) -> str:
    return "FSN-" + hashlib.md5(f"{user_id}{time.time()}".encode()).hexdigest()[:6].upper()


def pe(stage: str, agent: str, status: str,
       confidence: int = None, detail: str = "") -> dict:
    return {"stage": stage, "agent": agent, "status": status,
            "confidence": confidence, "detail": detail,
            "ts": datetime.now().strftime("%H:%M:%S")}


def r(user_id: str, text: str, pipeline_events=None, **extra) -> dict:
    return {
        "reply":           rewrite_with_llm(text),
        "pipeline_events": pipeline_events or [],
        "audit":           get_audit(user_id),
        **extra,
    }


def retry_with_backoff(fn, retries: int = 2, base_delay: float = 0.5):
    for attempt in range(retries):
        try:
            return fn()
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(base_delay * (2 ** attempt))


def simulate_webhook(event: str, user_id: str, detail: str):
    log_audit(user_id, "WEBHOOK_SENT",
              f"[{event}] → officer@finsense.com | {detail}",
              status="INFO")


# ── Background SLA + drift monitor ───────────────────────────────────────────
def _sla_monitor():
    """
    FIXED: Runs in background thread — proactively detects SLA breaches
    and process drift WITHOUT waiting for next user message.
    Checks every 10 seconds.
    """
    import sqlite3
    while True:
        time.sleep(10)
        try:
            conn = sqlite3.connect("finsense.db")
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT user_id, stage, stage_start, last_active
                FROM sessions
                WHERE stage NOT IN ('start','completed','escalated')
            """).fetchall()
            conn.close()

            now = time.time()
            for row in rows:
                uid   = row["user_id"]
                stage = row["stage"]
                s_start = row["stage_start"] or now
                l_active = row["last_active"] or now

                # SLA breach check
                limit = SLA_LIMITS.get(stage, 120)
                if (now - s_start) > limit:
                    increment_stat("sla_breaches")
                    log_audit(uid, "SLA_BREACH",
                              f"Stage '{stage}' exceeded {limit}s SLA",
                              status="ESCALATE")
                    simulate_webhook("SLA_BREACH", uid,
                                     f"Stage {stage} SLA breached")

                # Process drift check
                if (now - l_active) > DRIFT_TIMEOUT:
                    log_audit(uid, "SESSION_TIMEOUT",
                              f"Idle {int(now - l_active)}s — drift detected",
                              status="ESCALATE")
                    simulate_webhook("DRIFT_DETECTED", uid,
                                     f"Session idle at stage {stage}")
                    reset_session(uid)
        except Exception:
            pass


threading.Thread(target=_sla_monitor, daemon=True).start()


# ── Request / Response models ─────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    user_id: str = "default"


class AuthRequest(BaseModel):
    username: str
    password: str


# ── Auth endpoints ────────────────────────────────────────────────────────────
@app.post("/register")
def register(req: AuthRequest):
    if len(req.password) < 4:
        raise HTTPException(400, "Password must be at least 4 characters")
    if len(req.username.strip()) < 2:
        raise HTTPException(400, "Username must be at least 2 characters")
    ok = create_user(req.username.strip(), hash_password(req.password))
    if not ok:
        raise HTTPException(409, "Username already exists")
    token = create_token(req.username.strip().lower())
    return {"token": token, "username": req.username.strip()}


@app.post("/login")
def login(req: AuthRequest):
    user = get_user(req.username.strip())
    if not user or not verify_password(req.password, user["hashed_pw"]):
        raise HTTPException(401, "Invalid username or password")
    token = create_token(user["username"])
    return {"token": token, "username": user["username"]}


# ── Main chat endpoint ────────────────────────────────────────────────────────
@app.post("/chat")
def chat(req: ChatRequest):
    t0          = time.time()
    user_msg    = req.message.strip()
    user_lower  = user_msg.lower()
    state       = get_session(req.user_id)
    stage       = state["stage"]
    pipeline_ev = []

    # Update activity
    update_session(req.user_id, last_active=time.time())

    # Restart completed session
    if stage == "completed" and "loan" in user_lower:
        reset_session(req.user_id)
        stage = "start"

    # ── START ─────────────────────────────────────────────────────────────────
    if stage == "start":
        if any(w in user_lower for w in ["no", "cancel", "stop"]):
            return r(req.user_id, "No worries 😊 Type: I want a loan whenever you're ready.")

        if "loan" in user_lower:
            update_session(req.user_id, stage="amount",
                           start_time=time.time(), stage_start=time.time())
            log_audit(req.user_id, "SESSION_START", "User initiated loan request")
            pipeline_ev.append(pe("start", "Orchestrator", "COMPLETED",
                                   detail="Session started"))
            return r(req.user_id,
                     "Great 👍 How much loan amount are you looking for? (e.g. 5 lakh or 500000)",
                     pipeline_ev)

        return r(req.user_id,
                 "Hi 👋 I'm FinSense 🤖 — your AI loan assistant.\nType: I want a loan to begin.")

    # ── AMOUNT ────────────────────────────────────────────────────────────────
    elif stage == "amount":
        if not is_valid_amount(user_lower):
            return r(req.user_id,
                     "Please enter a valid amount between ₹10,000 and ₹50,00,000 (e.g. 5 lakh).")
        amt = extract_amount(user_lower)
        update_session(req.user_id, amount=amt, stage="aadhaar",
                       stage_start=time.time())
        log_audit(req.user_id, "AMOUNT_CAPTURED", f"₹{amt:,}", status="OK")
        pipeline_ev.append(pe("amount", "Orchestrator", "COMPLETED",
                               detail=f"₹{amt:,}"))
        return r(req.user_id,
                 "Got it! For document verification, please enter the last 4 digits of your Aadhaar.",
                 pipeline_ev)

    # ── AADHAAR ───────────────────────────────────────────────────────────────
    elif stage == "aadhaar":
        digits = "".join(c for c in user_msg if c.isdigit())
        if len(digits) != 4:
            return r(req.user_id,
                     "Please enter exactly the last 4 digits of your Aadhaar (e.g. 5678).")
        update_session(req.user_id, aadhaar=digits, stage="tenure",
                       stage_start=time.time())
        log_audit(req.user_id, "DOC_VERIFIED", f"Aadhaar XXXX-{digits}",
                  status="OK", rule="DOC_VERIFY_RULE_001",
                  explanation="Aadhaar 4-digit suffix validated")
        pipeline_ev.append(pe("doc_verify", "VerificationAgent", "COMPLETED",
                               confidence=95, detail="Aadhaar verified"))
        return r(req.user_id,
                 "Document verified ✅ For how many years would you like the loan? (1–30 years)",
                 pipeline_ev)

    # ── TENURE ────────────────────────────────────────────────────────────────
    elif stage == "tenure":
        if not is_valid_tenure(user_lower):
            return r(req.user_id,
                     "Please enter a valid tenure between 1 and 30 years.")
        ten = extract_tenure(user_lower)
        update_session(req.user_id, tenure=ten, stage="salary",
                       stage_start=time.time())
        log_audit(req.user_id, "TENURE_CAPTURED", f"{ten} years", status="OK")
        pipeline_ev.append(pe("tenure", "Orchestrator", "COMPLETED",
                               detail=f"{ten} years"))
        return r(req.user_id, "Thanks 😊 What is your monthly salary?", pipeline_ev)

    # ── SALARY → KYC → UNDERWRITING ──────────────────────────────────────────
    elif stage == "salary":
        if not is_valid_salary(user_lower):
            return r(req.user_id,
                     "Please enter a valid monthly salary between ₹10,000 and ₹10,00,000.")

        salary  = extract_salary(user_lower)
        state   = get_session(req.user_id)   # re-fetch with latest values
        aadhaar = state.get("aadhaar") or ""
        amount  = state.get("amount") or 0
        tenure  = state.get("tenure") or 5
        retries = state.get("kyc_retries") or 0

        update_session(req.user_id, salary=salary)
        log_audit(req.user_id, "SALARY_CAPTURED", f"₹{salary:,}", status="OK")
        pipeline_ev.append(pe("salary", "Orchestrator", "COMPLETED",
                               detail=f"₹{salary:,}"))

        # KYC — deterministic, single call, result stored in state
        try:
            kyc = retry_with_backoff(
                lambda: verify_kyc(aadhaar_suffix=aadhaar, retry=retries > 0),
                retries=2, base_delay=0.5
            )
        except Exception:
            kyc = {"kyc_verified": False, "confidence": 0, "route": "ESCALATE",
                   "route_msg": "KYC service unavailable", "checks": {},
                   "rule": "KYC_CONFIDENCE_RULE_001"}

        # Store KYC confidence in DB — used by underwriting (no re-call)
        update_session(req.user_id, kyc_confidence=kyc["confidence"])

        log_audit(req.user_id, "KYC_CHECK", kyc["route_msg"],
                  confidence=kyc["confidence"],
                  status="OK" if kyc["kyc_verified"] else "FAIL",
                  rule=kyc.get("rule"),
                  explanation=f"Confidence {kyc['confidence']}% → route: {kyc['route']}")

        pipeline_ev.append(pe("kyc", "VerificationAgent",
                               "COMPLETED" if kyc["kyc_verified"] else "FAILED",
                               confidence=kyc["confidence"],
                               detail=kyc["route_msg"]))

        if not kyc["kyc_verified"]:
            new_retries = retries + 1
            update_session(req.user_id, kyc_retries=new_retries)
            increment_stat("kyc_failures")

            if new_retries >= 2 or kyc["route"] == "ESCALATE":
                ref = make_ref_id(req.user_id)
                update_session(req.user_id, stage="escalated")
                increment_stat("escalations")
                log_audit(req.user_id, "ESCALATION",
                          f"Escalated — Ref: {ref}", status="ESCALATE")
                simulate_webhook("ESCALATION", req.user_id,
                                 f"KYC failed {new_retries}x — Ref: {ref}")
                pipeline_ev.append(pe("escalation", "EscalationHandler",
                                       "ESCALATED", detail=f"Ref: {ref}"))
                return r(req.user_id,
                         f"⚠️ KYC could not be verified. Your case is escalated to a loan officer. "
                         f"Reference ID: {ref}. You will be contacted within 24 hours.",
                         pipeline_ev, escalated=True, ref_id=ref)

            return r(req.user_id,
                     "❌ KYC verification failed. Please re-enter your salary to retry.",
                     pipeline_ev, kyc_failed=True, kyc_checks=kyc.get("checks", {}))

        # Underwriting — passes stored kyc_confidence, no second KYC call
        try:
            result = retry_with_backoff(
                lambda: check_eligibility(
                    user_id=req.user_id,
                    salary=salary,
                    requested_amount=amount,
                    tenure_years=tenure,
                    kyc_confidence=kyc["confidence"],   # passed through — FIXED
                ),
                retries=2, base_delay=0.5
            )
        except Exception:
            result = {"approved": False, "confidence": 0,
                      "rule_triggered": "SERVICE_ERROR",
                      "explanation": "Underwriting unavailable",
                      "message": "Service error. Please try again.",
                      "rules_checked": [], "kyc_confidence": kyc["confidence"],
                      "max_eligible_amount": 0}

        log_audit(req.user_id, "UNDERWRITING", result["message"],
                  confidence=result["confidence"],
                  status="APPROVED" if result["approved"] else "REJECTED",
                  rule=result.get("rule_triggered"),
                  explanation=result.get("explanation"))

        pipeline_ev.append(pe("underwriting", "UnderwritingAgent",
                               "APPROVED" if result["approved"] else "REJECTED",
                               confidence=result["confidence"],
                               detail=result.get("explanation", "")))

        elapsed_ms = int((time.time() - (state.get("start_time") or t0)) * 1000)
        increment_stat("total")
        increment_stat("total_ms", elapsed_ms)

        # ── APPROVED ──────────────────────────────────────────────────────────
        if result["approved"]:
            increment_stat("approved")
            emi_data = result.get("emi", {})
            ref      = make_ref_id(req.user_id)

            # Unique PDF per user — FIXED
            pdf_path = generate_sanction_letter(
                name=req.user_id.replace("_", " ").title(),
                amount=f"{amount:,}",
                tenure_years=tenure,
                emi=emi_data.get("emi", 0),
                total_payable=emi_data.get("total_payable", 0),
                annual_rate=emi_data.get("annual_rate", 10.5),
                ref_id=ref,
                credit_score=result.get("credit_score", 0),
                risk_profile=result.get("risk_profile", "N/A"),
                confidence=result.get("confidence", 0),
            )

            update_session(req.user_id, stage="completed")
            log_audit(req.user_id, "DECISION", "Loan APPROVED ✅",
                      confidence=result["confidence"], status="APPROVED",
                      rule="ALL_RULES_PASSED",
                      explanation=result.get("explanation"))
            log_audit(req.user_id, "SANCTION_GENERATED",
                      f"PDF: {pdf_path} — Ref: {ref}", status="OK")
            pipeline_ev.append(pe("sanction", "SanctionAgent", "COMPLETED",
                                   detail=f"Ref: {ref}"))
            simulate_webhook("LOAN_APPROVED", req.user_id,
                             f"₹{amount:,} approved — Ref: {ref}")

            save_application(
                req.user_id, ref_id=ref, amount=amount, tenure=tenure,
                salary=salary, decision="APPROVED",
                emi=emi_data.get("emi", 0),
                total_payable=emi_data.get("total_payable", 0),
                confidence=result.get("confidence"),
                kyc_conf=kyc["confidence"],
                credit_score=result.get("credit_score"),
                risk_profile=result.get("risk_profile"),
                pdf_path=pdf_path,
            )

            msg = (
                f"🎉 Congratulations! Your loan of ₹{amount:,} is APPROVED!\n\n"
                f"📊 Loan Summary:\n"
                f"• Amount: ₹{amount:,}\n"
                f"• Tenure: {tenure} years\n"
                f"• Monthly EMI: ₹{emi_data.get('emi', 0):,}\n"
                f"• Total Payable: ₹{emi_data.get('total_payable', 0):,}\n"
                f"• Interest Rate: {emi_data.get('annual_rate', 10.5)}% p.a.\n"
                f"• Risk Profile: {result.get('risk_profile')}\n\n"
                f"Reference ID: {ref}\nYour sanction letter is ready!"
            )
            return r(req.user_id, msg, pipeline_ev,
                     sanction_letter=True, ref_id=ref,
                     confidence=result["confidence"],
                     kyc_confidence=kyc["confidence"],
                     emi=emi_data,
                     rules_checked=result.get("rules_checked", []),
                     credit_score=result.get("credit_score"))

        # ── REJECTED ──────────────────────────────────────────────────────────
        else:
            increment_stat("rejected")
            max_amt = result.get("max_eligible_amount", 0)
            update_session(req.user_id, stage="recovery", max_eligible=max_amt)
            log_audit(req.user_id, "DECISION",
                      f"Loan REJECTED — {result.get('rule_triggered')}",
                      confidence=result["confidence"], status="REJECTED",
                      rule=result.get("rule_triggered"),
                      explanation=result.get("explanation"))
            simulate_webhook("LOAN_REJECTED", req.user_id,
                             result.get("explanation", ""))

            alt_emi = result.get("alt_emi", {})
            msg = (
                f"😔 Your loan request was not approved.\n\n"
                f"📋 Reason: {result.get('explanation')}\n"
                f"🔍 Rule: {result.get('rule_triggered')}\n\n"
                f"💡 Recovery Options:\n"
                f"• You are eligible for up to ₹{max_amt:,}\n"
                f"• EMI for ₹{max_amt:,}: ₹{alt_emi.get('emi', 0):,}/month\n\n"
                f"Reply 'yes' to apply for ₹{max_amt:,} instead."
            )
            return r(req.user_id, msg, pipeline_ev,
                     rejected=True, max_eligible=max_amt,
                     alt_emi=alt_emi,
                     confidence=result["confidence"],
                     rules_checked=result.get("rules_checked", []))

    # ── RECOVERY ──────────────────────────────────────────────────────────────
    elif stage == "recovery":
        state   = get_session(req.user_id)
        max_amt = state.get("max_eligible") or 0
        tenure  = state.get("tenure") or 5

        if any(w in user_lower for w in ["yes", "ok", "sure", "proceed", "agree"]):
            emi_data = calculate_emi(max_amt, tenure)
            ref      = make_ref_id(req.user_id)
            pdf_path = generate_sanction_letter(
                name=req.user_id.replace("_", " ").title(),
                amount=f"{max_amt:,}", tenure_years=tenure,
                emi=emi_data["emi"], total_payable=emi_data["total_payable"],
                ref_id=ref,
            )
            update_session(req.user_id, stage="completed")
            log_audit(req.user_id, "RECOVERY_ACCEPTED",
                      f"Alternative ₹{max_amt:,} accepted", status="APPROVED")
            increment_stat("approved")
            simulate_webhook("RECOVERY_APPROVED", req.user_id,
                             f"₹{max_amt:,} approved — Ref: {ref}")
            return r(req.user_id,
                     f"🎉 Your loan of ₹{max_amt:,} is approved!\n"
                     f"Monthly EMI: ₹{emi_data['emi']:,} for {tenure} years.\n"
                     f"Reference ID: {ref}",
                     sanction_letter=True, ref_id=ref, emi=emi_data)
        else:
            update_session(req.user_id, stage="completed")
            log_audit(req.user_id, "RECOVERY_DECLINED",
                      "User declined alternative offer", status="INFO")
            return r(req.user_id, "No problem 😊 Type: I want a loan to apply again.")

    # ── ESCALATED ─────────────────────────────────────────────────────────────
    elif stage == "escalated":
        return r(req.user_id,
                 "Your case is with our loan officer. "
                 "You'll be contacted within 24 hours. "
                 "Type: I want a loan to start a new application.")

    # ── COMPLETED ─────────────────────────────────────────────────────────────
    else:
        return r(req.user_id,
                 "Your loan process is completed. Type: I want a loan to apply again.")


# ── Endpoints ─────────────────────────────────────────────────────────────────
@app.get("/audit/{user_id}")
def audit_endpoint(user_id: str):
    return {"audit": get_audit(user_id)}


@app.get("/dashboard")
def dashboard_endpoint():
    s = get_stats()
    total = s.get("total") or 1
    return {
        "total_applications": s.get("total", 0),
        "approved":           s.get("approved", 0),
        "rejected":           s.get("rejected", 0),
        "approval_rate":      round(s.get("approved", 0) / total * 100, 1),
        "rejection_rate":     round(s.get("rejected", 0) / total * 100, 1),
        "kyc_failures":       s.get("kyc_failures", 0),
        "escalations":        s.get("escalations", 0),
        "sla_breaches":       s.get("sla_breaches", 0),
        "avg_processing_ms":  round(s.get("total_ms", 0) / total),
    }


@app.post("/demo")
def run_demo():
    """
    FIXED: Demo runs TWO scenarios — one approval, one rejection.
    Proves both happy path and failure recovery autonomously.
    """
    results = {}

    # Scenario 1: Approval (salary ₹50,000)
    demo_id = "demo_approved"
    reset_session(demo_id)
    steps_ok = []
    for msg in ["I want a loan", "5 lakh", "1234", "5 years", "50000"]:
        res = chat(ChatRequest(message=msg, user_id=demo_id))
        steps_ok.append({"input": msg, "reply": res.get("reply", "")})
    results["approval_scenario"] = {"steps": steps_ok,
                                     "audit": get_audit(demo_id)}

    # Scenario 2: Rejection + recovery (salary ₹15,000)
    demo_id2 = "demo_rejected"
    reset_session(demo_id2)
    steps_rej = []
    for msg in ["I want a loan", "5 lakh", "5678", "5 years", "15000", "yes"]:
        res = chat(ChatRequest(message=msg, user_id=demo_id2))
        steps_rej.append({"input": msg, "reply": res.get("reply", "")})
    results["rejection_recovery_scenario"] = {"steps": steps_rej,
                                               "audit": get_audit(demo_id2)}

    return {"mode": "autonomous_demo", **results}


@app.get("/download/{ref_id}")
def download_sanction(ref_id: str):
    """FIXED: unique PDF per ref_id — no race condition."""
    safe   = ref_id.replace("-", "_")
    path   = os.path.join(SANCTIONS_DIR, f"sanction_{safe}.pdf")
    if not os.path.exists(path):
        raise HTTPException(404, "Sanction letter not found")
    return FileResponse(path, media_type="application/pdf",
                        filename=f"sanction_{ref_id}.pdf")


# Legacy download — returns last generated (kept for backward compat)
@app.get("/download")
def download_legacy():
    import glob
    files = sorted(glob.glob(f"{SANCTIONS_DIR}/sanction_*.pdf"),
                   key=os.path.getmtime, reverse=True)
    if not files:
        raise HTTPException(404, "No sanction letter found")
    return FileResponse(files[0], media_type="application/pdf",
                        filename="sanction_letter.pdf")
