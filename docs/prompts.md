# Antigravity Task Prompts and Commit Statements

Use one prompt per task in sequence. Tasks are grouped where safe. The ML/data and security tasks remain separate because they are high-risk and require explicit verification. Run the relevant checks before committing. If Git is not initialized, do not initialize or commit without confirming the existing repository situation.

## P-00 — Repository audit
**Use for:** T-00

```text
Inspect the entire current repository before making changes. Review the file tree, Git status/history, README, package/dependency files, frontend/backend code, ML assets, tests, environment configuration, and existing docs. Do not overwrite or delete working code. Classify each requirement as implemented, partial, missing, or unverified. Give me a concise audit and a four-day plan aligned with task.md. Identify the fastest reliable route to a real end-to-end product. Do not make claims without evidence. Do not start broad implementation until the audit is complete.
```

**Commit statement after verification:** `chore: audit existing project and document implementation baseline`

## P-01 — Architecture, skeleton, and API contract
**Use for:** T-01

```text
Implement task T-01 from task.md. First read project.md, prd.md, architecture.md, agents.md, and task.md. Adapt to the audited repository instead of blindly replacing its structure. Establish the minimum maintainable project layout, configuration, request/response schemas, API contracts, CORS policy, input limits, and commands for running and testing frontend/backend. Include /health, /api/analyze/url, and /api/analyze/message contracts. Add or update documentation for the actual structure. Do not build fake analysis responses. Ensure secrets and local environment files are ignored by Git. Run available setup checks and report exact results.
```

**Commit statement:** `chore: establish application structure and API contracts`

## P-02 — Dataset audit and reproducible ML baseline (high importance)
**Use for:** T-02. Keep this task separate.

```text
Implement T-02 only after repository inspection. Focus first on a legitimate URL-classification baseline. Find or inspect candidate public datasets, but verify source, access, terms/license, labels, format, class balance, duplicates, and limitations before using them. Do not invent a dataset or silently scrape sites. Build reproducible preprocessing and training with a fixed random seed and leakage-aware train/validation/test separation. Fit preprocessing on training data only. Evaluate on held-out data with precision, recall, F1-score, confusion matrix, class balance, and false-negative/false-positive considerations. Save the trained artifact and feature/schema metadata in a documented location. Add a repeatable command and tests for loading the model and extracting the same feature schema used during training. Consider message classification only if an appropriate dataset can be validated without jeopardizing the URL model and app integration. Never invent metrics. If data access or licensing is unclear, stop and report it, then propose a transparent rules-based fallback; do not describe that fallback as ML.
```

**Commit statement:** `feat(ml): add reproducible URL classifier and measured evaluation`

## P-03 — FastAPI endpoints, analysis logic, and tests
**Use for:** T-03

```text
Implement T-03. Build the FastAPI backend using the actual trained artifact from T-02 where available. Add /health, /api/analyze/url, and /api/analyze/message endpoints with strict Pydantic schemas, input limits, clear error responses, and CORS configured through environment settings. URL analysis must only parse the submitted string and extract local features. Absolutely no HTTP request, browser navigation, DNS lookup, crawling, or preview of the submitted URL. Keep model predictions separate from rule-based indicators and return the method/source explicitly. Use cautious risk categories and actionable advice. For messages, use a trained classifier only if it is genuinely trained and evaluated; otherwise use transparent rules and label the method accordingly. Do not persist or log raw inputs. Add pytest coverage for normal, suspicious, benign-looking, empty, malformed, oversized, model-loading failure, and error paths. Run tests and fix failures without weakening assertions.
```

**Commit statement:** `feat(api): implement safe analysis endpoints and automated tests`

## P-04 — Frontend and real API integration
**Use for:** T-04

```text
Implement T-04. Build a real responsive React/TypeScript interface that calls the actual backend. Provide URL and message modes, validated input, loading/error/success states, risk category, explanation, warning indicators, safe next steps, method/source disclosure, and limitations. Add English/Hinglish explanation selection. Do not hard-code fake scan results or present sample content as a live result. Make API base URL configurable for local and deployed environments without exposing secrets. Use semantic accessible controls, keyboard navigation, and mobile-friendly layout. Read design.md if it exists; otherwise use a polished, restrained design system and avoid generic AI dashboard tropes. Test both flows end to end, including backend errors. Do not mark this task complete if the frontend is only a static mock.
```

**Commit statement:** `feat(frontend): connect analysis interface to live backend`

## P-05 — Learning section and quiz
**Use for:** T-05

```text
Implement T-05 with compact, locally bundled educational content. Cover phishing basics, suspicious links, internship/job scams, scholarship/payment scams, password and OTP safety, official-channel verification, and what to do after clicking a suspicious link or sharing sensitive information. Add a small quiz with answer feedback and explanations. Keep all content understandable for beginners and provide English/Hinglish explanation where practical. No LLM or paid external API. Ensure lesson/quiz navigation works and does not imply the user is protected simply by completing a quiz. Add tests or a documented manual check for answer consistency.
```

**Commit statement:** `feat(education): add cybersecurity lessons and awareness quiz`

## P-06 — Security, privacy, accessibility, and quality pass (high importance)
**Use for:** T-06. Keep this task separate.

```text
Perform T-06 as a security and quality review, not a visual redesign. Inspect every route and input path. Verify that submitted URLs are never opened, fetched, crawled, resolved, or previewed; raw submissions are not persisted/logged; input sizes and types are validated; HTML injection is prevented; secrets are not exposed; CORS is restricted to intended origins; errors do not reveal secrets; and the UI avoids definitive safety claims. Verify model/rules/external-intelligence separation. Run backend tests, frontend lint/build/tests if available, and realistic end-to-end smoke tests. Fix actual defects. Do not silence failures, remove meaningful assertions, or report commands that were not run. Update privacy notice, limitations, and known issues to match the implementation. Provide exact command output summaries.
```

**Commit statement:** `test(security): harden input handling and verify end-to-end behavior`

## P-07 — Deployment and docs
**Use for:** T-07

```text
Implement T-07 only after local end-to-end tests pass. Read deployment_guide.md. Choose the simplest suitable hosting approach for the actual repository and available free-tier limits. Confirm build commands, start commands, environment variables, CORS, model artifact size, and health checks. Never place secrets in source code or frontend variables. If deployment needs a user-owned account, API token, or confirmation, stop and follow manual_actions.md, giving exact steps. Do not claim a live deployment until the URL is tested end to end. Update README, architecture, dataset/model provenance, reproducible training/evaluation commands, API contracts, setup instructions, and limitations. If deployment is blocked, finish reliable local setup and document the exact blocker.
```

**Commit statement:** `docs(deploy): document verified setup and deployment configuration`

## P-08 — Final acceptance and handoff
**Use for:** T-08

```text
Complete T-08. Start the project using the README's documented clean-start procedure. Test URL analysis, message analysis, English/Hinglish explanations, learning section, quiz, invalid/empty/oversized inputs, backend unavailable behavior, and responsive layout. Run the final test/build commands and record actual results. Capture genuine screenshots only from the running app. Review Git status and ensure .env files, credentials, unnecessary raw datasets, caches, build outputs, and private user data are not committed. Update README with verified features, exact commands, measured model results, known limitations, and actual deployment status. Produce a concise handoff report and identify any incomplete requirements honestly.
```

**Commit statement:** `chore: finalize verification evidence and project handoff`

## Commit discipline
- Commit only after task acceptance criteria pass.
- Review `git diff` and `git status` before committing.
- Never include `.env`, API keys, personal data, or raw user submissions.
- Do not use `git add .` blindly; stage reviewed files.
- If tests fail, fix them before commit or clearly report why a safe commit cannot be made.
- If a task is partial, use a truthful commit message and explain the remaining work.
