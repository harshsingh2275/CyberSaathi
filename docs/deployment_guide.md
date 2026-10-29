# CyberSaathi AI — Deployment Guide

## Purpose
Use this guide only after the application works locally and its tests pass. Hosting platforms and free-tier policies can change; verify current limits on the provider's official documentation before deployment. Do not claim deployment succeeded until the public app has been tested end to end.

## 1. Pre-deployment checklist
- [x] Backend tests pass (150/150 passed in pytest).
- [x] Frontend production build passes (Vite build, TypeScript type-check, ESLint, quiz consistency check).
- [x] URL and message analysis work locally.
- [x] No submitted URL is fetched, opened, previewed, or resolved.
- [x] Raw user submissions are not logged or persisted by default.
- [x] Model artifact is present at the expected runtime path (`ml/artifacts/url_model.joblib`, 22.3 MB) and falls back to deterministic rules if missing.
- [x] Dataset/model licensing (Mendeley Hannousse & Yahiouche 2020, CC BY 4.0) and actual metrics (90.09% test accuracy) are documented.
- [x] `.env` and credentials are excluded from Git.
- [x] Backend errors do not reveal secrets or filesystem paths (generic 500 handler, sanitized 422 errors).
- [x] Frontend API base URL is configurable via `VITE_API_BASE_URL`.
- [x] CORS allows only the intended deployed frontend origin(s) via `CORS_ORIGINS`.

## 2. Decide deployment shape
Recommended simple arrangement:
- **Frontend:** static hosting for the Vite production build.
- **Backend:** Python/FastAPI-capable hosting.
- **Model artifacts:** include only if permitted and within provider size limits; otherwise use a documented build/download mechanism that does not require committing private credentials.
- **Database:** not required for MVP.
- **External API key:** not required for core analysis.

Before choosing providers, verify:
- Python runtime and start-command support.
- Whether free services sleep or have cold starts.
- Build/runtime limits and disk persistence behavior.
- Maximum repository/artifact size.
- Outbound network policy.
- Whether a payment method is required.
- Current free-tier conditions.

## 3. Backend configuration
Configure provider environment variables using its secret/configuration UI, not source code. Names should match the actual application settings. Example names only:
- `ENVIRONMENT=production`
- `CORS_ORIGINS=https://your-actual-frontend-host.example`
- `MODEL_PATH` only if the app supports/configures it.

Do not copy these example values literally. Use the actual deployed frontend origin and real supported variable names. Never expose backend secrets as frontend `VITE_*` variables.

Start command must match the actual project, for example a Uvicorn command pointing to the real FastAPI app module. Do not guess the module path; inspect the source and README.

## 4. Frontend configuration
- Set the frontend API base URL to the actual deployed backend base URL using the application's documented environment-variable name.
- Ensure the variable is designed to be public if bundled into the frontend.
- Rebuild and redeploy after changing a Vite build-time variable.
- Do not include private API keys in frontend environment variables.

## 5. Deployment steps
1. Commit reviewed code and push to the correct repository if using Git-based deployment.
2. Create/configure the backend service from the repository.
3. Set the Python version, build command, start command, working directory, and environment variables based on the actual repository.
4. Deploy and inspect build/runtime logs for errors. Never paste secrets into logs or reports.
5. Open the backend health endpoint. Confirm the expected response without exposing internal details.
6. Configure CORS for the exact frontend origin.
7. Create/configure static frontend hosting.
8. Set the API base URL and run a production build.
9. Deploy the frontend.
10. Test the public URL in a fresh browser session:
    - URL analysis with an illustrative test string.
    - Message analysis with a test message.
    - English/Hinglish explanation toggle.
    - Learning section and quiz.
    - Empty/invalid/oversized input.
    - Backend unavailable/error state where practical.
11. Confirm browser devtools show successful API requests to the intended backend and no secret values.
12. Record deployment date, verified URL, test cases, and any known limitations.

## 6. Model artifact and dataset considerations
- Do not commit large or restricted datasets without checking license and repository policy.
- Do not commit generated caches, raw personal data, or secrets.
- If model artifacts are too large or excluded from Git, document the exact reproducible training/build process.
- A deployed API must fail clearly and safely if the model artifact is missing. It must not silently return fake predictions.
- Do not use live data services unless actually integrated, permitted, and tested.

## 7. Common deployment issues
### CORS errors
Check the browser console and backend CORS configuration. Allow the exact frontend origin, including scheme and hostname. Do not use an unrestricted wildcard with credentials.

### API base URL is wrong
Check the built frontend's configured public API URL. Rebuild the frontend after changing build-time variables.

### Backend starts locally but not on host
Check Python version, dependency file, working directory, app import path, port binding, and the host's expected start command.

### Model file missing
Confirm artifact path, whether it is included in deployment, working directory, and build process. Do not substitute mock output.

### Free host sleeps or cold starts
Document the delay and show a proper loading/error state. Do not imply real-time availability if the host cannot guarantee it.

### Memory/build limits
Reduce unnecessary dependencies and artifact size only when doing so preserves correct behavior. Do not remove validation or tests to fit limits without explaining the trade-off.

## 8. Rollback and secrets
- Keep the last known-good deployment/commit identifiable.
- Revert using the hosting provider's supported rollback or a known-good commit.
- If a secret is exposed, revoke/rotate it immediately and remove it from the active configuration and history where appropriate.
- Never put tokens or passwords in this guide.

## 9. Deployment completion record
- **Frontend URL:** Held pending manual user deployment (M-05); verified local runtime at `http://localhost:5173`
- **Backend health URL:** Held pending manual user deployment (M-05); verified local endpoint at `http://localhost:8000/health`
- **Commit/version:** `docs(deploy): document verified setup and deployment configuration`
- **Test date:** 2026-10-29
- **URL analysis verified:** Yes (150 backend unit & smoke tests passing; verified with benign academic domains, banking phishing simulations, and shorteners)
- **Message analysis verified:** Yes (150 backend unit & smoke tests passing; verified with fake internships, lottery messages, bank KYC threats, and benign chats)
- **Model method and version:** RandomForestClassifier (53 structural URL features, v1.0.0, trained on Hannousse & Yahiouche 2020 Mendeley dataset, CC BY 4.0; 90.09% test accuracy)
- **Known limitations:**
  - Analysis is static and lexical; pages are never fetched to guarantee user privacy.
  - Link shorteners are flagged as suspicious by heuristic rule because resolving targets would break the zero-fetch guarantee.
  - Message analysis is deterministic rule-based (no LLM/NLP).
  - Production cloud hosting is held pending manual user action per M-05.
- **Deployment blocker:**
  - Live deployment requires a user-owned cloud account (Render, Vercel, or Netlify), manual dashboard sign-in, and repository connection, as explicitly required in `manual_actions.md` (M-05).
  - No third-party credentials or API tokens exist in the local environment, and project rules strictly prohibit storing credentials in source code.
  - The local development setup is 100% verified, reproducible, and ready for deployment following the steps in Section 5 and `manual_actions.md`.

A local-only app can still be a valid project outcome if it runs reliably and real screenshots are provided. Never invent a public URL.
