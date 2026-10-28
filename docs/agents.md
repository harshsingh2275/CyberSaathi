# Antigravity Agent Instructions — CyberSaathi AI

## Mission
Build **CyberSaathi AI**, a functional cybersecurity awareness web application that helps college students and beginner internet users assess suspicious URLs and copied messages, understand warning indicators, and learn safer online behavior. Primary SDG alignment: **SDG 4 — Quality Education**. SDG 9 and SDG 16 are supporting connections, not claims of measured impact.

## Project identity
- Student: Shashwat Singh
- Internship ID: IBMUEML010372
- College: ABES Engineering College, Ghaziabad
- Program: IBM SkillsBuild – AICTE – BharatCares Machine Learning & Applied AI Internship 2026
- Deadline for implementation: four days from the user's start date.

## Read before coding
Read these files in order:
1. `project.md`
2. `prd.md`
3. `architecture.md`
4. `task.md`
5. `prompts.md`
6. `manual_actions.md`
7. `model_guide.md`
8. `deployment_guide.md`
9. `design.md` when the user supplies it.

`start_to_finish_guide.md` is the human operator's short execution checklist. `operations-guide.md` covers post-build work.

## Working rules
- Inspect the repository before modifying it. Check Git status and preserve user work.
- Follow task IDs in `task.md` sequentially. Do not skip a failed prerequisite.
- Work in small verified increments. At the end of each task, report files changed, commands run, actual outcomes, blockers, and the next task.
- Use the exact task prompt in `prompts.md` as the starting instruction. Adapt only to the actual repository, and record meaningful deviations.
- Prefer a boring, maintainable, reliable implementation over excessive abstraction or features.
- Do not ask the user to perform a manual action unless it is listed in `manual_actions.md` or genuinely required. If needed, stop at a clear handoff and give precise instructions.
- Do not invent completion, successful tests, model metrics, datasets, deployment URLs, API integrations, or screenshots.
- Keep model outputs, deterministic rules, and any external intelligence separate in both code and UI.
- No paid LLM API is required. The core product must work without an API key.
- Never make the website a static mock or hard-code analysis results as if they were real.
- Never open, fetch, crawl, preview, or navigate to a submitted URL. Analyze its string/features only.
- No account system, database, or raw-submission history is needed for the MVP.
- Never put secrets in source control or frontend bundles.
- Do not use `design.md` as permission to violate safety or the PRD. If the design conflicts, explain and choose the safer functional behavior.

## Product behavior requirements
### URL analysis
- Validate input as a URL string without making a network request to it.
- Extract local lexical/structural features only, such as length, host/IP use, number of subdomains, punycode marker, unusual delimiters, and suspicious path/query patterns where technically appropriate.
- Only use features supported by the trained model's actual feature schema.
- Do not treat HTTPS as proof of trustworthiness.
- Return cautious categories: `High Risk`, `Suspicious`, `No Obvious Warning Signs`, or `Unable to Assess` if the model/data cannot support an assessment.
- A low-risk result is not a safety guarantee.

### Message analysis
- Accept copied SMS, email, internship, job, scholarship, and payment messages.
- Use a trained text model only if a legitimate, documented dataset and reproducible evaluation are available.
- Supplementary rules may flag urgency, upfront payment demands, credential/OTP requests, impersonation cues, and suspicious links.
- The UI/API must say whether the result comes from an ML model, rules, or both.
- Do not imply rules are an ML model.

### Explainability and language
- Explain each detected indicator in beginner-friendly language.
- Support English and Hinglish explanation text.
- Language selection changes explanations, not the underlying prediction, unless separately implemented and validated.
- Do not claim Hinglish model accuracy/validation without measured evidence.

### Safety and privacy
- Treat all user input as untrusted data.
- Enforce input length limits and strict request schemas.
- Do not store raw URLs/messages or log them.
- Do not render submitted content as unsafe HTML.
- Never ask for passwords, OTPs, or other secrets.
- Do not promise detection of all scams or claim content is safe.
- Clearly display that classification can be wrong and recommend independent verification through official channels.

## Technical direction
Preferred stack, unless repository constraints justify a documented change:
- Frontend: React + TypeScript + Vite + Tailwind CSS.
- Backend: Python + FastAPI + Pydantic.
- ML: scikit-learn, pandas, NumPy where needed.
- Tests: pytest for backend/model code; existing frontend test/lint/build tools where configured.
- No database or paid API for the core MVP.

Keep a clear separation between:
- frontend UI,
- backend schemas/routes,
- URL feature extraction,
- message feature/rule logic,
- model training/evaluation,
- saved model artifacts,
- educational content,
- tests and documentation.

## Data and model integrity
- Verify dataset provenance, access, license/terms, label meanings, and limitations.
- Avoid duplicates and train/test leakage.
- Split data before fitting learned preprocessing. Use a held-out test set.
- Record random seeds and commands.
- Report precision, recall, F1-score, confusion matrix, class balance, and relevant limitations from actual runs.
- Never fabricate data or results. If no valid dataset can be obtained in time, document the blocker and keep a transparent, deterministic fallback rather than falsely claiming ML.

## UI requirements before `design.md` arrives
Use accessible semantic HTML, keyboard support, clear hierarchy, responsive layouts, readable contrast, useful empty/loading/error/success states, and concise safety language. Do not use fake live statistics, fake recent scans, fake threat maps, or decorative elements that imply nonexistent functionality.

## Completion reporting template
At the end of each task report:
- **Task:** ID and name
- **Status:** Complete / Partial / Blocked
- **Changed:** key files
- **Verification:** exact commands and actual results
- **Risks/blockers:** anything unresolved
- **Next:** next task ID

A task is not complete just because code was generated. It is complete when its acceptance criteria are verified.
