# CyberSaathi AI — Project ko Hinglish mein samjho

## 1. Project kya hai?
CyberSaathi AI ek cybersecurity awareness web application hai. Iska purpose students aur normal internet users ko suspicious links aur scam messages samajhne mein help karna hai. User URL ya copied SMS/email/internship/job/scholarship message paste karega. App warning signs explain karega aur safer next steps suggest karega.

**One-line explanation:** “CyberSaathi AI ek student-focused tool hai jo suspicious URLs aur scam-like messages ko assess karke unke warning signs simple English ya Hinglish mein samjhata hai.”

## 2. Problem kya solve karta hai?
Students ko fake internship offers, scholarship scams, phishing links, fake job offers, impersonation aur payment-demand messages mil sakte hain. Beginners ko hamesha samajh nahi aata ki message mein kya suspicious hai. Kuch tools sirf label dete hain, explanation nahi. CyberSaathi AI ka focus sirf warning dena nahi, balki user ko batana hai ki warning kyun aayi aur ab safely kya karna chahiye.

## 3. Target users
- Primary: college students aur beginner internet users.
- Secondary: schools, colleges, digital-literacy clubs aur community educators.
- Early users: campus groups aur student communities.

## 4. App ka workflow
1. User choose karega: URL analysis ya message analysis.
2. User input paste karega.
3. Backend input validate karega.
4. URL ke case mein app URL ko **open ya fetch nahi karega**. Sirf string ke features analyze honge.
5. Valid trained model available hua to model prediction dega. Message analysis mein trained model tabhi use hoga jab real dataset aur evaluation available ho. Warna rules-based indicators transparently use honge.
6. Result mein cautious risk category, indicators, explanation aur next steps dikhaye jayenge.
7. User English ya Hinglish explanation select kar sakta hai.
8. Learning section mein phishing, OTP/password safety, internship scams jaise topics aur short quiz honge.

## 5. AI/ML ka role
URL classifier URL ki structural/lexical features dekh sakta hai, jaise URL length, subdomains, IP address usage, unusual symbols aur path/query patterns. Exact features trained model ke feature schema se match hone chahiye.

Message analysis mein urgency, advance payment demand, credentials/OTP request, impersonation language aur suspicious links jaise indicators identify ho sakte hain. Ye indicators rules se aaye hain ya trained ML model se, app ko clearly batana hai.

**Important:** Rules-based detection ko ML model bolna galat hoga. Model accuracy ya dataset size bina actual experiment ke nahi likhna.

## 6. Result ka meaning
- **High Risk:** implemented method ko strong ya multiple warning signs mile.
- **Suspicious:** warning signs hain, independent verification karo.
- **No Obvious Warning Signs:** current checks ko notable warning signs nahi mile. Iska matlab guaranteed safe nahi hai.
- **Unable to Assess:** input unsupported hai ya model/analysis available nahi.

HTTPS hona apne aap mein website ko trustworthy prove nahi karta. App kisi URL ko automatically open nahi karega aur passwords/OTP nahi maangega.

## 7. Project ka unique value
CyberSaathi AI ka focus beginners aur Indian college students hain. Ye:
- warning signs explain karta hai,
- English aur Hinglish explanations deta hai,
- internship, job, scholarship aur payment scam jaise relatable examples cover karta hai,
- actionable next steps deta hai,
- cybersecurity learning aur quiz ko analysis ke saath combine karta hai.

Ye claim nahi karna ki underlying technology duniya mein unique hai. Differentiator beginner-friendly explanation aur education-focused experience hai.

## 8. Proposed tech stack
- Frontend: React, TypeScript, Vite, Tailwind CSS.
- Backend: Python, FastAPI, Pydantic.
- ML: scikit-learn, pandas, NumPy.
- URL classifier: documented dataset par trained baseline.
- Message classifier: valid dataset aur time available ho to; otherwise clearly labeled rules-based analysis.
- Database/login: MVP ke liye required nahi.
- Paid LLM API: core product ke liye required nahi.

## 9. Privacy aur safety
- Raw URL/message default mein store ya log nahi karna.
- User ka URL kabhi open, crawl, preview ya fetch nahi karna.
- Input size limit aur validation honi chahiye.
- Secrets frontend/GitHub mein nahi hone chahiye.
- App ko guarantee nahi deni ki content safe hai.
- User ko official website/channel independently verify karne ki advice deni hai.

## 10. SDG alignment
- **Primary: SDG 4 — Quality Education**, kyunki app cybersecurity awareness ko accessible banata hai.
- **Supporting: SDG 9 — Industry, Innovation and Infrastructure**, kyunki practical ML application develop hoti hai.
- **Supporting: SDG 16 — Peace, Justice and Strong Institutions**, kyunki deceptive online communication aur safer digital behavior ke baare mein awareness promote hoti hai.

Ye alignment intended contribution hai; actual social impact ko measure kiye bina numbers ya impact claims nahi karne.

## 11. Four-day build strategy
- Day 1: repository audit, architecture, dataset verification, URL model baseline.
- Day 2: FastAPI backend, analysis logic, automated tests.
- Day 3: frontend integration, English/Hinglish explanations, learning section and quiz.
- Day 4: security/privacy pass, end-to-end tests, deployment if feasible, README and screenshots.

## 12. Project ko kisi ko explain karte waqt kya bolna hai?
“CyberSaathi AI ek AI/ML-supported cybersecurity awareness web app hai. Isme user suspicious URL ya message paste kar sakta hai. App URL ko open kiye bina uske features analyze karta hai aur message mein scam indicators check karta hai. Result mein risk category, warning signs aur safe next steps milte hain. Beginners ke liye English/Hinglish explanations aur short awareness lessons bhi hain. Model prediction aur rule-based indicators ko alag rakha gaya hai, aur app clearly batata hai ki result guarantee nahi hai.”

## 13. Kya claim nahi karna
- “Har scam detect karta hai.”
- “No warning signs means safe.”
- “Live threat intelligence integrated hai” jab tak actually integrated/tested na ho.
- “Model 99% accurate hai” jab tak actual evaluation output na ho.
- “Hinglish model validated hai” jab tak suitable test data se prove na ho.
- “Website deployed hai” jab tak actual live URL verify na ho.
- Planned features ko implemented features ki tarah present nahi karna.

## 14. Internship deliverables
Working application, source code, README, dataset/model evaluation evidence, API tests, genuine screenshots, architecture/workflow explanation, Concept Note, Lean Canvas aur presentation. Sabhi documents mein same project scope aur honest implementation status hona chahiye.
