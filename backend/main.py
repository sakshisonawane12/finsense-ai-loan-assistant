from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from dotenv import load_dotenv

from agents.verification_agent import verify_kyc
from agents.underwriting_agent import check_eligibility
from agents.sanction_agent import generate_sanction_letter
from logic.llm import rewrite_with_llm
from logic.validators import (
    is_valid_amount,
    is_valid_salary,
)

load_dotenv()

app = FastAPI()

conversation_state = {}

def get_user_state(user_id):
    if user_id not in conversation_state:
        conversation_state[user_id] = {
            "stage": "start",
            "amount": None,
            "tenure": None,
            "salary": None
        }
    return conversation_state[user_id]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    user_id: str


def is_valid_tenure(text: str) -> bool:
    digits = "".join(c for c in text if c.isdigit())
    if not digits:
        return False
    years = int(digits)
    return 1 <= years <= 30


@app.post("/chat")
def chat(req: ChatRequest):
    user_msg = req.message.lower().strip()
    state = get_user_state(req.user_id)
    stage = state["stage"]

    # 🔁 restart
    if stage == "completed" and "loan" in user_msg:
        state["stage"] = "start"
        stage = "start"

    # ================= START =================
    if stage == "start":

        if any(w in user_msg for w in ["no", "dont", "don't", "donnt", "cancel"]):
            state["stage"] = "completed"
            return {
                "reply": rewrite_with_llm(
                    "No worries 😊 I’m here whenever you need help with a personal loan.\n"
                    "Just type: I want a loan"
                )
            }

        if "loan" in user_msg:
            state["stage"] = "amount"
            return {
                "reply": rewrite_with_llm(
                    "Great 👍 How much loan amount are you looking for?"
                )
            }

        return {
            "reply": rewrite_with_llm(
                "Hi 👋 I’m FinSense 🤖 — your personal loan assistant.\n"
                "If you’d like to proceed, just type: I want a loan"
            )
        }

    # ================= AMOUNT =================
    elif stage == "amount":

        if not is_valid_amount(user_msg):
            return {
                "reply": rewrite_with_llm(
                    "Please enter a valid loan amount like 5 lakh or 500000."
                )
            }

        # Extract amount digits
        amount = int("".join(c for c in user_msg if c.isdigit()))

        state["amount"] = amount
        state["stage"] = "tenure"

        return {
            "reply": rewrite_with_llm(
                f"Got it 👍 You are looking for ₹{amount}. "
                "For how many years would you like the loan?"
            )
        }

    # ================= TENURE =================
    elif stage == "tenure":

        digits = "".join(c for c in user_msg if c.isdigit())

        if not digits:
            return {
                "reply": rewrite_with_llm(
                    "Please enter tenure in years (e.g. 5 or 10)."
                )
            }

        tenure = int(digits)

        if tenure < 1 or tenure > 30:
            return {
                "reply": rewrite_with_llm(
                    "Loan tenure should be between 1 and 30 years."
                )
            }

        state["tenure"] = tenure
        state["stage"] = "salary"

        return {
            "reply": rewrite_with_llm(
                f"Great 👍 {tenure} years selected. "
                "What is your monthly salary?"
            )
        }

    # ================= SALARY =================
    elif stage == "salary":

        if not is_valid_salary(user_msg):
            return {
                "reply": rewrite_with_llm(
                    "Please enter your monthly salary as a number (e.g. 30000)."
                )
            }

        kyc = verify_kyc()
        salary_digits = int("".join(c for c in user_msg if c.isdigit()))
        state["salary"] = salary_digits

        result = check_eligibility(salary_digits)
        state["stage"] = "approved" if result["approved"] else "rejected"

        return {
            "reply": rewrite_with_llm(
                f"Thanks 😊 {kyc['message']} {result['message']}"
            )
        }

    # ================= APPROVED =================
    elif stage == "approved":
        generate_sanction_letter()
        state["stage"] = "completed"
        return {
            "reply": rewrite_with_llm(
                "🎉 Your loan is approved! I’ve generated your sanction letter."
            ),
            "sanction_letter": True
        }

    # ================= REJECTED =================
    elif stage == "rejected":
        state["stage"] = "completed"
        return {
            "reply": rewrite_with_llm(
                "Based on the provided details, you’re not eligible right now.\n"
                "You may try again later."
            )
        }

    # ================= COMPLETED =================
    else:
        return {
            "reply": rewrite_with_llm(
                "Your loan process is completed.\n"
                "If you’d like to apply again, just type: I want a loan"
            )
        }


@app.get("/download")
def download_sanction():
    return FileResponse(
        "sanction_letter.pdf",
        media_type="application/pdf",
        filename="sanction_letter.pdf"
    )
