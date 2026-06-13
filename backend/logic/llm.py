"""
llm.py
FIXED: Fact-preserving prompt — Mistral is explicitly told to keep
all numbers, amounts, EMI values, reference IDs, and rule names intact.
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

HF_API_TOKEN = os.getenv("HF_API_TOKEN")
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
HEADERS = {"Authorization": f"Bearer {HF_API_TOKEN}"}


def generate_reply(prompt: str) -> str | None:
    try:
        resp = requests.post(
            API_URL,
            headers=HEADERS,
            json={
                "inputs": f"<s>[INST] {prompt} [/INST]",
                "parameters": {"temperature": 0.4, "max_new_tokens": 180},
            },
            timeout=4,
        )
        if resp.status_code != 200:
            return None
        result = resp.json()
        if isinstance(result, list) and "generated_text" in result[0]:
            return result[0]["generated_text"]
        return None
    except Exception:
        return None


def rewrite_with_llm(base_reply: str) -> str:
    """
    FIXED: Fact-preserving rewrite.
    Instructs the LLM to keep all numbers, ₹ amounts, percentages,
    reference IDs, and structured bullet points exactly as they are.
    Falls back to base_reply if LLM is slow, unavailable, or generic.
    """
    if not base_reply or len(base_reply.strip()) < 5:
        return base_reply

    prompt = (
        "Rewrite the following loan assistant message in a warm, empathetic, "
        "professional tone. IMPORTANT RULES:\n"
        "1. Keep ALL numbers, ₹ amounts, percentages, and EMI values EXACTLY as they are.\n"
        "2. Keep ALL reference IDs (like FSN-XXXXXX) unchanged.\n"
        "3. Keep ALL bullet points and structured data intact.\n"
        "4. Do NOT add new information or change any facts.\n"
        "5. Keep the response concise — same length as the original.\n\n"
        f"Message:\n{base_reply}"
    )

    rewritten = generate_reply(prompt)

    if not rewritten:
        return base_reply

    low = rewritten.lower()
    # Reject cold-start / generic / hallucinated responses
    bad = ["just a moment", "please wait", "loading", "getting ready",
           "i am an ai", "as an ai", "i cannot", "i'm sorry, i"]
    if any(b in low for b in bad):
        return base_reply

    # Reject if key numbers from base were dropped
    import re
    base_numbers = re.findall(r"[\d,]+", base_reply)
    for num in base_numbers[:3]:   # check first 3 numbers
        clean = num.replace(",", "")
        if len(clean) > 3 and clean not in rewritten.replace(",", ""):
            return base_reply   # number was lost — use original

    return rewritten.strip()
