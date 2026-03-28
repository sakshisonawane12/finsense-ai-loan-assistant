# FinSense – AI Loan Assistant

EY Techathon 2025 | Emotionally Intelligent Personal Loan Assistant

A web-based AI-powered loan assistant that simulates an end-to-end personal loan journey using multi-agent orchestration and LLM-powered empathetic responses.

---

## Features

### Frontend
- Animated landing page with scroll-triggered sections, hero chat preview, stats bar, agent pipeline visualization, team section, and CTA
- Split-panel login with form validation, password visibility toggle, error messages, loading spinner, and demo credentials
- Full-page chat UI with message bubbles, user/bot avatars, timestamps, typing indicator, quick reply chips, auto-scroll, and logout
- Session persistence via localStorage
- Responsive design with Tailwind CSS

### Backend
- Conversational loan flow state machine: start → amount → tenure → salary → approved/rejected → completed
- KYC verification via verification agent
- Rule-based loan eligibility underwriting (salary ≥ ₹30,000 + credit score ≥ 700)
- LLM-powered empathetic responses using Mistral-7B (Hugging Face)
- Auto-generated PDF sanction letter on approval
- Input validation for loan amount, tenure, and salary
- REST API with CORS support via FastAPI

---

## Tech Stack

| Layer     | Technology                                      |
|-----------|-------------------------------------------------|
| Frontend  | Next.js 16, React 19, TypeScript, Tailwind CSS  |
| Backend   | FastAPI, Python, Uvicorn                        |
| LLM       | Mistral-7B-Instruct via Hugging Face Inference API |
| PDF       | ReportLab                                       |
| Config    | python-dotenv                                   |

---

## Project Structure

```
finsense-ai-loan-assistant/
├── backend/
│   ├── agents/
│   │   ├── verification_agent.py   # KYC verification logic
│   │   ├── underwriting_agent.py   # Loan eligibility rules (salary + credit score)
│   │   ├── sanction_agent.py       # PDF sanction letter generator (ReportLab)
│   │   └── sales_agent.py
│   ├── logic/
│   │   ├── llm.py                  # Mistral-7B Hugging Face integration + fallback
│   │   └── validators.py           # Input validators (amount, salary, tenure)
│   ├── main.py                     # FastAPI app + conversation state machine
│   ├── .env                        # HF_API_TOKEN (not committed)
│   └── sanction_letter.pdf         # Generated on loan approval (not committed)
└── frontend/
    ├── app/
    │   ├── landing/page.tsx         # Landing page — animated hero, features, team, CTA
    │   ├── login/page.tsx           # Login — split layout, validation, demo credentials
    │   ├── page.tsx                 # Chat UI — bubbles, avatars, typing indicator, quick replies
    │   ├── chat/page.tsx            # Redirects to /
    │   ├── globals.css              # Global styles, animations, scrollbar
    │   └── layout.tsx               # Root layout with metadata
    ├── package.json
    └── next.config.ts
```

---

## Pages

| Route      | Description                              |
|------------|------------------------------------------|
| `/landing` | Marketing landing page                   |
| `/login`   | Authentication with validation           |
| `/`        | AI loan assistant chat interface         |

---

## How to Run

### Prerequisites
- Python 3.8+
- Node.js 18+

### 1. Backend

```bash
cd backend
pip install fastapi uvicorn python-dotenv pydantic reportlab requests
uvicorn main:app --reload
```

Backend runs at → `http://localhost:8000`

### 2. Frontend

Open a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at → `http://localhost:3000`

### 3. Environment

Ensure `backend/.env` contains:

```
HF_API_TOKEN=your_huggingface_token
```

---

## Demo Credentials

| Name    | Password |
|---------|----------|
| Sakshi  | pass123  |
| Srushti | pass123  |
| Sanika  | pass123  |
| Shreya  | pass123  |

Or enter any name with any password (4+ characters) to log in.

---

## Loan Flow

```
User: "I want a loan"
  → Bot asks: Loan amount?
  → Bot asks: Tenure (years)?
  → Bot asks: Monthly salary?
  → KYC verification runs
  → Underwriting engine checks eligibility
  → Approved: PDF sanction letter generated + download link shown
  → Rejected: Empathetic rejection message shown
```

---

Open `http://localhost:3000/landing` in your browser. Both terminals must be running simultaneously.
