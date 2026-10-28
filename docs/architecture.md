# CyberSaathi AI — Architecture and Workflow

## 1. Architectural principles
- Local-first, no mandatory paid APIs.
- Separate UI, API, analysis logic, model artifacts, and education content.
- Treat all user-submitted content as untrusted.
- Submitted URLs are analyzed as strings only. Never request, preview, resolve, or open them.
- Clearly distinguish ML prediction from deterministic rule indicators and any future external reputation service.
- No database or raw-submission storage is needed for the MVP.

## 2. Logical architecture

```text
┌────────────────────────────────────────────┐
│ Browser: React + TypeScript + Vite         │
│                                            │
│ URL / Message mode                         │
│ Input validation + loading/error states    │
│ Results + English/Hinglish explanations    │
│ Learning lessons + Quiz                    │
└─────────────────────┬──────────────────────┘
                      │ JSON over HTTPS (deployment)
                      │ local HTTP in development
┌─────────────────────▼──────────────────────┐
│ FastAPI backend                            │
│                                            │
│ Pydantic request validation                │
│ CORS + input-size limits                   │
│ /health                                    │
│ /api/analyze/url                           │
│ /api/analyze/message                       │
└──────────────┬─────────────────┬───────────┘
               │                 │
┌──────────────▼─────────┐ ┌─────▼─────────────────┐
│ URL analysis service   │ │ Message analysis      │
│                        │ │ service               │
│ Local URL parsing      │ │ Safe text handling    │
│ Feature extraction     │ │ Transparent rules     │
│ Trained model if valid │ │ Trained model only if │
│ artifact available     │ │ data/evaluation exist │
└──────────────┬─────────┘ └─────┬─────────────────┘
               │                 │
               └────────┬────────┘
                        ▼
             Structured result builder
             - cautious risk category
             - method/source disclosure
             - indicators and explanations
             - next steps
             - limitations
```

## 3. Proposed repository layout
Adapt this to the actual repository instead of replacing an existing good structure blindly.

```text
/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/ or app/
│   │   ├── services/api.ts
│   │   ├── data/education.ts
│   │   └── types/
│   ├── public/
│   ├── package.json
│   └── .env.example
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/routes/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── ml/
│   │   └── config.py
│   ├── tests/
│   ├── requirements.txt or pyproject.toml
│   └── .env.example
├── ml/
│   ├── data/README.md
│   ├── train_url_model.py
│   ├── evaluate_url_model.py
│   ├── artifacts/ (generated, not necessarily committed)
│   └── reports/ (actual evaluation output)
├── docs/
│   ├── architecture.md
│   ├── model_guide.md
│   └── deployment_guide.md
├── screenshots/
├── .gitignore
├── README.md
└── design.md (provided separately)
```

## 4. API contracts

### `GET /health`
Purpose: report service health without revealing secrets or local paths.
Example response:
```json
{"status":"ok"}
```

### `POST /api/analyze/url`
Request:
```json
{"url":"https://example.invalid/login","language":"en"}
```
`language` may be `en` or `hinglish`. The example URL is illustrative and must not be opened.

Response shape (values are illustrative schema only, not predictions):
```json
{
  "category":"Unable to Assess",
  "method":"ml_model",
  "indicators":[
    {"code":"example_indicator","label":"Example indicator","explanation":"Illustrative explanation"}
  ],
  "summary":"Illustrative result text",
  "recommendations":["Verify the organization through an independently found official channel."],
  "disclaimer":"This assessment can be wrong and does not guarantee safety."
}
```

Possible `method` values should be explicit and limited to those actually implemented, for example `ml_model`, `rules`, or `ml_model_and_rules`. If no valid model is available, return `rules` or `unable_to_assess`, not `ml_model`.

### `POST /api/analyze/message`
Request:
```json
{"message":"Example message text","language":"hinglish"}
```
Response should use the same general shape, and disclose whether the result came from an evaluated model, rules, or both.

## 5. End-to-end workflows

### URL workflow
1. User selects URL analysis.
2. Frontend validates that input is present and within limits.
3. Frontend sends the string to backend.
4. Backend validates the request schema and parses the URL locally.
5. URL feature extractor generates exactly the features expected by the model.
6. Trained model predicts if a valid model artifact exists; otherwise a disclosed fallback is used.
7. Result builder adds transparent indicators, category, safe next steps, language-specific explanation, and disclaimer.
8. Frontend renders results and method/source.
9. Input is not stored, logged, or opened.

### Message workflow
1. User selects message analysis.
2. Frontend validates length and sends the text.
3. Backend validates and analyzes text.
4. If an evaluated text model exists, use it; otherwise apply clearly labeled deterministic rules.
5. Return indicators such as urgency, upfront payment, credentials/OTP requests, suspicious links, or impersonation cues where actually detected.
6. Display explanation, safe next steps, and limitations.
7. Do not store/log the raw message.

### Learning/quiz workflow
1. User opens a lesson.
2. Frontend renders locally bundled content.
3. Quiz responses are evaluated locally.
4. Feedback explains the answer. No personal profile or progress database is required.

## 6. Result semantics
- `High Risk`: multiple or strong indicators according to the implemented method; not a legal/forensic conclusion.
- `Suspicious`: indicators warrant caution or independent verification.
- `No Obvious Warning Signs`: the implemented checks did not identify notable indicators; not a safety guarantee.
- `Unable to Assess`: invalid/unsupported input, model unavailable, or insufficient evidence.

The exact mapping from model scores to categories must be documented and justified. Do not invent thresholds without validation. If probabilities are not calibrated, avoid calling them confidence.

## 7. Model pipeline
1. Dataset source and license review.
2. Data inspection and label mapping.
3. Duplicate/leakage checks.
4. Train/validation/test split.
5. Training-only preprocessing fit.
6. Baseline training with fixed seed.
7. Held-out evaluation.
8. Save model artifact and feature schema/version.
9. Add model-loading and prediction tests.
10. Document limitations and reproducibility commands.

For message classification, do not claim a trained model unless the equivalent process is completed.

## 8. Security and privacy boundaries
- No outbound network calls to user-submitted URLs.
- No DNS resolution of submitted hostnames.
- No HTML rendering of raw user input.
- Request size and text length limits.
- No raw input in logs, traces, analytics, or persisted storage by default.
- Keep CORS restricted to configured frontend origins.
- No secrets in frontend code or Git.
- Do not rely on client-side validation alone.
- No claim that HTTPS, a clean result, or a model score guarantees safety.

## 9. Deployment architecture
- Frontend hosted as a static build where suitable.
- FastAPI hosted on a Python-compatible service.
- Configure frontend API base URL and backend CORS explicitly.
- Confirm model artifact size and runtime dependencies against host limits.
- Verify health and both analysis routes from the deployed frontend.
- If free hosting is unsuitable, document a reliable local run path rather than claiming a working deployment.
