# CyberSaathi AI

A cybersecurity awareness web application for college students and beginner internet users.

**Owner:** Shashwat Singh | Internship ID: IBMUEML010372  
**Institution:** ABES Engineering College, Ghaziabad  
**Program:** IBM SkillsBuild – AICTE – BharatCares Machine Learning & Applied AI Internship 2026

---

## What it does

- Analyze a suspicious URL using local string features and a trained ML baseline (no URL is opened or fetched).
- Analyze a copied message (SMS, email, internship/job offer) for scam and phishing indicators.
- Get plain English or Hinglish explanations, warning indicators, and safer next steps.
- Learn about cybersecurity threats through focused lessons and a short quiz.

**Important:** This tool cannot guarantee safety. Always verify through official channels independently.

---

## Quick start

### Requirements

| Tool | Minimum version | Check |
|------|----------------|-------|
| Python | 3.10 | `python --version` |
| Node.js | 18 | `node --version` |
| npm | 9 | `npm --version` |

---

### 1 — Backend

```bash
# From the repository root
cd backend

# Create and activate a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and edit environment configuration
cp .env.example .env
# Edit .env if needed (defaults work for local development)

# Start the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Verify at: http://localhost:8000/health → `{"status":"ok"}`

Interactive API docs: http://localhost:8000/docs

---

### 2 — Frontend

```bash
# In a separate terminal, from the repository root
cd frontend

# Install dependencies
npm install

# Copy and edit environment configuration
cp .env.example .env
# Edit VITE_API_BASE_URL if the backend is not on http://localhost:8000

# Start the development server
npm run dev
```

Open: http://localhost:5173

---

### 3 — Backend tests

```bash
cd backend
# (virtual environment must be active)
pytest
```

Expected output: all tests pass. See `backend/tests/` for test files.

---

### 4 — Frontend type-check and lint

```bash
cd frontend
npm run type-check
npm run lint
```

---

### 5 — Frontend production build

```bash
cd frontend
npm run build
# Output: frontend/dist/
```

---

## ML model (T-02 — to be completed)

The URL classification model is trained separately. To reproduce:

```bash
# 1. Place a verified, licensed dataset in ml/data/ (see ml/data/README.md)
# 2. From the repository root:
python ml/train_url_model.py
# Outputs: ml/artifacts/url_model.joblib, ml/artifacts/feature_schema.json
#          ml/reports/url_model_evaluation.json
```

Until the model artifact is built, the backend returns `"method": "unable_to_assess"`.

---

## Project structure

```
/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application factory
│   │   ├── config.py            # Settings (pydantic-settings)
│   │   ├── schemas/             # Pydantic request/response models
│   │   ├── api/routes/          # Route handlers
│   │   └── services/            # Analysis logic (stubs → real in T-02/T-03)
│   ├── tests/                   # pytest test suite
│   ├── requirements.txt
│   ├── pyproject.toml
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.tsx              # Root component (skeleton → full UI in T-04)
│   │   ├── services/api.ts      # All API calls (configurable base URL)
│   │   └── types/api.ts         # TypeScript types mirroring backend schemas
│   ├── index.html
│   ├── vite.config.ts
│   ├── package.json
│   └── .env.example
├── ml/
│   ├── data/README.md           # Dataset placement instructions
│   ├── artifacts/README.md      # Generated artifacts documentation
│   ├── reports/README.md        # Evaluation report documentation
│   └── train_url_model.py       # Training script (stub → full in T-02)
├── docs/                        # Planning documents and build instructions
├── .gitignore
└── README.md
```

---

## API contracts

### `GET /health`
```json
{"status": "ok"}
```

### `POST /api/analyze/url`
Request:
```json
{"url": "https://example.com/login", "language": "en"}
```
Response fields: `category`, `method`, `indicators`, `summary`, `recommendations`, `disclaimer`, `language`

Valid `category` values: `High Risk` | `Suspicious` | `No Obvious Warning Signs` | `Unable to Assess`  
Valid `method` values: `ml_model` | `rules` | `ml_model_and_rules` | `unable_to_assess`

### `POST /api/analyze/message`
Request:
```json
{"message": "Congratulations! You have won a scholarship.", "language": "hinglish"}
```
Same response shape as URL analysis.

Full schema details: http://localhost:8000/docs

---

## Environment variables

| Variable | Where | Default | Purpose |
|----------|-------|---------|---------|
| `CORS_ORIGINS` | `backend/.env` | `http://localhost:5173` | Comma-separated allowed frontend origins |
| `ENVIRONMENT` | `backend/.env` | `development` | Runtime environment |
| `MODEL_PATH` | `backend/.env` | (auto-resolved) | Override path to trained model artifact |
| `VITE_API_BASE_URL` | `frontend/.env` | `http://localhost:8000` | Backend base URL for API calls |

Never commit `.env` files. Never put secrets in frontend variables.

---

## Privacy and safety notices

- Submitted URLs are **never opened, fetched, or resolved**. Only the string is analyzed.
- Raw submitted URLs and messages are **not stored or logged** by default.
- Results are not a guarantee of safety. Independent verification is always necessary.
- HTTPS alone does not prove a website is trustworthy.

---

## Known limitations (T-01 state)

- URL and message analysis return `Unable to Assess` until the model (T-02) and analysis services (T-03) are implemented.
- Frontend shows a placeholder page until the UI is built in T-04.
- Message analysis will use transparent rule-based indicators (labeled as `rules`) unless a valid text dataset is separately verified and trained.

---

## Implementation status

| Task | Description | Status |
|------|-------------|--------|
| T-00 | Repository audit | ✅ Complete |
| T-01 | Project skeleton, API contracts | ✅ Complete |
| T-02 | Dataset verification, URL ML baseline | ⏳ Pending |
| T-03 | Backend analysis services and tests | ⏳ Pending |
| T-04 | Frontend UI and real API integration | ⏳ Pending |
| T-05 | Learning section and quiz | ⏳ Pending |
| T-06 | Security/privacy hardening | ⏳ Pending |
| T-07 | Deployment and reproducible docs | ⏳ Pending |
| T-08 | Final evidence and handoff | ⏳ Pending |
