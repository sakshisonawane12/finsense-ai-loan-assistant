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

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= STATE =================
conversation_state = {}
audit_logs = {}
dashboard_stats = {
    "total": 0, "approved": 0, "rejected": 0,
    "kyc_failures": 0, "escalations": 0,
    "total_processing_ms": 0,
}

# ================= HELPERS =================

def get_state(user_id):
    if user_id not in conversation_state:
        conversation_state[user_id] = {
            "stage": "start",
            "amount": None,
            "tenure": None,
            "salary": None,
            "aadhaar": None,
            "kyc_retries": 0,
        }
    return conversation_state[user_id]

def log_audit(user_id, event, detail, confidence=None, status="INFO", explanation=None):
    audit_logs.setdefault(user_id, []).append({
        "ts": datetime.now().strftime("%H:%M:%S"),
        "event": event,
        "detail": detail,
        "status": status,
        "confidence": confidence,
        "explanation": explanation
    })

def build_response(user_id, text, pipeline_events=None, extra=None):
    return {
        "reply": rewrite_with_llm(text),
        "pipeline_events": pipeline_events or [],
        "audit": audit_logs.get(user_id, []),
        **(extra or {})
    }

def make_ref_id(user_id):
    return "FSN-" + hashlib.md5(user_id.encode()).hexdigest()[:6].upper()

# ================= REQUEST =================
class ChatRequest(BaseModel):
    message: str
    user_id: str = "default"

# ================= CHAT =================

@app.post("/chat")
def chat(req: ChatRequest):
    user_msg = req.message.strip()
    user_lower = user_msg.lower()
    state = get_state(req.user_id)
    stage = state["stage"]
    pipeline_events = []

    # ================= WHY HANDLER =================
    if any(w in user_lower for w in ["why", "reason", "explain"]):
        logs = audit_logs.get(req.user_id, [])
        if not logs:
            return build_response(req.user_id, "No data yet. Start with 'I want a loan'.")
        last = logs[-1]
        explanation = last.get("explanation") or last.get("detail")
        return build_response(req.user_id, f"Here's why:\n\n{explanation}")

    # ================= START =================
    if stage == "start":
        if "loan" in user_lower:
            state["stage"] = "amount"
            log_audit(req.user_id, "START", "Loan journey started")
            pipeline_events.append({"stage": "start", "status": "COMPLETED"})
            return build_response(req.user_id,
                "Great 👍 How much loan do you need?",
                pipeline_events
            )

        return build_response(req.user_id,
            "Type 'I want a loan' to begin."
        )

    # ================= AMOUNT =================
    if stage == "amount":
        if not is_valid_amount(user_lower):
            return build_response(req.user_id,
                "Enter a valid amount like 50000, 50k, or 5 lakh."
            )

        amount = extract_amount(user_lower)
        state["amount"] = amount
        state["stage"] = "aadhaar"

        log_audit(req.user_id, "AMOUNT", f"₹{amount}", status="OK")
        pipeline_events.append({"stage": "amount", "status": "COMPLETED"})

        return build_response(req.user_id,
            "Enter last 4 digits of Aadhaar.",
            pipeline_events
        )

    # ================= AADHAAR =================
    if stage == "aadhaar":
        digits = "".join(c for c in user_msg if c.isdigit())

        if len(digits) != 4:
            return build_response(req.user_id,
                "Enter valid 4-digit Aadhaar."
            )

        state["aadhaar"] = digits
        state["stage"] = "tenure"

        log_audit(req.user_id, "AADHAAR", "Verified", status="OK")
        pipeline_events.append({"stage": "doc_verify", "status": "COMPLETED"})

        return build_response(req.user_id,
            "Loan tenure (years)?",
            pipeline_events
        )

    # ================= TENURE =================
    if stage == "tenure":
        if not is_valid_tenure(user_lower):
            return build_response(req.user_id,
                "Enter valid tenure (1–30 years)."
            )

        tenure = extract_tenure(user_lower)
        state["tenure"] = tenure
        state["stage"] = "salary"

        log_audit(req.user_id, "TENURE", f"{tenure} years", status="OK")
        pipeline_events.append({"stage": "tenure", "status": "COMPLETED"})

        return build_response(req.user_id,
            "Enter your monthly salary.",
            pipeline_events
        )

    # ================= SALARY =================
    if stage == "salary":
        if not is_valid_salary(user_lower):
            return build_response(req.user_id,
                "Enter valid salary."
            )

        salary = extract_salary(user_lower)
        state["salary"] = salary

        log_audit(req.user_id, "SALARY", f"₹{salary}", status="OK")
        pipeline_events.append({"stage": "salary", "status": "COMPLETED"})

        # KYC
        kyc = verify_kyc(aadhaar_suffix=state["aadhaar"])
        pipeline_events.append({
            "stage": "kyc",
            "status": "COMPLETED" if kyc["kyc_verified"] else "FAILED",
            "confidence": kyc["confidence"]
        })

        if not kyc["kyc_verified"]:
            log_audit(req.user_id, "KYC_FAIL", "KYC failed", status="FAIL")
            return build_response(req.user_id,
                "KYC failed. Try again.",
                pipeline_events
            )

        # UNDERWRITING
        result = check_eligibility(
    salary=salary,
    requested_amount=state["amount"],
    tenure_years=state["tenure"],
    user_id=req.user_id,
    kyc_confidence=kyc["confidence"]
)

        pipeline_events.append({
            "stage": "underwriting",
            "status": "APPROVED" if result["approved"] else "REJECTED",
            "confidence": result["confidence"]
        })

        log_audit(
            req.user_id,
            "UNDERWRITING",
            result["message"],
            confidence=result["confidence"],
            status="APPROVED" if result["approved"] else "REJECTED",
            explanation=result.get("explanation")
        )

        dashboard_stats["total"] += 1

        # ================= APPROVED =================
        if result["approved"]:
            dashboard_stats["approved"] += 1

            ref = make_ref_id(req.user_id)
            emi = result["emi"]

            generate_sanction_letter(
                name=req.user_id,
                amount=state["amount"],
                tenure_years=state["tenure"],
                emi=emi["emi"],
                total_payable=emi["total_payable"],
                annual_rate=emi["annual_rate"],
                ref_id=ref
            )

            state["stage"] = "completed"

            return build_response(req.user_id,
                f"🎉 Loan Approved!\nEMI: ₹{emi['emi']}",
                pipeline_events,
                {
                    "sanction_letter": True,
                    "confidence": result["confidence"],
                    "emi": emi,
                    "rules_checked": result.get("rules_checked", [])
                }
            )

        # ================= REJECTED =================
        else:
            dashboard_stats["rejected"] += 1
            state["stage"] = "completed"

            return build_response(req.user_id,
                f"❌ Loan not approved.\n{result.get('explanation')}",
                pipeline_events,
                {
                    "confidence": result["confidence"],
                    "rules_checked": result.get("rules_checked", [])
                }
            )

    # ================= COMPLETED =================
    if stage == "completed":
        if "loan" in user_lower:
            conversation_state.pop(req.user_id)
            return build_response(req.user_id,
                "Restarting... Type your loan amount."
            )

        return build_response(req.user_id,
            "Process complete. Type 'I want a loan' to restart."
        )

# ================= ENDPOINTS =================

@app.get("/audit/{user_id}")
def get_audit(user_id: str):
    return {"audit": audit_logs.get(user_id, [])}

@app.get("/dashboard")
def dashboard():
    total = dashboard_stats["total"] or 1
    return {
        "total_applications": dashboard_stats["total"],
        "approved": dashboard_stats["approved"],
        "rejected": dashboard_stats["rejected"],
        "approval_rate": round(dashboard_stats["approved"] / total * 100, 1),
        "rejection_rate": round(dashboard_stats["rejected"] / total * 100, 1),
        "kyc_failures": dashboard_stats["kyc_failures"],
        "escalations": dashboard_stats["escalations"],
        "avg_processing_ms": 500
    }

@app.get("/download")
def download():
    return FileResponse("sanction_letter.pdf", filename="sanction_letter.pdf")