/**
 * CyberSaathi AI — Locally bundled quiz content for T-05.
 *
 * Rules enforced by the type system and the consistency check in
 * scripts/check-quiz-consistency.ts:
 *
 *   1. `correctIndex` must be a valid index into the `options` array.
 *   2. Every option must be a non-empty string.
 *   3. `explanationEn` and `explanationHi` must both be non-empty.
 *   4. `correctIndex` must NOT point to a decoy/obviously-wrong answer —
 *      this is enforced by human review (see the consistency check script).
 *   5. No answer should imply the user is fully protected by completing this
 *      quiz. Explanations explicitly note ongoing vigilance is required.
 *
 * IMPORTANT — when editing questions:
 *   - Run `npm run check-quiz` (or `npx ts-node scripts/check-quiz-consistency.ts`)
 *     to verify structural consistency before committing.
 *   - If you change option order, update `correctIndex` accordingly.
 *   - Each question belongs to a lesson (`lessonId`) so results can be
 *     grouped by topic. Use a LESSONS id from lessons.ts.
 */

export interface QuizQuestion {
  id: string;
  /** Maps to a lesson id in lessons.ts */
  lessonId: string;
  questionEn: string;
  questionHi: string;
  /** 2–4 choices; correctIndex is 0-based */
  options: {
    textEn: string;
    textHi: string;
  }[];
  /** 0-based index into options[] pointing to the correct answer */
  correctIndex: number;
  /** Explanation shown after any answer is selected */
  explanationEn: string;
  explanationHi: string;
}

export const QUIZ_QUESTIONS: QuizQuestion[] = [
  // ── Phishing basics ────────────────────────────────────────────────────────
  {
    id: 'q-phishing-1',
    lessonId: 'phishing-basics',
    questionEn:
      'You receive an urgent email saying your bank account will be blocked unless you click a link and verify your OTP. What should you do?',
    questionHi:
      'Aapko ek urgent email aati hai jo kehti hai ki jab tak aap ek link click karke OTP verify na karein, aapka bank account block ho jayega. Aap kya karenge?',
    options: [
      {
        textEn: 'Click the link quickly to avoid losing account access.',
        textHi: 'Account access kho jaane se bachne ke liye jaldi link click karein.',
      },
      {
        textEn: 'Call your bank on its official helpline number to verify whether the alert is real.',
        textHi: 'Bank ke official helpline number par call karke confirm karein ki alert sach hai ya nahi.',
      },
      {
        textEn: 'Share the email with a friend so they can check if it is safe.',
        textHi: 'Email ek dost ke saath share karein taaki woh check kar sakein.',
      },
      {
        textEn: 'Reply to the email and ask the sender to prove they are from the bank.',
        textHi: 'Email ka reply karein aur sender se bank ka proof maangein.',
      },
    ],
    correctIndex: 1,
    explanationEn:
      'Always verify unexpected alerts by contacting your bank directly on the number printed on your card or the official website — not the number in the message. Banks never ask for OTPs over phone or email. Completing this quiz does not guarantee you will catch every phishing attempt; ongoing vigilance is essential.',
    explanationHi:
      'Kisi bhi unexpected alert ko verify karne ke liye apne card ke peeche ya official website par likhe number se seedha bank se contact karein — message mein diya number nahi. Banks kabhi phone ya email par OTP nahi maangte. Yeh quiz complete karna aapko hamesha safe nahi banata; lagatar vigilance zaruri hai.',
  },
  {
    id: 'q-phishing-2',
    lessonId: 'phishing-basics',
    questionEn: 'Which of the following is a typical sign of a phishing message?',
    questionHi: 'Niche diye mein se kaun sa phishing message ka typical sign hai?',
    options: [
      {
        textEn: 'The message addresses you by your full name and account number.',
        textHi: 'Message mein aapka poora naam aur account number likha hai.',
      },
      {
        textEn: 'The message creates urgency and asks for a password or OTP.',
        textHi: 'Message urgency create karta hai aur password ya OTP maangta hai.',
      },
      {
        textEn: 'The message is from an email address you recognise from previous legitimate emails.',
        textHi: 'Message ek aise email address se hai jo aapne pehle legitimate emails mein dekha hai.',
      },
      {
        textEn: 'The message contains a link to the company\'s official homepage only.',
        textHi: 'Message mein sirf company ke official homepage ka link hai.',
      },
    ],
    correctIndex: 1,
    explanationEn:
      'Creating a false sense of urgency ("act now or lose access") combined with a request for a password or OTP is the hallmark of phishing. Note that attackers can spoof familiar sender names too, so urgency + credential request is always a red flag.',
    explanationHi:
      'Fake urgency ("abhi act karo nahi toh access kho jaoge") ke saath password ya OTP ki maang phishing ki pehchaan hai. Dhyan rakhein ki attackers familiar sender names bhi spoof kar sakte hain.',
  },

  // ── Suspicious links ────────────────────────────────────────────────────────
  {
    id: 'q-links-1',
    lessonId: 'suspicious-links',
    questionEn:
      'A WhatsApp message links to "http://sbi-net-banking-update.xyz/login". What is most suspicious about this URL?',
    questionHi:
      'Ek WhatsApp message "http://sbi-net-banking-update.xyz/login" par link karta hai. Is URL mein sabse suspicious kya hai?',
    options: [
      {
        textEn: 'It uses HTTP instead of HTTPS.',
        textHi: 'Yeh HTTPS ki jagah HTTP use karta hai.',
      },
      {
        textEn: 'The domain is "sbi-net-banking-update.xyz", not the official "sbi.co.in".',
        textHi: 'Domain "sbi-net-banking-update.xyz" hai, official "sbi.co.in" nahi.',
      },
      {
        textEn: 'It came via WhatsApp instead of email.',
        textHi: 'Yeh email ki bajaye WhatsApp par aaya.',
      },
      {
        textEn: 'The path contains the word "login".',
        textHi: 'Path mein "login" word hai.',
      },
    ],
    correctIndex: 1,
    explanationEn:
      'The domain is the most important part of a URL. "sbi-net-banking-update.xyz" is not SBI\'s official domain (sbi.co.in). Attackers put "sbi" in the subdomain or path to deceive — always look at the domain only.',
    explanationHi:
      'Domain URL ka sabse important hissa hai. "sbi-net-banking-update.xyz" SBI ka official domain (sbi.co.in) nahi hai. Attackers "sbi" ko subdomain ya path mein daalte hain dhoka dene ke liye — hamesha sirf domain dekho.',
  },
  {
    id: 'q-links-2',
    lessonId: 'suspicious-links',
    questionEn: 'A padlock icon (🔒) and "https://" in the address bar means:',
    questionHi: 'Address bar mein padlock icon (🔒) aur "https://" ka matlab hai:',
    options: [
      {
        textEn: 'The website is safe and trustworthy.',
        textHi: 'Website safe aur trustworthy hai.',
      },
      {
        textEn: 'The connection between your browser and the website is encrypted.',
        textHi: 'Aapke browser aur website ke beech connection encrypted hai.',
      },
      {
        textEn: 'The website has been verified by the government.',
        textHi: 'Website government ne verify ki hai.',
      },
      {
        textEn: 'Your personal data cannot be stolen from this website.',
        textHi: 'Is website se aapka personal data nahi churaaya ja sakta.',
      },
    ],
    correctIndex: 1,
    explanationEn:
      'HTTPS only encrypts the connection — it does not verify who owns the website. Phishing sites frequently use HTTPS. Always check the domain, not just the padlock.',
    explanationHi:
      'HTTPS sirf connection encrypt karta hai — yeh website ke maalik ko verify nahi karta. Phishing sites bhi aksar HTTPS use karti hain. Hamesha domain check karein, sirf padlock nahi.',
  },

  // ── Job scams ───────────────────────────────────────────────────────────────
  {
    id: 'q-job-1',
    lessonId: 'job-scams',
    questionEn:
      'You receive a WhatsApp message offering a ₹50,000/month work-from-home internship with no experience needed. They ask for a ₹500 "registration fee." What should you do?',
    questionHi:
      'Aapko WhatsApp par ek message aata hai jo ₹50,000/month work-from-home internship offer karta hai, bina kisi experience ke. Woh ₹500 "registration fee" maangte hain. Aap kya karenge?',
    options: [
      {
        textEn: 'Pay the fee — it is only ₹500 and could be worth it.',
        textHi: 'Fee de do — sirf ₹500 hai aur worth it ho sakti hai.',
      },
      {
        textEn: 'Verify the company name on LinkedIn and MCA website; never pay a fee to get a job.',
        textHi: 'LinkedIn aur MCA website par company name verify karein; job pane ke liye kabhi fee mat do.',
      },
      {
        textEn: 'Ask for the company\'s GST number before paying.',
        textHi: 'Pay karne se pehle company ka GST number maangein.',
      },
      {
        textEn: 'Accept the offer verbally and pay only after the first salary.',
        textHi: 'Offer verbally accept karein aur pehli salary ke baad hi pay karein.',
      },
    ],
    correctIndex: 1,
    explanationEn:
      'No legitimate employer charges fees for joining. High pay, no experience required, WFH, and an upfront fee are classic scam signals. Always research independently before engaging.',
    explanationHi:
      'Koi bhi legitimate employer joining ke liye fees nahi lega. High pay, no experience, WFH, aur upfront fee — yeh sab classic scam signals hain. Involve hone se pehle hamesha independently research karein.',
  },
  {
    id: 'q-job-2',
    lessonId: 'job-scams',
    questionEn: 'Which action best protects you when evaluating an unsolicited job offer?',
    questionHi: 'Unsolicited job offer evaluate karte waqt kaun sa action sabse zyada protect karta hai?',
    options: [
      {
        textEn: 'Reply to the message and request more details.',
        textHi: 'Message ka reply karein aur zyada details maangein.',
      },
      {
        textEn: 'Search for the company name independently and call only official contact numbers.',
        textHi: 'Company ka naam independently search karein aur sirf official contact numbers par call karein.',
      },
      {
        textEn: 'Accept only if the offer letter has a company letterhead.',
        textHi: 'Sirf tabhi accept karein jab offer letter par company letterhead ho.',
      },
      {
        textEn: 'Check if the person who sent the message has a LinkedIn profile.',
        textHi: 'Dekho kya message bhejne wale ka LinkedIn profile hai.',
      },
    ],
    correctIndex: 1,
    explanationEn:
      'Searching independently and calling official numbers (found via official websites, not the message) is the safest approach. Offer letters, letterheads, and LinkedIn profiles can all be faked.',
    explanationHi:
      'Independently search karna aur official numbers par call karna (official website se, message se nahi) sabse safe tarika hai. Offer letters, letterheads, aur LinkedIn profiles sab fake ho sakte hain.',
  },

  // ── Scholarship / payment scams ────────────────────────────────────────────
  {
    id: 'q-scholarship-1',
    lessonId: 'scholarship-scams',
    questionEn: 'You get a message: "Scan this QR code to receive your ₹10,000 scholarship." What happens if you scan a payment QR code?',
    questionHi: 'Aapko message aata hai: "₹10,000 scholarship receive karne ke liye yeh QR code scan karein." Agar aap payment QR code scan karein toh kya hoga?',
    options: [
      {
        textEn: 'Money is deposited into your account.',
        textHi: 'Paisa aapke account mein aata hai.',
      },
      {
        textEn: 'Money is sent OUT of your account to the scammer.',
        textHi: 'Paisa aapke account se scammer ke paas JAATA hai.',
      },
      {
        textEn: 'Nothing happens — QR codes cannot transfer money.',
        textHi: 'Kuch nahi hota — QR codes paisa transfer nahi kar sakte.',
      },
      {
        textEn: 'Your bank verifies the scholarship and processes the payment.',
        textHi: 'Aapka bank scholarship verify karta hai aur payment process karta hai.',
      },
    ],
    correctIndex: 1,
    explanationEn:
      'Payment QR codes initiate an outgoing payment — they never receive money. You should never need to scan a QR code or share your UPI PIN to receive funds.',
    explanationHi:
      'Payment QR codes outgoing payment shuru karte hain — yeh paisa kabhi receive nahi karte. Paisa receive karne ke liye kabhi QR code scan karne ya UPI PIN share karne ki zaroorat nahi hoti.',
  },
  {
    id: 'q-scholarship-2',
    lessonId: 'scholarship-scams',
    questionEn: 'A message claims you have won a National Scholarship Portal (NSP) scholarship, asking you to pay ₹200 GST to release the funds. What is this?',
    questionHi: 'Ek message claim karta hai ki aapne National Scholarship Portal (NSP) scholarship jeeti hai, aur fund release karne ke liye ₹200 GST maangta hai. Yeh kya hai?',
    options: [
      {
        textEn: 'A legitimate government process — GST on scholarships is normal.',
        textHi: 'Ek legitimate government process — scholarship par GST normal hai.',
      },
      {
        textEn: 'An advance-fee scam — no real scholarship charges a fee for release.',
        textHi: 'Ek advance-fee scam — koi bhi real scholarship release ke liye fee nahi leti.',
      },
      {
        textEn: 'A test to see if you are eligible for the scholarship.',
        textHi: 'Ek test hai ki aap scholarship ke liye eligible hain ya nahi.',
      },
      {
        textEn: 'Safe only if the message came from an official government email.',
        textHi: 'Safe hai sirf agar message official government email se aaya ho.',
      },
    ],
    correctIndex: 1,
    explanationEn:
      'Legitimate scholarships never ask for advance payments to release funds. This is a textbook advance-fee fraud. Verify at scholarships.gov.in directly, not through any link from the message.',
    explanationHi:
      'Legitimate scholarships kabhi fund release ke liye advance payment nahi maangti. Yeh classic advance-fee fraud hai. scholarships.gov.in par directly verify karein, message ke kisi bhi link se nahi.',
  },

  // ── Password and OTP safety ─────────────────────────────────────────────────
  {
    id: 'q-otp-1',
    lessonId: 'password-otp',
    questionEn:
      'A caller says they are from your bank and need your OTP to "complete a security upgrade." What should you do?',
    questionHi:
      'Ek caller kehta hai woh aapke bank se hai aur "security upgrade complete karne" ke liye OTP chahiye. Aap kya karenge?',
    options: [
      {
        textEn: 'Share the OTP since the caller knows your account details.',
        textHi: 'OTP share karein kyunki caller ko aapke account details pata hain.',
      },
      {
        textEn: 'Hang up. Banks never ask for OTPs on calls.',
        textHi: 'Phone rakh dein. Banks kabhi call par OTP nahi maangte.',
      },
      {
        textEn: 'Ask the caller to hold while you note down the OTP first.',
        textHi: 'Caller ko hold par rakhein aur pehle OTP note kar lein.',
      },
      {
        textEn: 'Share only the first two digits of the OTP as a verification.',
        textHi: 'Sirf OTP ke pehle do digits share karein verification ke liye.',
      },
    ],
    correctIndex: 1,
    explanationEn:
      'Your bank will NEVER call you to ask for an OTP, PIN, or password. If someone on the phone asks for your OTP — no matter what reason they give — it is a social-engineering attack. Hang up and call the official bank helpline if you are concerned.',
    explanationHi:
      'Aapka bank aapko kabhi OTP, PIN, ya password ke liye call nahi karega. Agar phone par koi aapka OTP maange — chahe jo bhi reason bataye — yeh social engineering attack hai. Phone rakhein aur concerned hone par official bank helpline par call karein.',
  },
  {
    id: 'q-otp-2',
    lessonId: 'password-otp',
    questionEn: 'Which password is strongest?',
    questionHi: 'Kaun sa password sabse strong hai?',
    options: [
      {
        textEn: 'password123',
        textHi: 'password123',
      },
      {
        textEn: 'Rahul@1999',
        textHi: 'Rahul@1999',
      },
      {
        textEn: 'Tr0pical$Mango!Beach42',
        textHi: 'Tr0pical$Mango!Beach42',
      },
      {
        textEn: 'admin',
        textHi: 'admin',
      },
    ],
    correctIndex: 2,
    explanationEn:
      'A long passphrase with mixed case, numbers, and symbols that does not contain your name or birth year is the strongest choice. "password123" and "admin" are among the most commonly cracked. Using your name/year ("Rahul@1999") is guessable by anyone who knows basic details about you.',
    explanationHi:
      'Mixed case, numbers, aur symbols ke saath ek lamba passphrase jo aapka naam ya birth year contain na kare — yahi sabse strong option hai. "password123" aur "admin" sabse zyada crack hone wale passwords mein se hain. Naam/year wale passwords ("Rahul@1999") easily guessable hain.',
  },

  // ── Verify sources ──────────────────────────────────────────────────────────
  {
    id: 'q-verify-1',
    lessonId: 'verify-sources',
    questionEn:
      'You receive a WhatsApp message with a "click here to apply" link for a government scheme. What is the safest way to apply?',
    questionHi:
      'Aapko WhatsApp par ek government scheme ke liye "yahan click karein apply karein" link wala message aata hai. Apply karne ka sabse safe tarika kya hai?',
    options: [
      {
        textEn: 'Click the link — it looks official.',
        textHi: 'Link click karein — official lagta hai.',
      },
      {
        textEn: 'Forward the link to family members so more people can benefit.',
        textHi: 'Link family members ko forward karein taaki zyada log benefit kar sakein.',
      },
      {
        textEn: 'Type the official government website address in your browser yourself and apply from there.',
        textHi: 'Browser mein official government website address khud type karein aur wahan se apply karein.',
      },
      {
        textEn: 'Apply only if the message has been sent by five or more contacts.',
        textHi: 'Sirf tabhi apply karein jab yeh message paanch ya zyada contacts ne bheja ho.',
      },
    ],
    correctIndex: 2,
    explanationEn:
      'Always navigate to official government websites by typing the URL yourself. Viral WhatsApp messages cannot be trusted to contain correct links — even well-intentioned shares may carry altered or phishing links.',
    explanationHi:
      'Hamesha official government websites par URL khud type karke navigate karein. Viral WhatsApp messages par correct links hone ka bharosa nahi kiya ja sakta — well-intentioned shares mein bhi altered ya phishing links ho sakte hain.',
  },

  // ── After incident ──────────────────────────────────────────────────────────
  {
    id: 'q-incident-1',
    lessonId: 'after-incident',
    questionEn: 'You accidentally clicked a suspicious link and entered your email password. What is the FIRST thing you should do?',
    questionHi: 'Aapne galti se ek suspicious link click kiya aur apna email password enter kar diya. Aapko SABSE PEHLE kya karna chahiye?',
    options: [
      {
        textEn: 'Wait to see if anything unusual happens before acting.',
        textHi: 'Pehle dekho kuch unusual hota hai ya nahi, phir action lena.',
      },
      {
        textEn: 'Change your email password immediately from a different, trusted device.',
        textHi: 'Kisi aur trusted device se turant apna email password badlein.',
      },
      {
        textEn: 'Uninstall your browser.',
        textHi: 'Apna browser uninstall kar lo.',
      },
      {
        textEn: 'Factory reset your phone before doing anything else.',
        textHi: 'Pehle phone factory reset karo.',
      },
    ],
    correctIndex: 1,
    explanationEn:
      'Time is critical. Change the compromised password immediately, then check for any suspicious logins, and enable 2FA if not already on. Your email account controls password resets for everything else — secure it first.',
    explanationHi:
      'Waqt bahut important hai. Compromised password turant badlein, phir suspicious logins check karein aur agar 2FA nahi lagi hai toh enable karein. Email account baaki sab ke password reset control karta hai — pehle use secure karein.',
  },
  {
    id: 'q-incident-2',
    lessonId: 'after-incident',
    questionEn: 'You shared your Aadhaar and PAN card details with what turned out to be a fake job portal. What should you do?',
    questionHi: 'Aapne apna Aadhaar aur PAN card details ek fake job portal ke saath share kar diya jo nikla. Aapko kya karna chahiye?',
    options: [
      {
        textEn: 'Nothing — these are public documents anyway.',
        textHi: 'Kuch nahi — yeh toh public documents hain.',
      },
      {
        textEn: 'File a complaint at cybercrime.gov.in, alert your bank, and monitor your credit report.',
        textHi: 'cybercrime.gov.in par complaint darj karein, bank ko alert karein, aur apna credit report monitor karein.',
      },
      {
        textEn: 'Change your Aadhaar number immediately.',
        textHi: 'Turant apna Aadhaar number badlein.',
      },
      {
        textEn: 'Delete your social media profiles.',
        textHi: 'Apne social media profiles delete karein.',
      },
    ],
    correctIndex: 1,
    explanationEn:
      'Identity documents can be used for financial fraud. Report to cybercrime.gov.in (or call 1930), alert your bank about potential misuse, and consider placing a credit-lock request. Aadhaar numbers cannot be changed but you can lock your Aadhaar biometrics at uidai.gov.in.',
    explanationHi:
      'Identity documents financial fraud ke liye use ho sakte hain. cybercrime.gov.in par report karein (ya 1930 par call karein), bank ko potential misuse ke baare mein alert karein, aur credit-lock request consider karein. Aadhaar number nahi badla ja sakta lekin aap uidai.gov.in par apne Aadhaar biometrics lock kar sakte hain.',
  },
];

// ─── Integrity check (runtime) ────────────────────────────────────────────────
// This runs once when the module is imported (dev + production) and throws
// loudly if the data is structurally broken.  It does NOT check semantic
// correctness of answers — that requires human review (see the consistency
// check script).

function assertQuizIntegrity(questions: QuizQuestion[]): void {
  const ids = new Set<string>();
  for (const q of questions) {
    if (ids.has(q.id)) {
      throw new Error(`[quiz] Duplicate question id: "${q.id}"`);
    }
    ids.add(q.id);

    if (q.options.length < 2) {
      throw new Error(`[quiz] Question "${q.id}" has fewer than 2 options.`);
    }
    if (q.correctIndex < 0 || q.correctIndex >= q.options.length) {
      throw new Error(
        `[quiz] Question "${q.id}" correctIndex (${q.correctIndex}) is out of range (0–${q.options.length - 1}).`
      );
    }
    for (let i = 0; i < q.options.length; i++) {
      const opt = q.options[i];
      if (!opt.textEn.trim()) {
        throw new Error(`[quiz] Question "${q.id}" option[${i}].textEn is empty.`);
      }
      if (!opt.textHi.trim()) {
        throw new Error(`[quiz] Question "${q.id}" option[${i}].textHi is empty.`);
      }
    }
    if (!q.explanationEn.trim()) {
      throw new Error(`[quiz] Question "${q.id}" explanationEn is empty.`);
    }
    if (!q.explanationHi.trim()) {
      throw new Error(`[quiz] Question "${q.id}" explanationHi is empty.`);
    }
  }
}

// Runs immediately at import time — any data error surfaces as a thrown Error.
assertQuizIntegrity(QUIZ_QUESTIONS);
