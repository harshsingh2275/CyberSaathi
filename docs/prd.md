# Product Requirements Document — CyberSaathi AI

## 1. Product summary
**CyberSaathi AI** is a cybersecurity awareness web application for college students and beginner internet users. It helps users review suspicious URLs and copied messages, understand warning indicators, and learn safer online practices through plain English and Hinglish explanations.

**Owner:** Shashwat Singh  
**Internship ID:** IBMUEML010372  
**Institution:** ABES Engineering College, Ghaziabad  
**Program:** IBM SkillsBuild – AICTE – BharatCares Machine Learning & Applied AI Internship 2026

## 2. Problem statement
Students and young internet users encounter phishing links, fake internship/job offers, scholarship scams, impersonation attempts, and fraudulent payment requests. Beginners may struggle to distinguish legitimate communication from potentially deceptive content. Existing warnings can be too technical or provide little explanation. CyberSaathi AI aims to make risk indicators understandable and provide safer next steps.

## 3. Goals
1. Analyze a submitted URL using local URL features and a documented, trained ML baseline where valid data and evaluation are available.
2. Analyze copied messages for common scam/phishing indicators using a trained text classifier when feasible, with transparently disclosed rules as a fallback or supplement.
3. Present cautious risk categories, indicators, explanations, and actionable recommendations.
4. Offer English and Hinglish explanations.
5. Provide a focused set of cybersecurity lessons and awareness quizzes.
6. Deliver a reproducible, tested application with clear privacy and model limitations.

## 4. Non-goals for the four-day MVP
- User accounts, authentication, or personal profiles.
- Database, scan history, analytics dashboard, or admin panel.
- Automated URL opening, crawling, DNS lookups, or website previews.
- Live threat-intelligence integration unless separately approved, implemented, and verified after the core MVP.
- Browser extension, mobile app, background monitoring, or notifications.
- Paid LLM API dependence.
- Claims of production-grade security or guaranteed detection.

## 5. Target users
- Primary: college students and beginner internet users.
- Secondary: schools, colleges, digital-literacy clubs, and community educators.
- Early adopters: student groups and campus communities accessible through workshops and peer sharing.

## 6. User stories
- As a student, I can paste a suspicious URL and receive a cautious assessment without the application visiting that URL.
- As a user, I can paste a suspicious SMS/email/offer and see indicators that deserve attention.
- As a beginner, I can understand the result without advanced security knowledge.
- As a user, I can switch explanation language between English and Hinglish.
- As a learner, I can read short lessons and complete a quiz with feedback.
- As a privacy-conscious user, I can use the core analysis without creating an account or having my raw submission stored by default.

## 7. Functional requirements
### FR-1 URL analysis
- Accept a URL string with maximum length limits.
- Parse and extract only local string/structural features.
- Use a real trained model if a documented dataset and reproducible evaluation are available.
- Return category, method/source, indicators, explanation, recommendations, and limitations.
- Never send a network request to the submitted URL.
- Never claim HTTPS alone proves trustworthiness.

### FR-2 Message analysis
- Accept copied SMS, email, internship, job, scholarship, or payment-related text.
- Detect indicators such as urgency, upfront payment, credential/OTP requests, impersonation language, and suspicious links.
- Use an evaluated trained classifier only if supported by real data.
- Clearly disclose when rules, rather than an ML model, generated the indicators/result.

### FR-3 Explanation and language
- Support English and Hinglish explanation text.
- Keep the model prediction distinct from explanatory text and rule-based indicators.
- Do not claim that the classifier has been validated on Hinglish unless measured evidence supports that claim.
- Show confidence only if the model's score is meaningful and properly interpreted.

### FR-4 Education and quiz
- Provide concise content on phishing, suspicious links, internship/job scams, scholarship/payment scams, password/OTP safety, official verification, and response after suspected compromise.
- Include a short quiz with correct-answer feedback and explanations.
- No paid external service required.

### FR-5 User experience
- Responsive desktop and mobile layouts.
- Clear mode selection and input area.
- Empty, invalid, loading, success, API error, and backend unavailable states.
- Keyboard accessible controls and semantic labels.
- Clear privacy notice and non-guarantee disclaimer.

## 8. Non-functional requirements
- Maintainable separation of frontend, API, model/rules, education content, and tests.
- Reproducible local setup and model training.
- Stable JSON schemas and predictable error handling.
- Configurable API base URL and environment-based CORS.
- No secrets in frontend bundles or version control.
- Avoid logging or persisting raw submissions.
- Reasonable input size limits and dependency hygiene.
- Core features work without paid API keys.

## 9. ML and data requirements
- Verify dataset source, license/terms, labels, class distribution, and limitations.
- Inspect duplicates and data leakage.
- Split data before fitting preprocessing; fit learned preprocessing on training data only.
- Use a held-out test set and fixed seeds where appropriate.
- Report actual precision, recall, F1-score, confusion matrix, class balance, and false-negative/false-positive considerations.
- Store the model artifact with matching feature/schema code.
- Never fabricate dataset sizes or metrics. If a valid model cannot be built, state the limitation and use a clearly labeled deterministic fallback.

## 10. Risk language
Allowed categories: `High Risk`, `Suspicious`, `No Obvious Warning Signs`, and `Unable to Assess` where appropriate.
- `No Obvious Warning Signs` must never be described as “safe.”
- Do not promise every scam will be detected.
- Explain that automated analysis can make mistakes and independent verification is necessary.

## 11. Success criteria
- Frontend and backend communicate successfully.
- URL analysis uses the actual model if model completion is verified, or transparently disclosed fallback behavior.
- Message analysis behaves as documented and labels its method accurately.
- Results include understandable indicators and safe next steps.
- English/Hinglish explanation toggle works.
- Lessons and quiz work.
- Invalid input and service failures are handled gracefully.
- Submitted URLs are never opened or fetched.
- No raw submissions are stored/logged by default.
- Model evaluation is reproducible and documentation matches actual implementation.
- Another person can run the app from the README or access a verified deployment.

## 12. Evidence and internship deliverables
- Working application and source code.
- Reproducible README and setup instructions.
- Dataset provenance and model training/evaluation outputs, where applicable.
- API tests and end-to-end verification.
- Genuine screenshots and, if verified, deployment URL.
- Consistent Concept Note, Lean Canvas, and presentation.
- Clearly distinguish implemented features from planned/future work.

## 13. Constraints and priority
The build window is four days. Prioritize the complete, secure end-to-end flow. Defer optional features before compromising input safety, transparent analysis, testing, or reproducibility.
