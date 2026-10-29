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
pytest -v
```

Expected output: 150 passed. Tests cover API contracts, model reproducibility, analysis logic, security & input hardening, and realistic end-to-end smoke scenarios.

---

### 4 — Frontend type-check, lint, and quiz check

```bash
cd frontend
npm run type-check
npm run lint
npm run check-quiz
```

---

### 5 — Frontend production build

```bash
cd frontend
npm run build
# Output: frontend/dist/
```

---

## ML model (T-02 baseline)

The URL classification model uses a `RandomForestClassifier` trained on the peer-reviewed Hannousse & Yahiouche dataset (`dataset_B_05_2020.csv`), computing 53 URL-only features locally without any network requests.

- **Dataset Provenance:**
  - Source: Mendeley Data — *Web page phishing detection* (Hannousse & Yahiouche, 2020)
  - URL: `https://data.mendeley.com/datasets/c2gw7fy2j4/3`
  - License: Creative Commons Attribution 4.0 International (CC BY 4.0)
  - Total Samples: 11,430 balanced URLs (5,715 phishing, 5,715 legitimate)
  - Train/Val/Test Split: 70% train (8,000 URLs), 15% validation (1,715 URLs), 15% test (1,715 URLs)
  - Leakage Prevention: Deterministic split with fixed random seed (42) applied before model fitting.
- **Artifacts:** `ml/artifacts/url_model.joblib` (22.3 MB), `ml/artifacts/feature_schema.json` (53 features, v1.0.0)
- **Measured Evaluation Metrics (held-out test set of 1,715 samples):**
  - **Accuracy:** 90.09% (0.90087)
  - **Phishing Precision:** 89.26% (0.89257)
  - **Phishing Recall:** 91.13% (0.91132)
  - **Phishing F1-Score:** 90.18% (0.90185)
  - **Macro Average F1:** 90.09% (0.90086)
  - **Confusion Matrix:**
    - True Negatives (Legitimate classified as legitimate): 764
    - False Positives (Legitimate flagged as phishing): 94 (FPR: 10.96%)
    - False Negatives (Phishing missed as legitimate): 76 (FNR: 8.87%)
    - True Positives (Phishing correctly caught): 781
- **Reproducible training command:**
  ```bash
  # Ensure Python virtual environment with requirements.txt is active
  python ml/train_url_model.py
  ```
- If the artifact is unavailable, the backend gracefully falls back to deterministic rule checks with explicit `"method": "rules"` disclosure. No fake predictions or mock results are ever returned.

---

## Project structure

```
/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app factory, CORS, security headers & error handlers
│   │   ├── config.py            # Settings (pydantic-settings, CORS, input limits)
│   │   ├── schemas/             # Pydantic request/response models & validation
│   │   ├── api/routes/          # /health, /api/analyze/url, /api/analyze/message
│   │   └── services/            # URL ML+rule analysis & message rule-based analysis
│   ├── tests/                   # pytest test suite (150 tests covering contracts, ML, security, e2e)
│   ├── requirements.txt
│   ├── pyproject.toml
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.tsx              # Root component with tabs, mode selection, language toggle
│   │   ├── components/          # AnalysisForm, ResultCard, LearnSection, QuizSection, UI
│   │   ├── data/                # Locally bundled lessons (7) and quiz questions (13)
│   │   ├── services/api.ts      # Backend API integration (configurable base URL)
│   │   └── types/api.ts         # TypeScript interfaces matching backend schemas
│   ├── index.html
│   ├── vite.config.ts
│   ├── package.json
│   └── .env.example
├── ml/
│   ├── data/README.md           # Dataset placement instructions
│   ├── artifacts/               # Trained url_model.joblib and feature_schema.json
│   ├── reports/                 # Measured evaluation reports
│   ├── url_features.py          # 53 deterministic URL feature extractors (no network)
│   └── train_url_model.py       # Reproducible training pipeline
├── docs/                        # Planning documents, guides, and prompts
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
Same response shape as URL analysis. Method is always `rules` (transparently disclosed).

Full schema details: http://localhost:8000/docs

---

## Environment variables

| Variable | Where | Default | Purpose |
|----------|-------|---------|---------|
| `CORS_ORIGINS` | `backend/.env` | `http://localhost:5173,http://127.0.0.1:5173,...` | Comma-separated allowed frontend origins |
| `ENVIRONMENT` | `backend/.env` | `development` | Runtime environment |
| `MODEL_PATH` | `backend/.env` | `ml/artifacts/url_model.joblib` | Override path to trained model artifact |
| `VITE_API_BASE_URL` | `frontend/.env` | `http://localhost:8000` | Backend base URL for API calls |

Never commit `.env` files. Never put secrets in frontend variables.

---

## Privacy and security architecture (T-06 verified)

- **Submitted URLs are NEVER opened, fetched, crawled, or resolved.** URL analysis uses string parsing and local feature extraction only. No HTTP requests, sockets, or DNS lookups are made to submitted targets.
- **Raw user submissions are NEVER persisted or logged.** User URLs and message texts are not written to databases, files, or server log files.
- **No sensitive input reflection in errors.** Validation exception handlers strip user inputs from HTTP 422 error payloads, ensuring tokens, passwords, and sensitive text are never reflected.
- **HTML / Script injection prevented.** Responses contain structured text without reflected markup. Frontend renders all dynamic values via safe React text nodes; no `dangerouslySetInnerHTML` is used.
- **Strict CORS policy.** Configurable via `CORS_ORIGINS`; wildcards with credentials are not permitted. Preflight OPTIONS requests from unauthorized origins receive no CORS approval.
- **HTTP security headers.** Every response includes `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, and `Referrer-Policy: no-referrer`.
- **Stack trace & secret protection.** Generic 500 error responses prevent leaking internal exception traces, environment variables, or server paths.
- **No third-party threat intelligence or LLM API calls.** Analysis runs completely offline and deterministically without external API dependencies.

---

## Known limitations & known issues

- **Static structural analysis only:** URL classification relies on structural and lexical patterns (53 features) and deterministic rule heuristics. Because pages are never fetched (to protect user privacy and safety), it cannot detect malicious payload content inside compromised legitimate web pages.
- **URL shortening services:** Link shorteners (e.g., bit.ly, tinyurl.com) conceal real destinations. CyberSaathi flags them as suspicious by rule because expanding the shortener would require resolving or visiting the redirect target.
- **Message analysis is rule-based:** Message classification relies on pattern matching for common phishing tropes (OTPs, upfront fees, urgency, lottery claims, KYC threats). It is explicitly labeled as `rules` and does not use an NLP or generative LLM model.
- **Probabilistic results:** Automated analysis can produce false positives and false negatives. A "No Obvious Warning Signs" verdict is **not** a guarantee of safety. Independent verification via official channels is always required.
- **Language support:** Explanations and educational advice are available in English and Hinglish. The underlying ML URL classifier evaluates language-agnostic URL structural features.

---

## Deployment & Hosting Configuration (T-07)

### Recommended hosting approach
The simplest and most reliable free-tier arrangement for CyberSaathi is:
- **Backend:** [Render](https://render.com) Web Service (Free Tier: 512 MB RAM, Python 3.12, custom domain/SSL, custom health check).
- **Frontend:** [Render](https://render.com) Static Site or [Vercel](https://vercel.com) (Free Tier: unlimited bandwidth, global edge CDN, automatic SPA rewrites via `_redirects` / `vercel.json`).
- **Infrastructure-as-Code:** Provided via [`render.yaml`](file:///D:/CyberSaathi/render.yaml) at the repository root.

### Specification & Verified Parameters

| Parameter | Backend Service | Frontend Static Site |
|---|---|---|
| **Platform** | Render Web Service (Free Tier) | Render Static Site or Vercel (Free Tier) |
| **Root Directory** | `backend` | `frontend` |
| **Runtime** | Python 3.10+ (tested on 3.12.10) | Node.js 18+ (tested on Vite 5 / Node 20) |
| **Build Command** | `pip install --upgrade pip && pip install -r requirements.txt` | `npm install && npm run build` |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` | N/A (Static file serving from CDN) |
| **Publish Directory** | N/A | `dist` |
| **Health Check Path** | `GET /health` (`200 OK`, `{"status": "ok"}`) | `GET /` (`200 OK`) |
| **Environment Variables** | `ENVIRONMENT=production`<br>`CORS_ORIGINS=https://<your-frontend>.onrender.com` | `VITE_API_BASE_URL=https://<your-backend>.onrender.com` |
| **Model Artifact Size** | `ml/artifacts/url_model.joblib`: 22.3 MB (~140 MB RAM in memory) | `dist/`: ~225 KB total assets |
| **CORS Policy** | Whitelist via `CORS_ORIGINS`; wildcards disallowed | Browser origin sent in headers |
| **Secrets Exposure** | Zero secrets required; no LLM API keys | Zero private variables bundled |

### Deployment status and blocker documentation
- **Deployment Status:** Configuration verified; local end-to-end runtime 100% passing.
- **Exact Blocker:** Live cloud deployment requires a user-owned account (on Render or Vercel), personal login authentication, and linking the user's GitHub repository, as explicitly specified in [`docs/manual_actions.md`](file:///D:/CyberSaathi/docs/manual_actions.md) (M-05).
- **Zero-Secret Policy:** In accordance with project security invariants, Antigravity does not request, store, or embed third-party API tokens, cloud passwords, or private SSH keys into source code or environment files.
- **Live Verification Requirement:** Under project rules, a live deployment URL is never claimed until the URL is tested end-to-end in a real browser.

### Steps for user to deploy live (M-05 Action Guide)

When you are ready to publish CyberSaathi to live cloud hosting:

1. **Push your code to GitHub:**
   ```bash
   git push origin master
   ```
2. **Deploy Backend on Render:**
   - Sign in to [dashboard.render.com](https://dashboard.render.com).
   - Click **New +** → **Web Service** → Connect your GitHub repository (`CyberSaathi`).
   - Settings:
     - **Name:** `cybersaathi-backend`
     - **Root Directory:** `backend`
     - **Runtime:** `Python 3`
     - **Build Command:** `pip install --upgrade pip && pip install -r requirements.txt`
     - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
     - **Plan:** Free
   - In **Advanced** → **Environment Variables**:
     - `PYTHON_VERSION` = `3.12.2`
     - `ENVIRONMENT` = `production`
     - `CORS_ORIGINS` = `https://cybersaathi-frontend.onrender.com` (or your chosen frontend URL)
   - In **Health Check Path**, enter: `/health`
   - Click **Create Web Service**. Wait for deployment. Your backend URL will be `https://cybersaathi-backend.onrender.com`.
3. **Deploy Frontend on Render (or Vercel):**
   - Click **New +** → **Static Site** → Connect the same repository.
   - Settings:
     - **Name:** `cybersaathi-frontend`
     - **Root Directory:** `frontend`
     - **Build Command:** `npm install && npm run build`
     - **Publish Directory:** `dist`
   - In **Environment Variables**:
     - `VITE_API_BASE_URL` = `https://cybersaathi-backend.onrender.com` (use your actual backend URL from step 2)
   - Click **Create Static Site**.
4. **Update CORS:**
   - Go back to your Backend Web Service settings on Render.
   - Update `CORS_ORIGINS` to match your actual frontend URL (e.g., `https://cybersaathi-frontend.onrender.com`).
5. **Verify End-to-End:**
   - Open your frontend URL in a browser.
   - Test a URL analysis (e.g. `https://example.com`), a message analysis, the Hinglish toggle, and the quiz.
   - Check browser DevTools network tab to ensure requests to `/api/analyze/url` return `200 OK`.

---

## Implementation status

| Task | Description | Status |
|------|-------------|--------|
| T-00 | Repository audit | ✅ Complete |
| T-01 | Project skeleton, API contracts | ✅ Complete |
| T-02 | Dataset verification, URL ML baseline | ✅ Complete |
| T-03 | Backend analysis services and tests | ✅ Complete |
| T-04 | Frontend UI and real API integration | ✅ Complete |
| T-05 | Learning section and quiz | ✅ Complete |
| T-06 | Security/privacy hardening & quality review | ✅ Complete |
| T-07 | Deployment and reproducible docs | ✅ Complete (Configuration verified; live deploy held pending M-05 manual action) |
| T-08 | Final evidence and handoff | ⏳ Pending |
