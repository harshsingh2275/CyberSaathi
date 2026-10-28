# Operations Guide — After the Four-Day Build

Yeh file project complete hone ke baad maintenance aur future improvements ke liye hai. Core MVP verify hone se pehle is list par kaam mat shuru karna.

## O-01 — Regular health checks
- Backend health endpoint check karo.
- Frontend se URL aur message analysis ka smoke test run karo.
- Hosting logs mein errors check karo, lekin raw submissions/secrets log nahi hone chahiye.
- Deployment provider ke uptime, sleep/cold-start aur build limits review karo.

## O-02 — Dataset and model updates
- Naya dataset add karne se pehle provenance, license, labels aur privacy review karo.
- Duplicates aur leakage check karo.
- Existing model ke saath held-out metrics compare karo.
- Model ko replace tabhi karo jab evaluation reproducible ho aur trade-offs documented hon.
- Model artifact aur training code version together track karo.
- Previous known-good model ko rollback ke liye preserve karo.

## O-03 — Improve explanations and education
- Students se voluntary feedback lo, sensitive input collect kiye bina.
- Lesson clarity, quiz accuracy aur result explanations improve karo.
- English/Hinglish translations ko meaning ke liye review karo.
- Hinglish model classification claim tabhi add karo jab suitable data aur evaluation ho.

## O-04 — Security and privacy review
- Dependencies update karte waqt tests rerun karo.
- CORS origins aur environment variables review karo.
- Ensure raw URLs/messages logs, analytics, screenshots, or persistence mein accidentally na aa rahe hon.
- Agar secret leak ho, revoke/rotate karo.
- User-submitted URLs ko fetch/open karne wali feature kabhi silently add mat karo.

## O-05 — Future features (only after validation)
Possible later improvements:
- Validated multilingual message classifier.
- Verified threat-intelligence integration with explicit separation from local model results.
- Better calibration and explainability.
- Larger/diverse datasets and drift monitoring.
- Browser extension only after a separate threat model and privacy review.
- Institution/educator feedback workflow.

Har new feature ke liye scope, risks, tests aur manual actions pehle define karo. Live threat intelligence, accounts, databases, and browser extensions are not required for the initial MVP.

## O-06 — Presentation and internship evidence
- Keep genuine screenshots and test outputs current.
- Record exact model version and measured metrics.
- Update architecture and README whenever behavior changes.
- Keep Concept Note, Lean Canvas, and PPT consistent.
- Separate implemented, planned, and future-scope items.
