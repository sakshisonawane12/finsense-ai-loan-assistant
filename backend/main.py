from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from agents.sales_agent import handle_sales
from agents.verification_agent import verify_kyc
from agents.underwriting_agent import check_eligibility
from agents.sanction_agent import generate_sanction_letter
from fastapi.responses import FileResponse
from dotenv import load_dotenv
load_dotenv()
from logic.llm import rewrite_with_llm
from logic.validators import is_valid_amount, is_valid_salary

app = FastAPI()
conversation_state = {
    "stage": "start"
}
# allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
@app.post("/chat")
def chat(req: ChatRequest):
    user_msg = req.message.lower()
    stage = conversation_state["stage"]

    # 🔁 RESET FLOW IF USER WANTS NEW LOAN
    if "loan" in user_msg and stage == "completed":
        conversation_state["stage"] = "start"
        stage = "start"

    # 🟢 START
    if stage == "start":
        conversation_state["stage"] = "amount"
        return {
            "reply": rewrite_with_llm(
                "Sure 👍 I can help you with a personal loan. "
                "How much amount are you looking for?"
            )
        }

    # 💰 AMOUNT
    elif stage == "amount":
        if not is_valid_amount(req.message):
            return {
                "reply": rewrite_with_llm(
                    "That doesn’t look like a valid loan amount. "
                    "Please enter an amount like '5 lakh' or '500000'."
                )
            }

        conversation_state["stage"] = "salary"
        return {"reply": rewrite_with_llm("Got it. What is your monthly salary?")}

    # 💵 SALARY
    elif stage == "salary":
        if not is_valid_salary(req.message):
            return {
                "reply": rewrite_with_llm(
                    "That doesn’t look like a valid salary. "
                    "Please enter your monthly salary as a number (e.g. 30000)."
                )
            }

        kyc = verify_kyc()
        result = check_eligibility(salary=50000)  # demo value

        conversation_state["stage"] = "approved" if result["approved"] else "rejected"

        base_reply = f"Thanks. {kyc['message']} {result['message']}"
        return {"reply": rewrite_with_llm(base_reply)}

    # ✅ APPROVED
    elif stage == "approved":
        file = generate_sanction_letter()
        conversation_state["stage"] = "completed"
        return {
            "reply": rewrite_with_llm(
                "🎉 Your loan is approved! I’ve generated your sanction letter."
            ),
            "sanction_letter": file
        }

    # ❌ REJECTED
    elif stage == "rejected":
        conversation_state["stage"] = "completed"
        return {
            "reply": rewrite_with_llm(
                "Unfortunately, you are not eligible at the moment. "
                "You may try again with different details."
            )
        }

    # 🧊 COMPLETED / IDLE
    else:
        return {
            "reply": rewrite_with_llm(
                "Your loan process is completed. "
                "If you want to apply again, please type 'I want a loan'."
            )
        }


@app.get("/download")
def download_sanction():
    return FileResponse(
        "sanction_letter.pdf",
        media_type="application/pdf",
        filename="sanction_letter.pdf"
    )