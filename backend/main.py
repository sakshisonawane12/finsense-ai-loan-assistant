from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import re

from agents.verification_agent import verify_kyc
from agents.underwriting_agent import check_eligibility
from agents.sanction_agent import generate_sanction_letter
from logic.llm import rewrite_with_llm

load_dotenv()

app = FastAPI()

# ✅ Multi-user state
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

# ✅ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Request model
class ChatRequest(BaseModel):
    message: str
    user_id: str

# ================= UTIL FUNCTIONS =================

def extract_amount(text):
    text = text.lower()
    digits = re.findall(r'\d+', text)

    if not digits:
        return None

    num = int(digits[0])

    if "lakh" in text:
        return num * 100000
    elif "k" in text:
        return num * 1000
    else:
        return num


def extract_tenure(text):
    digits = re.findall(r'\d+', text)
    if not digits:
        return None
    years = int(digits[0])
    if 1 <= years <= 30:
        return years
    return None


def extract_salary(text):
    digits = re.findall(r'\d+', text)
    if not digits:
        return None
    return int(digits[0])

# ================= CHAT API =================

@app.post("/chat")
def chat(req: ChatRequest):
    user_msg = req.message.lower().strip()
    state = get_user_state(req.user_id)
    stage = state["stage"]

    print("STATE:", state)

    # 🔁 Restart flow anytime
    if "loan" in user_msg:
        state.update({
            "stage": "amount",
            "amount": None,
            "tenure": None,
            "salary": None
        })
        return {
            "reply": rewrite_with_llm(
                "Great 👍 How much loan amount are you looking for?"
            )
        }

    try:
        # ================= AMOUNT =================
        if stage == "amount":

            amount = extract_amount(user_msg)
            print("EXTRACTED AMOUNT:", amount)

            if not amount:
                return {
                    "reply": rewrite_with_llm(
                        "Please enter a valid loan amount like 5 lakh or 500000."
                    )
                }

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

            tenure = extract_tenure(user_msg)

            if not tenure:
                return {
                    "reply": rewrite_with_llm(
                        "Please enter a valid tenure between 1 and 30 years."
                    )
                }

            state["tenure"] = tenure
            state["stage"] = "salary"

            return {
                "reply": rewrite_with_llm(
                    f"Great 👍 {tenure} years selected. What is your monthly salary?"
                )
            }

        # ================= SALARY =================
        elif stage == "salary":

            salary = extract_salary(user_msg)

            if not salary or salary < 10000:
                return {
                    "reply": rewrite_with_llm(
                        "Please enter a valid monthly salary (e.g. 30000)."
                    )
                }

            state["salary"] = salary

            # ✅ Run agents
            kyc = verify_kyc()
            result = check_eligibility(
                salary=state["salary"],
                amount=state["amount"],
                tenure=state["tenure"]
            )

            state["stage"] = "approved" if result["approved"] else "rejected"

            return {
                "reply": rewrite_with_llm(
                    f"{kyc['message']} {result['message']}"
                )
            }

        # ================= APPROVED =================
        elif stage == "approved":

            generate_sanction_letter(
                name=req.user_id,
                amount=state["amount"]
            )

            state["stage"] = "completed"

            return {
                "reply": rewrite_with_llm(
                    f"🎉 Your loan of ₹{state['amount']} is approved! "
                    "Your sanction letter is ready."
                ),
                "sanction_letter": True
            }

        # ================= REJECTED =================
        elif stage == "rejected":

            state["stage"] = "completed"

            return {
                "reply": rewrite_with_llm(
                    "Sorry 😔 You are not eligible based on current details. "
                    "You may try again with different inputs."
                )
            }

        # ================= DEFAULT =================
        else:
            return {
                "reply": rewrite_with_llm(
                    "Hi 👋 I’m FinSense 🤖. Type 'I want a loan' to begin."
                )
            }

    except Exception as e:
        print("ERROR:", e)
        return {
            "reply": "Something went wrong. Please try again."
        }


# ================= DOWNLOAD =================

@app.get("/download")
def download_sanction():
    return FileResponse(
        "sanction_letter.pdf",
        media_type="application/pdf",
        filename="sanction_letter.pdf"
    )