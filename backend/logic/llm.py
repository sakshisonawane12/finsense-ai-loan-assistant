from dotenv import load_dotenv
load_dotenv()
import os
import requests

HF_API_TOKEN = os.getenv("HF_API_TOKEN")
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"

headers = {
    "Authorization": f"Bearer {HF_API_TOKEN}"
}
def generate_reply(prompt: str):
    payload = {
        "inputs": f"<s>[INST] {prompt} [/INST]",
        "parameters": {
            "temperature": 0.7,
            "max_new_tokens": 150,
        }
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    result = response.json()

    # Normal HF response
    if isinstance(result, list) and "generated_text" in result[0]:
        return result[0]["generated_text"]

    # Sometimes HF returns dict with error / loading
    if isinstance(result, dict) and "error" in result:
        return "Just a moment please, I’m getting ready to help you 😊"

    return "I’m here to help you with your loan 😊"

def rewrite_with_llm(base_reply: str):
    """
    Hybrid mode:
    - Try HF to improve tone
    - If HF is cold / slow / generic → fallback immediately
    """
    try:
        prompt = (
            "Rewrite the following message in a polite, empathetic, "
            "professional tone suitable for a loan assistant:\n\n"
            f"{base_reply}"
        )

        rewritten = generate_reply(prompt)

        # ❌ HF cold-start / generic replies → ignore
        if rewritten is None:
            return base_reply

        lower = rewritten.lower()
        if (
            "getting ready" in lower
            or "just a moment" in lower
            or "please wait" in lower
        ):
            return base_reply

        return rewritten

    except Exception:
        return base_reply
