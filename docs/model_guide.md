# Model Guide — High-Risk Tasks for Claude in Antigravity

Yeh guide batati hai kaunse tasks technically difficult ya correctness ke liye critical hain. Claude model ko in tasks par use karo. Claude ko bhi `agents.md`, `prd.md`, `architecture.md`, `task.md` aur actual repo inspect karna chahiye.

## Highest priority: Claude recommended

### T-02 / P-02 — Dataset validation, ML training and evaluation
**Why hard:** Dataset labels, licensing, duplicate leakage, feature mismatch, preprocessing leakage, imbalanced classes, and reproducibility are easy to get wrong.
**Claude should handle:**
- Dataset source/terms/labels audit.
- Feature extraction and training pipeline consistency.
- Leakage-aware split and training-only preprocessing.
- Reproducible baseline and saved artifact.
- Actual precision, recall, F1-score, confusion matrix, class balance, false-negative/false-positive review.
- Tests proving inference features match training features.
**Do not accept:** fabricated metrics, unexplained dataset, random train/test split after preprocessing, or a model artifact without a repeatable training command.

### T-03 / P-03 — Backend/model integration and safe URL handling
**Why hard:** The API must load the right artifact, validate input, produce consistent output, and never make network requests to the submitted URL.
**Claude should handle:**
- FastAPI/Pydantic schemas.
- Correct model loading and failure handling.
- Strict separation of ML output and rule indicators.
- Unit tests for URL parsing, input validation, and error paths.
- Ensuring no HTTP client/browser/DNS call is triggered by user URL input.
**Do not accept:** silently falling back to fake predictions, raw input logging, broad exception swallowing, or unsupported confidence claims.

### T-06 / P-06 — Security/privacy and end-to-end verification
**Why hard:** A product can appear functional while leaking input, exposing secrets, or giving misleading risk labels.
**Claude should handle:**
- Security review of all routes and frontend input rendering.
- Input size/type validation, CORS, secret handling, logging, and error responses.
- Confirmation no submitted URL is opened/fetched/resolved.
- Tests that reflect actual user flows.
- Honest list of unresolved risks.
**Do not accept:** deleting tests, weakening assertions, or claiming a check passed without running it.

## Next priority

### T-01 / P-01 — Architecture and API contracts
Use Claude if existing code is tangled or frontend/backend contracts are unclear. Ask it to preserve working code and propose minimal changes.

### T-04 / P-04 — Frontend integration
Use Claude if API integration, TypeScript types, loading/error states, accessibility, or responsive behavior is failing. Ensure it uses actual API results rather than mocks.

### T-07 / P-07 — Deployment troubleshooting
Use Claude if the hosting build fails, model artifacts are missing, environment variables/CORS are wrong, or the backend start command is unclear. Do not provide it with secrets.

## Suggested division of work
- Antigravity default model: T-00, documentation, project skeleton, routine UI, education content, README updates.
- Claude: T-02, T-03, T-06, and difficult blockers in T-01/T-04/T-07.
- User: dataset terms review where needed, account authorization, deployment secrets, live smoke test, final acceptance.

## Before accepting Claude output
1. Did it inspect actual source files?
2. Does code match the documented model feature schema?
3. Are results based on a real model or explicitly labeled rules?
4. Are tests actually run?
5. Are all metrics derived from real output?
6. Are URL submissions never fetched/opened?
7. Are raw inputs and secrets protected?
8. Does the README match actual behavior?
