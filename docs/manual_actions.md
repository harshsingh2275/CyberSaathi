# Manual Actions — CyberSaathi AI (M-xx)

Yeh file sirf un actions ke liye hai jo user ko khud karne pad sakte hain. Har action zaroori nahi hai. **Core ML analysis ke liye paid LLM API key ki requirement nahi honi chahiye.**

## M-00 — Repository open aur baseline confirm
1. Antigravity mein CyberSaathi AI ka correct project folder open karo.
2. Confirm karo ki existing code ka backup/version control available hai.
3. Antigravity se `P-00` run karwao aur audit padh lo.
4. Agar repo mein important existing code hai, bina samjhe replace karne ki permission mat do.

**Done when:** Project folder correct hai aur existing code ki state clear hai.

## M-01 — Python aur Node environment
1. Terminal mein `python --version` (ya `py --version`) check karo.
2. `node --version` aur `npm --version` check karo.
3. Agar project ke existing README mein specific versions hain, unhe priority do.
4. Missing runtime install karna pade to official installer use karo. Installation ke baad terminal restart karke versions verify karo.

**Done when:** Backend aur frontend ke required runtimes available hain.

## M-02 — Dataset source/licensing review
1. Antigravity/Claude jo dataset suggest kare, uska original source page kholo.
2. Confirm karo ki source accessible hai, use terms/license samajh aate hain, aur academic project ke liye allowed hai.
3. Agar terms unclear hain, dataset ko use karne ki approval mat do. Alternative dataset ya transparent rules fallback choose karo.
4. Dataset files mein personal data ya unnecessary sensitive content ho to stop karke review karo.

**Done when:** Dataset provenance, terms, labels aur limitations documented hain. Koi fabricated dataset nahi hai.

## M-03 — Secrets/API keys (normally not required)
- MVP ko paid LLM key ke bina kaam karna chahiye.
- Agar hosting provider token ya optional third-party service key genuinely needed ho, use sirf provider ke official dashboard se generate karo.
- Key ko `.env` ya hosting dashboard ke secret/environment-variable panel mein rakho. GitHub, source code, screenshots, frontend `VITE_*` variable, ya public documentation mein secret mat daalo.
- Key share karne ki zaroorat ho to chat mein paste na karo; local environment/dashboard mein khud set karo.
- Kisi paid service ke liye payment method/plan activation maanga jaye to pehle cost confirm karo. User approval ke bina paid service enable mat karo.

**Done when:** Required secrets local/hosting environment mein secure hain, ya confirm hai ki key ki zaroorat nahi.

## M-04 — GitHub repository (optional, recommended)
1. Agar Git repo pehle se hai, remote aur current branch verify karo.
2. Agar GitHub par push karna hai, user-owned repository select/create karo.
3. `.env`, credentials, private data, model caches, aur unwanted raw datasets commit na hon.
4. Push se pehle `git status` aur staged diff check karo.
5. Antigravity ko commits tabhi karne do jab task verify ho aur user ka repository workflow clear ho.

**Done when:** Reviewed source code version control mein hai; secrets nahi hain.

## M-05 — Deployment account/manual approval
1. `deployment_guide.md` tabhi follow karo jab local tests pass ho jaayein.
2. Hosting provider choose karne se pehle free-tier limits, sleep/cold-start behavior, model artifact size aur backend support check karo.
3. Agar provider login, OAuth approval, GitHub authorization, card/payment details, domain purchase ya token ki zaroorat ho, yeh step khud complete karo.
4. Credentials ko Antigravity prompt ya source code mein paste mat karo.
5. Deployment ke baad actual public URL ko browser mein khol kar URL analysis aur message analysis test karo.

**Done when:** Live app end-to-end verify ho gayi hai, ya deployment ka blocker clearly documented hai.

## M-06 — Final human acceptance
1. Local ya deployed app khud use karke URL aur message dono test karo.
2. English/Hinglish toggle, learning section, quiz, empty input, invalid input aur backend unavailable state check karo.
3. Screenshots sirf actual running app se lo.
4. Model metrics aur dataset information ko training output se match karo.
5. Project explain karne se pehle model ki limitations aur rules-vs-ML difference samajh lo.

**Done when:** Tum independently project ka workflow, actual implemented features, model evaluation aur limitations explain kar sakte ho.

## Important
Agar Antigravity kisi manual action ke liye rukta hai, usse exact screen/menu, required value name, expected outcome, aur next step batane ko bolo. Secret values ko response mein print karne ki zaroorat nahi hai.
