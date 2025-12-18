# AI Log Analyzer

AI Log Analyzer grew out of a simple goal for this hackathon: take the mountain of application logs we stare at every day, and turn them into something the whole team can consume in minutes. Upload a log, and you immediately see what broke, when it broke, and you can even interrogate the data through a chat assistant that refuses to hallucinate. Everything runs locally with familiar tools (FastAPI, Vite, FAISS, Gemini) so juries can reproduce the demo with almost no setup.

---

## Why We Built It

- **Upload once, learn a lot:** The same file powers dashboards, summaries, and conversational search.
- **Timeline stays readable:** We bucket events by the actual span (minutes, hours, days) so charts never devolve into noise.
- **Chats stay grounded:** The LLM only answers with the log snippets we hand it, including natural language date tags.
- **Demo-ready:** Need data? `generate_logs.py` produces a realistic, two-week log in seconds.

---

## Architecture Overview

```
React Dashboard  ───▶  FastAPI Backend  ───▶  FAISS + Sentence-BERT
        ▲                  │                     │
        │                  └── Gemini answers ◀──┘
        └────── REST (upload/summary/query)
```

**What lives where?**

- **Frontend/Vite:** DashboardView, SummaryView, ChatView, Recharts visualizations, lucide-react icons, Axios service calls.
- **Backend/FastAPI:** `/upload`, `/summary`, `/query` routes, FAISS index management, sentence-transformers embeddings, Google Generative AI calls.
- **RAG glue:** 5-line chunks with overlap, `all-MiniLM-L6-v2` embeddings, keyword fallback, natural-language `DateText` annotation, and “last 24 hours” parsing.
- **Utilities:** `generate_logs.py` for synthetic demos, `check_models.py` to verify Gemini API access.

---

## Project Layout

```
backend/              FastAPI app, services/
frontend/             React + Vite client
generate_logs.py      1.5k-line, two-week log generator
sample_logs.log       Default demo file
check_models.py       Quick Gemini model list tool
```

---

## Running the Project

### Requirements
- Python 3.10+ (3.11 preferred)
- Node.js 18+
- A Google Generative AI key (`GOOGLE_API_KEY`) with access to the `gemini-2.5-flash` model

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

export GOOGLE_API_KEY="your-key"   # or put it in backend/.env
uvicorn main:app --reload
```
Example `.env` snippet:
```
GOOGLE_API_KEY=AIza...yourKey
GEMINI_MODEL=gemini-2.5-flash
```
The code already defaults to `gemini-2.5-flash`, so make sure your key has access to that exact model name.

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Visit the Vite URL (defaults to `http://localhost:5173`) to reach the UI.

### Optional: Generate a Demo Log
```bash
python generate_logs.py
```
This rewrites `sample_logs.log` with 1,500 entries evenly spaced across the last two weeks, so every run starts with the same data story.

---

## Product Walkthrough

1. **Upload a log** from the sidebar. Backend chunks the file, embeds it, pushes vectors into FAISS, and calculates stats.
2. **Dashboard View** shows severity totals, the adaptive timeline, and categorized error counts.
3. **Summary View** hits `/summary`, asking Gemini to describe top incidents plus recommended actions.
4. **Chat View** sends queries to `/query`. Backend finds relevant chunks (keyword + semantic), shares them with Gemini, and returns the answer alongside the referenced snippets.

Each Gemini response is attached to the logs it used, so juries can verify every claim on the spot.

---

## API Cheat Sheet

| Method | Endpoint  | What it does | Notes |
|--------|-----------|--------------|-------|
| POST   | `/upload` | Accepts `sample_logs.log` or any text log | Returns severity stats, time-series data, and initializes FAISS |
| GET    | `/summary`| LLM-generated executive summary | Only works after an upload |
| POST   | `/query`  | Chat about the ingested logs | Body `{ "query": "..." }`, response includes `answer`, `suggested_followup`, `relevant_logs` |

FastAPI exposes clear error messages, and the frontend surfaces them in the sidebar status area.

---

## What’s Under the Hood

- **Adaptive timeline buckets:** `_choose_bucket_size` detects the overall span and uses minute/hour/day bins accordingly.
- **Date tagging for natural queries:** `_augment_line_with_human_date` adds `DateText: December 12, 2025...` so human phrasing aligns with FAISS vectors.
- **Semantic + keyword fallback:** `_keyword_chunk_search` normalizes queries (drops ordinals, handles “last 24 hours”) and runs a quick scan before falling back to FAISS.
- **Guardrails for Gemini:** Prompts stress that answers must cite provided snippets; the frontend shows those snippets so judges can trace the logic.
- **Developer tooling:** `generate_logs.py` guarantees reproducible demos; `check_models.py` confirms the Gemini account before the pitch.

---

## 5-Minute Demo Plan

1. (Optional) Regenerate the sample log.
2. Start backend + frontend, upload the log.
3. Walk the dashboard: severity donut, timeline (mention adaptive buckets), and error categories.
4. Show the Summary View’s incidents/actions.
5. Ask the chat:
   - “What was the most common error on December 12th?”
   - “List the errors from the last 24 hours.”
   - “Any DB connection timeouts?”
6. Point out that every answer cites the exact log fragment that backs it up.

---

## Roadmap Ideas

- Keep multiple uploads around so users can compare releases.
- Add auth so production logs/API keys stay safe.
- Turn recurring chat questions into saved monitors.
- Package everything for the cloud (Docker + IaC).
- Track LLM response quality for continuous improvement.

---

## Final Notes

This repo is intentionally self-contained for the hackathon. Feel free to fork it, tighten up auth, or swap in another model. Just remember to hide your Google API key before pushing anything public.

Have fun exploring the logs—we certainly did. Good luck to every team on stage!
