from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from agents.sales_agent import handle_sales
from agents.verification_agent import verify_kyc
from agents.underwriting_agent import check_eligibility
from agents.sanction_agent import generate_sanction_letter
from fastapi.responses import FileResponse

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
    msg = req.message.lower()
    stage = conversation_state["stage"]

    if stage in ["start", "amount"]:
        reply = handle_sales(stage)
        conversation_state["stage"] = "amount" if stage == "start" else "salary"
        return {"reply": reply}

    elif stage == "salary":
        kyc = verify_kyc()
        result = check_eligibility()

        conversation_state["stage"] = "approved" if result["approved"] else "rejected"

        return {
            "reply": f"Thanks. {kyc['message']}\n\n{result['message']}"
    }
    elif stage == "verified":
        result = check_eligibility()
        conversation_state["stage"] = "approved" if result["approved"] else "rejected"
        return {"reply": result["message"]}

    elif stage == "approved":
        file = generate_sanction_letter()
        conversation_state["stage"] = "completed"
        return {
            "reply": "🎉 Your loan is approved! Sanction letter generated successfully.",
            "sanction_letter": file
        }
    elif stage == "rejected":
        return {"reply": "You can try again with different details in future."}

    else:
        return {"reply": "Your loan details are under review ✅"}

@app.get("/download")
def download_sanction():
    return FileResponse(
        "sanction_letter.pdf",
        media_type="application/pdf",
        filename="sanction_letter.pdf"
    )