import type { ModuleGuideProps } from "./ModuleGuide";

/** Shared beginner copy for each screen — keep jargon low, define terms inline. */
export const GUIDES: Record<string, ModuleGuideProps> = {
  dashboard: {
    title: "Dashboard",
    plainEnglish:
      "This is the scoreboard. It shows how many patients, visits, insurance cards, document scans, bills, and eligibility checks are in the practice system right now.",
    whyItMatters:
      "Hospital billing teams glance here first to see if work is flowing. If numbers are zero, start the walkthrough and load demo data.",
    howItWorks:
      "Numbers come from the practice database after you sync patients or run eligibility / OCR / claims demos.",
    nextStep: {
      href: "/walkthrough",
      label: "Open the full walkthrough",
      reason: "Best place to start if you are new.",
    },
    terms: [
      {
        term: "RCM",
        meaning:
          "Revenue Cycle Management — the whole path from a patient visit to getting paid by insurance.",
      },
      {
        term: "Eligibility",
        meaning:
          "Checking whether a patient’s insurance is active and will cover a visit on a certain date.",
      },
    ],
    mockNote:
      "All counts here are from synthetic demo data, not real patients or real insurance.",
    demoTip:
      "You should see about 3 patients, 3 visits, 3 insurance policies, 4 documents, and 3 claims after seeding.",
  },
  patients: {
    title: "Patients",
    plainEnglish:
      "A patient is a person who receives care. This screen is the clinic’s list of people (name, date of birth, phone, city).",
    whyItMatters:
      "Almost everything else hangs off a patient: visits, insurance, bills, and eligibility checks.",
    howItWorks:
      "Use “Sync Mock FHIR” to pull pretend hospital records into this app. Click Open to see one person’s chart.",
    nextStep: {
      href: "/encounters",
      label: "Go to Encounters (visits)",
      reason: "Next we look at appointments and visits.",
    },
    terms: [
      {
        term: "FHIR",
        meaning:
          "A common “language” hospitals use to share medical data (like a shared spreadsheet format for health records).",
      },
      {
        term: "EHR",
        meaning:
          "Electronic Health Record — the hospital’s main charting system (Epic, Oracle, etc.). We pretend with mock FHIR.",
      },
    ],
    mockNote:
      "Names like Ava Chen are fake. Choose Mock Epic or Mock Oracle Health — not live EHR credentials.",
    demoTip:
      "Select Mock Epic → Sync EHR → Postgres, then open Ava Chen (epic-mock-pat-ava).",
  },
  encounters: {
    title: "Encounters (visits)",
    plainEnglish:
      "An encounter is one visit — office visit, ER trip, telehealth call. It has a date and a reason.",
    whyItMatters:
      "Insurance coverage is checked for a visit date. Bills (claims) are also tied to visits.",
    howItWorks:
      "Browse the list, then open the patient to see visits on their chart.",
    nextStep: {
      href: "/insurance",
      label: "Go to Insurance",
      reason: "Next we look at the insurance card on file.",
    },
    terms: [
      {
        term: "Encounter",
        meaning: "Healthcare word for “this visit” or “this episode of care.”",
      },
    ],
    mockNote: "Visit dates and reasons are synthetic demo records.",
    demoTip: "Notice visits linked back to patients — Ava’s MRI story starts from a visit date.",
  },
  insurance: {
    title: "Insurance policies",
    plainEnglish:
      "This is the insurance card information stored for a patient: which company (payer), member ID, and when coverage starts/ends.",
    whyItMatters:
      "Without correct insurance info, the clinic cannot check eligibility or send a bill that gets paid.",
    howItWorks:
      "Policies appear after mock FHIR “Coverage” sync. Click Open to jump to the patient.",
    nextStep: {
      href: "/payers",
      label: "Go to Payers",
      reason: "See the insurance companies themselves.",
    },
    terms: [
      {
        term: "Member ID",
        meaning: "The ID printed on the insurance card that identifies the covered person.",
      },
      {
        term: "Coverage dates",
        meaning: "The start and end of when the plan is active.",
      },
    ],
    mockNote: "Payers and member IDs are fake (for example MEM-AVA-1001).",
    demoTip: "Find Ava’s Acme Health policy — you will use it on the Eligibility screen.",
  },
  payers: {
    title: "Payers",
    plainEnglish:
      "A payer is the insurance company that pays claims (Acme Health, Blue Ridge Mutual, etc.).",
    whyItMatters:
      "Clinics map internal payer names to external codes so bills go to the right company.",
    howItWorks:
      "Review the list and the “mappings” that connect our codes to outside codes.",
    nextStep: {
      href: "/eligibility",
      label: "Go to Eligibility",
      reason: "Ask: “Is this patient covered on this date?”",
    },
    terms: [
      {
        term: "Payer mapping",
        meaning:
          "A translation between our internal insurance company ID and an outside system’s ID.",
      },
    ],
    mockNote: "These are synthetic payers created for learning — not real insurers.",
    demoTip: "Acme Health Insurance is the payer on Ava’s denied MRI claim.",
  },
  eligibility: {
    title: "Eligibility verification",
    plainEnglish:
      "Before (or after) a visit, the clinic asks the insurance company: “Is this member’s plan active on this date, and what might they owe?”",
    whyItMatters:
      "Catching inactive coverage early avoids surprise bills and wasted claim work.",
    howItWorks:
      "Pick a patient, their insurance policy, a service date, and a practice scenario (ACTIVE, INACTIVE, …). Then run the check.",
    nextStep: {
      href: "/documents",
      label: "Go to Documents",
      reason: "Next we “read” paper forms with OCR.",
    },
    terms: [
      {
        term: "Copay",
        meaning: "Fixed amount the patient pays for a visit (for example $30).",
      },
      {
        term: "Deductible",
        meaning:
          "Amount the patient must pay out of pocket each year before insurance pays more.",
      },
      {
        term: "Scenario",
        meaning:
          "In this demo, a practice switch so you can see ACTIVE vs DENIED-style answers without calling a real insurer.",
      },
    ],
    mockNote:
      "Verification goes through MOCK AVAILITY (simulated 270/271). Not live Availity or real payer credentials.",
    demoTip:
      "Choose Ava Chen + Acme policy + ACTIVE → Verify via Mock Availity. Expect AVAIL-ACME-001 + transaction ID.",
  },
  documents: {
    title: "Documents & OCR",
    plainEnglish:
      "Clinics still get paper or PDFs: insurance cards, EOBs, visit notes. OCR (optical character recognition) is software that reads those pages and pulls out useful fields.",
    whyItMatters:
      "Typing member IDs and denial codes by hand is slow and error-prone. Extraction speeds up billing work.",
    howItWorks:
      "Pick a document type and click Extract. The mock “Azure Document Intelligence” returns structured fields.",
    nextStep: {
      href: "/policy",
      label: "Go to Policy Copilot",
      reason: "Look up coverage rules that support an appeal.",
    },
    terms: [
      {
        term: "OCR",
        meaning: "Computer reading of text from an image or PDF.",
      },
      {
        term: "EOB",
        meaning:
          "Explanation of Benefits — the insurer’s letter saying what they paid, what you owe, or why they denied.",
      },
      {
        term: "Azure Document Intelligence",
        meaning:
          "Microsoft’s cloud OCR product. This app uses a mock version so you need no Azure account.",
      },
    ],
    mockNote:
      "No real Azure credentials. Extraction uses templates that look like Azure results.",
    demoTip:
      "Extract an EOB — you should see denial code CO-50, which shows up again on Claims.",
  },
  policy: {
    title: "Policy Copilot (RAG)",
    plainEnglish:
      "When insurance denies a bill, staff look up coverage rules (Medicare NCDs/LCDs, plan policies). This copilot searches a small library of pretend rules and answers with citations.",
    whyItMatters:
      "Good appeals quote the rule that says the service should be covered — not just “please pay us.”",
    howItWorks:
      "Ask a plain question. The app finds the closest policy pages (RAG) and summarizes them with scores.",
    nextStep: {
      href: "/claims",
      label: "Go to Claims",
      reason: "See Ava’s denied MRI bill and draft an appeal.",
    },
    terms: [
      {
        term: "RAG",
        meaning:
          "Retrieval-Augmented Generation — find relevant documents first, then answer using those documents (like open-book quiz).",
      },
      {
        term: "Vector database",
        meaning:
          "A searchable shelf of text pieces scored by similarity. Ours is a tiny local version — no paid AI key required.",
      },
      {
        term: "CMS",
        meaning:
          "Centers for Medicare & Medicaid Services — U.S. agency that publishes many coverage rules. Our text is synthetic, not from CMS.gov.",
      },
    ],
    mockNote:
      "Policy pages are synthetic learning text — not official CMS publications.",
    demoTip:
      "Ask: “When is MRI for low back pain covered?” then keep that idea for the appeal letter.",
  },
  claims: {
    title: "Claims, denials & appeals",
    plainEnglish:
      "A claim is the bill sent to insurance. A denial means “we will not pay.” An appeal is a formal request to reconsider, often with clinical notes and policy citations.",
    whyItMatters:
      "This is where clinics recover revenue after a “no.” Understanding denials is core RCM work.",
    howItWorks:
      "Review demo claims. On Ava’s denied MRI claim, click Draft AI appeal to generate a letter that uses the Policy Copilot.",
    nextStep: {
      href: "/assistant",
      label: "Go to Capstone AI",
      reason: "Ask one question that pulls the whole story together.",
    },
    terms: [
      {
        term: "Claim",
        meaning: "The bill (with procedure and diagnosis codes) sent to the payer.",
      },
      {
        term: "Denial / CARC",
        meaning:
          "Reason code from the payer. Example CO-50 ≈ “not medically necessary.”",
      },
      {
        term: "Appeal",
        meaning: "A written challenge asking the payer to reverse a denial.",
      },
      {
        term: "CPT / ICD-10",
        meaning:
          "CPT = procedure codes (what was done). ICD-10 = diagnosis codes (why).",
      },
    ],
    mockNote:
      "Claims, denial codes, and AI letters are demo-only. No real clearinghouse.",
    demoTip:
      "Find CLM-2026-1001 (denied). Draft AI appeal and read the letter — it cites synthetic policies.",
  },
  assistant: {
    title: "Capstone AI assistant",
    plainEnglish:
      "This is the “glue” chat. It peeks at patients, eligibility, scanned documents, claims/denials, and policy search, then answers in one place.",
    whyItMatters:
      "Real RCM tools aim to reduce tab-hopping. Capstone shows how AI can sit on top of many modules.",
    howItWorks:
      "Ask about Ava’s MRI denial. Watch which modules were used in the reply.",
    nextStep: {
      href: "/history",
      label: "Go to History",
      reason: "See a log of eligibility checks you ran.",
    },
    terms: [
      {
        term: "Capstone",
        meaning:
          "A final project that combines earlier skills — here: FHIR + OCR + RAG + claims + AI.",
      },
    ],
    mockNote:
      "The assistant only sees local demo data and synthetic policies. Not clinical or legal advice.",
    demoTip:
      "Try: “Why was Ava's MRI claim denied and what policy supports an appeal?”",
  },
  history: {
    title: "Eligibility history",
    plainEnglish:
      "A diary of eligibility checks — who was checked, which scenario, and what status came back.",
    whyItMatters:
      "Audits and patient billing disputes need a trail of “what did we know, and when?”",
    howItWorks:
      "Run a few checks on Eligibility, then return here to see the log fill in.",
    nextStep: {
      href: "/walkthrough",
      label: "Replay the walkthrough",
      reason: "Review the full story anytime.",
    },
    terms: [
      {
        term: "Audit trail",
        meaning: "A trustworthy history of actions for compliance and learning.",
      },
    ],
    mockNote: "Only mock eligibility checks appear here.",
    demoTip:
      "If this list is empty, go to Eligibility, run ACTIVE for Ava, then refresh.",
  },
};
