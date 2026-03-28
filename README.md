# FinSense – AI Loan Assistant

EY Techathon 2025 | Emotionally Intelligent Personal Loan Assistant

A web-based AI-powered loan assistant that simulates an end-to-end personal loan journey using multi-agent orchestration, failure recovery, audit trails, and LLM-powered empathetic responses.

---

## Features

### Frontend
- Animated landing page with scroll-triggered sections, hero chat preview, stats bar, agent pipeline visualization, team section, and CTA
- Split-panel login with form validation, password visibility toggle, error messages, loading spinner, and demo credentials
- Full-page chat UI with message bubbles, user/bot avatars, timestamps, typing indicator, quick reply chips, auto-scroll, and logout
- Collapsible audit trail sidebar with confidence score progress bars per decision
- Confidence score badges (KYC % + Underwriting %) shown on bot messages
- Escalation message styling (orange highlight) when case is sent to human officer
- Admin dashboard at `/dashboard` — approval rate, rejection rate, KYC failures, escalations, avg processing time, agent health
- Session persistence via localStorage
- Responsive design with Tailwind CSS

### Backend
- Conversational loan flow state machine: start → amount → tenure → salary → approved / recovery / escalated / completed
- KYC verification with confidence score (88–99%) and retry support
- Agent-to-agent communication: UnderwritingAgent queries VerificationAgent for KYC confidence before deciding
- Rule-based loan eligibility underwriting (salary ≥ ₹30,000 + credit score ≥ 700)
- Failure detection + auto recovery:
  - KYC failure → prompts user to retry
  - 2x KYC failure → escalates to human loan officer with reference ID
  - Salary too low → suggests max eligible amount + longer tenure
  - User can accept alternative offer to get approved for lower amount
- Confidence scores on every agent decision (KYC + underwriting)
- Full audit trail stored per user (event, detail, status, confidence, timestamp)
- Workflow monitoring dashboard endpoint (`/dashboard`)
- Autonomous demo mode (`/demo`) — runs full loan flow with no user input
- LLM-powered empathetic responses using Mistral-7B (Hugging Face) with fallback
- Auto-generated PDF sanction letter on approval
- Input validation for loan amount, tenure, and salary with numeric extraction
- REST API with CORS support via FastAPI

---

## Tech Stack

| Layer     | Technology                                          |
|-----------|-----------------------------------------------------|
| Frontend  | Next.js 16, React 19, TypeScript, Tailwind CSS      |
| Backend   | FastAPI, Python, Uvicorn                            |
| LLM       | Mistral-7B-Instruct via Hugging Face Inference API  |
| PDF       | ReportLab                                           |
| Config    | python-dotenv                                       |

---

## Project Structure

```
finsense-ai-loan-assistant/
├── backend/
│   ├── agents/
│   │   ├── verification_agent.py   # KYC check, confidence score, agent-to-agent query
│   │   ├── underwriting_agent.py   # Eligibility rules, confidence, alternative suggestions
│   │   ├── sanction_agent.py       # PDF sanction letter generator (ReportLab)
│   │   └── sales_agent.py
│   ├── logic/
│   │   ├── llm.py                  # Mistral-7B Hugging Face integration + fallback
│   │   └── validators.py           # Input validators + numeric extractors
│   └── main.py                     # FastAPI app, state machine, audit trail, dashboard, demo
└── frontend/
    ├── app/
    │   ├── landing/page.tsx         # Landing page — animated hero, features, team, CTA
    │   ├── login/page.tsx           # Login — split layout, validation, demo credentials
    │   ├── page.tsx                 # Chat UI — bubbles, audit sidebar, confidence badges
    │   ├── dashboard/page.tsx       # Admin dashboard — stats, agent health, auto demo
    │   ├── chat/page.tsx            # Redirects to /
    │   ├── globals.css              # Global styles, animations, scrollbar
    │   └── layout.tsx               # Root layout with metadata
    ├── package.json
    └── next.config.ts
```

---

## Pages & API Endpoints

### Frontend Routes

| Route        | Description                                      |
|--------------|--------------------------------------------------|
| `/landing`   | Marketing landing page                           |
| `/login`     | Authentication with validation                   |
| `/`          | AI loan assistant chat interface                 |
| `/dashboard` | Workflow monitoring admin panel                  |

### Backend Endpoints

| Method | Endpoint          | Description                                      |
|--------|-------------------|--------------------------------------------------|
| POST   | `/chat`           | Main conversation endpoint (state machine)       |
| GET    | `/audit/{user_id}`| Full audit trail for a user session              |
| GET    | `/dashboard`      | Workflow stats (approval rate, failures, etc.)   |
| POST   | `/demo`           | Autonomous demo — runs full loan flow with no user input |
| GET    | `/download`       | Download generated sanction letter PDF           |

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
  → VerificationAgent runs KYC (confidence score generated)
  → UnderwritingAgent queries VerificationAgent (agent-to-agent)
  → Underwriting checks salary + credit score

  ✅ Approved:
      → PDF sanction letter generated
      → Download link shown in chat
      → Audit trail available in sidebar

  ❌ Rejected (low salary):
      → AI suggests max eligible amount
      → User can reply "yes" to accept alternative → approved
      → Or decline → session ends

  ❌ KYC Failed:
      → User prompted to retry
      → 2nd failure → escalated to human loan officer
      → Reference ID generated
```

---

## Audit Trail Example

```
✅ SESSION_START   — User initiated loan request          [INFO]
✅ AMOUNT_CAPTURED — ₹5,00,000                           [OK]
✅ TENURE_CAPTURED — 5 years                             [OK]
✅ SALARY_CAPTURED — ₹50,000                             [OK]
✅ KYC_CHECK       — KYC verified successfully ✅         [OK]   confidence: 94%
✅ UNDERWRITING    — Eligible for loan                   [APPROVED] confidence: 91%
✅ DECISION        — Loan APPROVED ✅                     [APPROVED]
```

---

Open `http://localhost:3000/landing` in your browser. Both terminals must be running simultaneously.
