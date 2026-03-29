from dotenv import load_dotenv
load_dotenv()

import os
import requests

HF_API_TOKEN = os.getenv("HF_API_TOKEN")

API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"

headers = {
    "Authorization": f"Bearer {HF_API_TOKEN}"
}


# ================= CORE LLM =================

def generate_reply(prompt: str):
    """
    Calls HuggingFace API with timeout + safe fallback
    """

    payload = {
        "inputs": f"<s>[INST] {prompt} [/INST]",
        "parameters": {
            "temperature": 0.7,
            "max_new_tokens": 150,
        }
    }

    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json=payload,
            timeout=3  # 🔥 prevents hanging
        )

        if response.status_code != 200:
            return None

        result = response.json()

        # Normal HF response
        if isinstance(result, list) and "generated_text" in result[0]:
            return result[0]["generated_text"]

        # HF loading / error
        if isinstance(result, dict) and "error" in result:
            return None

        return None

    except Exception:
        return None


# ================= HYBRID REWRITE =================

def rewrite_with_llm(base_reply: str):
    """
    Hybrid:
    - Try LLM rewrite
    - If slow / generic → fallback immediately
    """

    # 🔒 safety: avoid useless calls
    if not base_reply or len(base_reply.strip()) < 5:
        return base_reply

    try:
        prompt = (
            "Rewrite the following message in a polite, empathetic, "
            "professional tone suitable for a loan assistant:\n\n"
            f"{base_reply}"
        )

        rewritten = generate_reply(prompt)

        # ❌ fallback conditions
        if not rewritten:
            return base_reply

        lower = rewritten.lower()

        if (
            "just a moment" in lower
            or "please wait" in lower
            or "loading" in lower
            or "getting ready" in lower
        ):
            return base_reply

        return rewritten.strip()

    except Exception:
        return base_reply