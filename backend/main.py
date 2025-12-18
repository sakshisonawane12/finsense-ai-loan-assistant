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

conversation_state = {
    "stage": "start"
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str


def is_valid_tenure(text: str) -> bool:
    digits = "".join(c for c in text if c.isdigit())
    if not digits:
        return False
    years = int(digits)
    return 1 <= years <= 30


@app.post("/chat")
def chat(req: ChatRequest):
    user_msg = req.message.lower().strip()
    stage = conversation_state["stage"]

    # 🔁 restart
    if stage == "completed" and "loan" in user_msg:
        conversation_state["stage"] = "start"
        stage = "start"

    # ================= START =================
    if stage == "start":

        if any(w in user_msg for w in ["no", "dont", "don't", "donnt", "cancel"]):
            conversation_state["stage"] = "completed"
            return {
                "reply": rewrite_with_llm(
                    "No worries 😊 I’m here whenever you need help with a personal loan.\n"
                    "Just type: I want a loan"
                )
            }

        if "loan" in user_msg:
            conversation_state["stage"] = "amount"
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
                    "That doesn’t look like a valid loan amount.\n"
                    "Please enter something like 5 lakh or 500000."
                )
            }

        conversation_state["stage"] = "tenure"
        return {
            "reply": rewrite_with_llm(
                "For how many years would you like to take this loan?"
            )
        }

    # ================= TENURE =================
    elif stage == "tenure":

        if not is_valid_tenure(user_msg):
            return {
                "reply": rewrite_with_llm(
                    "Please enter a valid loan duration in years (e.g. 5 or 10)."
                )
            }

        conversation_state["stage"] = "salary"
        return {
            "reply": rewrite_with_llm(
                "Thanks 😊 What is your monthly salary?"
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
        result = check_eligibility(salary=50000)

        conversation_state["stage"] = "approved" if result["approved"] else "rejected"

        return {
            "reply": rewrite_with_llm(
                f"Thanks 😊 {kyc['message']} {result['message']}"
            )
        }

    # ================= APPROVED =================
    elif stage == "approved":
        generate_sanction_letter()
        conversation_state["stage"] = "completed"
        return {
            "reply": rewrite_with_llm(
                "🎉 Your loan is approved! I’ve generated your sanction letter."
            ),
            "sanction_letter": True
        }

    # ================= REJECTED =================
    elif stage == "rejected":
        conversation_state["stage"] = "completed"
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
