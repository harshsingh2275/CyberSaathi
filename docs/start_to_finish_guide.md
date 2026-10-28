# Start-to-Finish Guide (4 Days)

Is file mein sirf order, kya karna hai, aur kaunsi file dekhni hai diya gaya hai. Detailed instructions respective files mein hain.

## Day 1
1. **Repository inspect karna** → `P-00` run karo → Details: `prompts.md`, `task.md` (T-00).
2. **Project setup aur API contracts lock karna** → `P-01` run karo → Details: `prompts.md`, `architecture.md`, `prd.md` (T-01).
3. **Dataset/model feasibility verify karna** → `M-02` manually complete karo → Details: `manual_actions.md`, `model_guide.md`.
4. **URL model baseline banana** → `P-02` run karo → Details: `prompts.md`, `model_guide.md`, `task.md` (T-02).

## Day 2
5. **Backend endpoints aur tests banana** → `P-03` run karo → Details: `prompts.md`, `architecture.md`, `prd.md` (T-03).
6. **Backend tests aur real model loading verify karna** → Antigravity se actual test commands/results lo → Details: `task.md`, `model_guide.md`.

## Day 3
7. **Frontend ko real backend se connect karna** → `P-04` run karo → Details: `prompts.md`, `prd.md`, aur `design.md` agar available ho (T-04).
8. **Lessons aur quiz add karna** → `P-05` run karo → Details: `prompts.md`, `prd.md` (T-05).
9. **Local end-to-end check karna** → URL, message, language toggle, lesson aur quiz manually test karo → Details: `task.md`, `manual_actions.md`.

## Day 4
10. **Security/privacy/testing pass** → `P-06` run karo → Details: `prompts.md`, `architecture.md`, `prd.md` (T-06).
11. **Deployment karna, agar local app verified hai** → `M-05` follow karo aur `P-07` run karo → Details: `deployment_guide.md`, `manual_actions.md` (T-07).
12. **Final acceptance, screenshots, README aur handoff** → `P-08` run karo → Details: `task.md`, `prompts.md`, `manual_actions.md` (T-08).
13. **Project ko khud explain karne ki preparation** → `project.md` aur `model_guide.md` padho.
14. **Deployment ke baad maintenance/future improvements** → `operations-guide.md` dekho.

## Important short-name mapping
- `M-xx` = `docs/manual-actions.md`
- `P-xx`, `X-xx`, `S-xx`, `H-xx` = `docs/prompt.md`
- `T-xx` = `docs/task.md`
- Deploy steps = `docs/deployment-guide.md`
- Baad ka kaam = `docs/operations-guide.md`

## Priority rule
Agar time kam ho: working URL/message analysis, transparent ML/rules labels, safety, tests, README aur screenshots pehle. Accounts, database, live threat intelligence, browser extension aur fancy animations baad mein.
