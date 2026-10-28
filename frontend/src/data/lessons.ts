/**
 * CyberSaathi AI — Locally bundled educational lesson content for T-05.
 *
 * No external API is used. All content is static and shipped with the app.
 * Each lesson has bilingual (English + Hinglish) text so both language
 * preferences are served without a network call.
 *
 * Lesson IDs must be unique strings used as React keys and for navigation.
 */

export interface LessonStep {
  /** Short bold heading */
  headingEn: string;
  headingHi: string;
  /** Paragraph body — 2–4 sentences */
  bodyEn: string;
  bodyHi: string;
}

export interface Lesson {
  id: string;
  /** Tab/card title */
  titleEn: string;
  titleHi: string;
  /** One-line description shown in the lesson list */
  summaryEn: string;
  summaryHi: string;
  /** Visual indicator icon (emoji-safe, aria-hidden) */
  icon: string;
  steps: LessonStep[];
}

export const LESSONS: Lesson[] = [
  // ── 1. Phishing basics ─────────────────────────────────────────────────────
  {
    id: 'phishing-basics',
    titleEn: 'What is Phishing?',
    titleHi: 'Phishing kya hota hai?',
    summaryEn: 'Understand how attackers impersonate trusted sources to steal information.',
    summaryHi: 'Samjhein kaise attackers trusted sources ki nakal utarte hain.',
    icon: '🎣',
    steps: [
      {
        headingEn: 'The core trick',
        headingHi: 'Yeh kaam kaise karta hai',
        bodyEn:
          'Phishing is when someone pretends to be a trusted person or organisation — a bank, college, company, or government department — to trick you into giving them your password, OTP, or personal details.',
        bodyHi:
          'Phishing tab hota hai jab koi kisi trusted person ya organisation — bank, college, company, ya government — ki nakal utarke aapse password, OTP, ya personal details mangta hai.',
      },
      {
        headingEn: 'How it arrives',
        headingHi: 'Kaise aata hai',
        bodyEn:
          'Phishing attempts come through email, SMS (called smishing), WhatsApp, social media DMs, or fake phone calls (called vishing). The message usually creates urgency: "Your account will be blocked!" or "Claim your prize now!"',
        bodyHi:
          'Phishing email, SMS (smishing), WhatsApp, social media DM, ya fake phone calls (vishing) ke zariye aata hai. Message mein aksar urgency hoti hai: "Aapka account band ho jayega!" ya "Abhi apna prize claim karein!"',
      },
      {
        headingEn: 'Why it works',
        headingHi: 'Yeh kyun kaam karta hai',
        bodyEn:
          'Attackers use official logos, realistic email addresses, and convincing language. They count on you acting quickly before you have time to think. Slowing down is your best defence.',
        bodyHi:
          'Attackers official logos, realistic email addresses, aur convincing language use karte hain. Woh chahte hain aap sochne se pehle hi act karein. Ruk jaana aapki sabse badi raksha hai.',
      },
      {
        headingEn: 'Red flags to look for',
        headingHi: 'Dhyan dene wali baatein',
        bodyEn:
          'Unexpected requests for passwords or OTPs, generic greetings ("Dear User"), grammar mistakes, urgent deadlines, and links that do not match the real domain are all warning signs.',
        bodyHi:
          'Password ya OTP ki unexpected maang, generic greetings ("Dear User"), grammar mistakes, urgent deadlines, aur aisi links jo real domain se match nahi karti — yeh sab warning signs hain.',
      },
    ],
  },

  // ── 2. Suspicious links ────────────────────────────────────────────────────
  {
    id: 'suspicious-links',
    titleEn: 'How to Spot Suspicious Links',
    titleHi: 'Suspicious Links Kaise Pahchanein',
    summaryEn: 'Learn to read a URL carefully before clicking anything.',
    summaryHi: 'Kisi bhi link par click karne se pehle URL dhyan se padhna seekhein.',
    icon: '🔗',
    steps: [
      {
        headingEn: 'Read the domain, not the display text',
        headingHi: 'Display text nahi, domain padhein',
        bodyEn:
          'The visible text of a link can say "www.sbi.co.in" but the actual URL can be completely different. Always hover over a link (on desktop) or long-press (on mobile) to see the real address before clicking.',
        bodyHi:
          'Link ka visible text "www.sbi.co.in" bol sakta hai lekin actual URL bilkul alag ho sakta hai. Click karne se pehle hamesha hover ya long-press karke real address dekh lein.',
      },
      {
        headingEn: 'Look for lookalike domains',
        headingHi: 'Lookalike domains dhundein',
        bodyEn:
          'Attackers register domains that look almost right: "sbi-onIine.com" (capital I instead of l), "g00gle.com" (zeros instead of O), or "amazon-india-offers.com". The real domain is just the part before the first single slash.',
        bodyHi:
          'Attackers almost-correct-looking domains register karte hain: "sbi-onIine.com" (l ki jagah capital I), "g00gle.com" (O ki jagah zero), ya "amazon-india-offers.com". Real domain woh hai jo pehli single slash se pehle aata hai.',
      },
      {
        headingEn: 'URL shorteners hide the destination',
        headingHi: 'URL shorteners destination chhupate hain',
        bodyEn:
          'Services like bit.ly, tinyurl.com, or t.co shorten links so you cannot see where they go. If you receive a shortened link from an unknown sender, do not click it. Expand it using a URL preview tool first.',
        bodyHi:
          'bit.ly, tinyurl.com, ya t.co jaise services links ko shorten karte hain taaki destination na dikhein. Agar kisi unknown sender se shortened link mila ho toh click mat karein.',
      },
      {
        headingEn: 'HTTPS is not proof of safety',
        headingHi: 'HTTPS ka matlab safe nahi hai',
        bodyEn:
          'A padlock icon or "https://" only means the connection is encrypted — it does not mean the website is legitimate. Phishing sites routinely use HTTPS. The domain is still what you need to check.',
        bodyHi:
          'Padlock icon ya "https://" sirf yeh batata hai ki connection encrypted hai — yeh website ke legitimate hone ki guarantee nahi hai. Phishing sites bhi regularly HTTPS use karti hain.',
      },
    ],
  },

  // ── 3. Internship / job scams ─────────────────────────────────────────────
  {
    id: 'job-scams',
    titleEn: 'Internship & Job Offer Scams',
    titleHi: 'Internship aur Job Offer Scams',
    summaryEn: 'Spot fake job and internship offers targeting college students.',
    summaryHi: 'College students ko target karne wale fake job/internship offers pahchanein.',
    icon: '💼',
    steps: [
      {
        headingEn: 'Too-good-to-be-true offers',
        headingHi: 'Zyada-acha-lagne-wale offers',
        bodyEn:
          'Scam offers promise very high pay for minimal work, no experience required, work-from-home, and instant joining. Legitimate companies follow a defined hiring process and do not make verbal or WhatsApp-only offers.',
        bodyHi:
          'Scam offers mein bahut zyada pay, minimal kaam, koi experience nahi chahiye, WFH, aur turant joining hota hai. Legitimate companies ek defined hiring process follow karti hain aur sirf WhatsApp par offers nahi deti.',
      },
      {
        headingEn: 'They ask for money',
        headingHi: 'Woh paise maangte hain',
        bodyEn:
          'A real employer never asks you to pay for training materials, registration fees, background checks, or a "refundable security deposit." If any payment is requested before or during onboarding, it is a scam.',
        bodyHi:
          'Ek real employer kabhi training materials, registration fees, background check, ya "refundable security deposit" ke liye paise nahi maangta. Agar onboarding se pehle ya dauraaan koi payment maangi jaye, yeh scam hai.',
      },
      {
        headingEn: 'Verify the company independently',
        headingHi: 'Company ko independently verify karein',
        bodyEn:
          'Search for the company name on Google, LinkedIn, and the Ministry of Corporate Affairs (MCA) website. Call the official phone number you find on those sources — not the number provided in the message.',
        bodyHi:
          'Google, LinkedIn, aur Ministry of Corporate Affairs (MCA) website par company ka naam search karein. Wahan mile official phone number par call karein — message mein diya number nahi.',
      },
      {
        headingEn: 'Fake offer letters and portals',
        headingHi: 'Fake offer letters aur portals',
        bodyEn:
          'Scammers send convincing-looking offer letters with company logos. They may also set up fake HR portals where you submit your Aadhaar, PAN, or bank details. Never submit sensitive documents to an unverified portal.',
        bodyHi:
          'Scammers company logos ke saath convincing offer letters bhejte hain. Woh fake HR portals bhi bana lete hain jahan aapka Aadhaar, PAN, ya bank details maangenge. Kabhi bhi unverified portal par sensitive documents submit mat karein.',
      },
    ],
  },

  // ── 4. Scholarship / payment scams ────────────────────────────────────────
  {
    id: 'scholarship-scams',
    titleEn: 'Scholarship & Payment Scams',
    titleHi: 'Scholarship aur Payment Scams',
    summaryEn: 'Recognise fake scholarship, prize, and advance-fee fraud.',
    summaryHi: 'Fake scholarship, prize, aur advance-fee fraud pahchanein.',
    icon: '🎓',
    steps: [
      {
        headingEn: 'You cannot win what you did not enter',
        headingHi: 'Jo enter nahi kiya woh nahi jeet sakte',
        bodyEn:
          'If a message says you have won a scholarship, lottery, or prize that you never applied for, it is almost certainly a scam. Legitimate scholarships require you to apply first and publish results publicly.',
        bodyHi:
          'Agar koi message bole ki aapne ek scholarship, lottery, ya prize jeeta hai jiske liye aapne apply hi nahi kiya tha, toh yeh almost pakka scam hai. Legitimate scholarships mein pehle apply karna padta hai.',
      },
      {
        headingEn: 'Processing fee / tax before release',
        headingHi: 'Release se pehle processing fee / tax',
        bodyEn:
          'A common variant asks you to pay a small "processing fee" or "GST" to release your scholarship money. This is a classic advance-fee fraud. Once you pay, they either disappear or keep asking for more.',
        bodyHi:
          'Ek common variant mein scholarship release karne ke liye chhota "processing fee" ya "GST" maangaa jaata hai. Yeh classic advance-fee fraud hai. Ek baar payment ke baad woh ya toh gayab ho jaate hain ya baar baar paisa maangte hain.',
      },
      {
        headingEn: 'Fake government / NGO impersonation',
        headingHi: 'Fake government / NGO impersonation',
        bodyEn:
          'Scammers claim to represent PM Scholarships, NSP, AICTE, or well-known NGOs. Always verify by visiting the official website directly (type the URL yourself; do not click a link from the message) or calling the official helpline.',
        bodyHi:
          'Scammers PM Scholarship, NSP, AICTE, ya well-known NGOs ka naam use karte hain. Hamesha official website par directly jaayein (URL khud type karein; message mein diya link mat click karein) ya official helpline par call karein.',
      },
      {
        headingEn: 'QR code and UPI scams',
        headingHi: 'QR code aur UPI scams',
        bodyEn:
          '"Scan this QR code to receive your scholarship" is a common trap. Scanning a payment QR code sends money out — it does not deposit money in. You should never need to scan a QR code or share a UPI PIN to receive money.',
        bodyHi:
          '"Scholarship receive karne ke liye yeh QR code scan karein" ek common trap hai. Payment QR scan karne se paisa jaata hai — aata nahi. Paisa receive karne ke liye aapko kabhi QR scan karne ya UPI PIN share karne ki zaroorat nahi hai.',
      },
    ],
  },

  // ── 5. Password and OTP safety ─────────────────────────────────────────────
  {
    id: 'password-otp',
    titleEn: 'Password & OTP Safety',
    titleHi: 'Password aur OTP Safety',
    summaryEn: 'Keep your accounts secure with strong passwords and safe OTP habits.',
    summaryHi: 'Strong passwords aur safe OTP habits se accounts surakshit rakhein.',
    icon: '🔑',
    steps: [
      {
        headingEn: 'Strong, unique passwords',
        headingHi: 'Strong, unique passwords',
        bodyEn:
          'Use a different password for every important account. A strong password is at least 12 characters long and mixes letters, numbers, and symbols. Use a password manager (like Bitwarden — free) rather than writing passwords down.',
        bodyHi:
          'Har important account ke liye alag password use karein. Strong password kam se kam 12 characters ka hota hai aur usme letters, numbers, aur symbols hote hain. Passwords likhne ki bajaye password manager (jaise Bitwarden — free) use karein.',
      },
      {
        headingEn: 'Enable two-factor authentication (2FA)',
        headingHi: '2FA enable karein',
        bodyEn:
          'Enable 2FA on your email, social media, and banking accounts. Even if an attacker steals your password, they still need the second factor (OTP or authentication app) to log in.',
        bodyHi:
          'Email, social media, aur banking accounts par 2FA enable karein. Agar attacker aapka password bhi chura le, toh bhi login karne ke liye second factor (OTP ya authentication app) chahiye hoga.',
      },
      {
        headingEn: 'Never share an OTP',
        headingHi: 'OTP kabhi share mat karein',
        bodyEn:
          'Banks, government services, and legitimate companies will NEVER ask you to read out your OTP over the phone. If someone asks for your OTP — even if they claim to be from your bank — hang up immediately.',
        bodyHi:
          'Banks, government services, aur legitimate companies KABHI phone par aapse OTP nahi maangti. Agar koi OTP maange — chahe woh apne aap ko bank ka representative bole — turant phone disconnect karein.',
      },
      {
        headingEn: 'Beware of SIM-swap and remote-access tricks',
        headingHi: 'SIM-swap aur remote-access tricks se bachein',
        bodyEn:
          'Do not install remote-access apps (AnyDesk, TeamViewer) for anyone who contacts you unsolicited. Do not share OTPs or PINs under any pretext. A SIM swap can happen if you share personal details; report unusual loss of mobile signal immediately.',
        bodyHi:
          'Kisi bhi unsolicited contact ke kehne par remote-access apps (AnyDesk, TeamViewer) install mat karein. Kisi bhi bahane se OTP ya PIN share mat karein. Agar achanak mobile signal band ho jaye toh turant report karein.',
      },
    ],
  },

  // ── 6. Official channel verification ──────────────────────────────────────
  {
    id: 'verify-sources',
    titleEn: 'Verify Through Official Channels',
    titleHi: 'Official Channels se Verify Karein',
    summaryEn: 'Always double-check offers and alerts using sources you find yourself.',
    summaryHi: 'Hamesha khud dhoondhe sources se offers aur alerts double-check karein.',
    icon: '✅',
    steps: [
      {
        headingEn: 'Go directly to the source',
        headingHi: 'Seedha source par jaayein',
        bodyEn:
          'Instead of clicking links in messages, open a browser and type the official website address yourself (e.g., sbi.co.in, nsp.gov.in). Bookmark official sites you use often.',
        bodyHi:
          'Messages mein links click karne ki bajaye browser mein official website address khud type karein (jaise sbi.co.in, nsp.gov.in). Aksar use ki jaane wali official sites bookmark kar lein.',
      },
      {
        headingEn: 'Call the official helpline',
        headingHi: 'Official helpline par call karein',
        bodyEn:
          'Find the customer-care number from the official website, not from a Google ad or the suspicious message. Confirm whether the offer, alert, or job is genuine before taking any action.',
        bodyHi:
          'Customer care number Google ad ya suspicious message se nahi, official website se lein. Koi bhi action lene se pehle confirm karein ki offer, alert, ya job genuine hai ya nahi.',
      },
      {
        headingEn: 'Cross-check using trusted news or official announcements',
        headingHi: 'Trusted news ya official announcements se cross-check karein',
        bodyEn:
          'If a message claims a scheme or policy has changed, verify it with a reputable news source or the relevant government portal. Scammers exploit news events to make their messages seem timely.',
        bodyHi:
          'Agar message bole ki koi scheme ya policy change hua hai toh reputable news source ya government portal se verify karein. Scammers news events ka fayda uthate hain apne messages ko timely dikhane ke liye.',
      },
      {
        headingEn: 'Legitimate organisations never demand secrecy',
        headingHi: 'Legitimate organisations kabhi secrecy nahi maangte',
        bodyEn:
          'If you are told "do not tell anyone about this offer" or "do not consult your parents/friends," that is a manipulation tactic. Real opportunities can be openly discussed and verified.',
        bodyHi:
          'Agar kaha jaye "is offer ke baare mein kisi ko mat batana" ya "apne parents/friends se mat poochho," toh yeh manipulation tactic hai. Real opportunities ko openly discuss aur verify kiya ja sakta hai.',
      },
    ],
  },

  // ── 7. After clicking a suspicious link / sharing info ────────────────────
  {
    id: 'after-incident',
    titleEn: 'What to Do After an Incident',
    titleHi: 'Incident ke Baad Kya Karein',
    summaryEn: 'Immediate steps if you clicked a bad link or shared sensitive information.',
    summaryHi: 'Agar aapne bad link click kiya ya sensitive info share ki toh turant kya karein.',
    icon: '🚨',
    steps: [
      {
        headingEn: 'Do not panic — act quickly',
        headingHi: 'Ghabrayein mat — jaldi action lein',
        bodyEn:
          'If you clicked a suspicious link, do not enter any credentials on the page that opened. Close the tab immediately. Take a screenshot for reference. Disconnect from Wi-Fi temporarily to limit any data sent.',
        bodyHi:
          'Agar aapne suspicious link click kiya toh jo page khula uspar koi credentials mat daalo. Tab turant band karein. Reference ke liye screenshot lein. Data transmission rokne ke liye Wi-Fi temporarily disconnect karein.',
      },
      {
        headingEn: 'Change your passwords immediately',
        headingHi: 'Turant passwords badlein',
        bodyEn:
          'Change the password of the affected account and any other account that shares that password. Start with your email account — it is the master key to everything else.',
        bodyHi:
          'Affected account aur jo bhi account usi password ka use karta hai, unke passwords turant badle. Pehle email account se shuru karein — yeh baki sab ka master key hai.',
      },
      {
        headingEn: 'If you shared financial details',
        headingHi: 'Agar aapne financial details share ki',
        bodyEn:
          'Call your bank immediately on the official helpline (not from the message). Ask them to block your card, reverse any unauthorised transactions, and place a temporary hold. File a complaint at cybercrime.gov.in or call 1930.',
        bodyHi:
          'Apne bank ke official helpline par turant call karein (message wale number par nahi). Card block karwayein, unauthorised transactions reverse karwayein. cybercrime.gov.in par complaint darj karein ya 1930 par call karein.',
      },
      {
        headingEn: 'Report and warn others',
        headingHi: 'Report karein aur doosron ko warn karein',
        bodyEn:
          'Report the scam number or message to your telecom provider (spam SMS can be forwarded to 1909). Share what happened with friends and family so they can avoid the same trap. You are not alone — reporting helps protect others.',
        bodyHi:
          'Scam number ya message ko apne telecom provider ko report karein (spam SMS 1909 par forward karein). Jo hua woh apne dosto aur family ko batayein taaki woh bhi bachein. Reporting karne se doosron ki bhi raksha hoti hai.',
      },
    ],
  },
];
