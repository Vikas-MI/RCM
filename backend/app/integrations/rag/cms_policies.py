"""Synthetic CMS-style policy snippets for learning RAG.

ELI5: These are pretend Medicare rule pages we keep in a shoebox so the
assistant can look them up. Not official CMS text.
"""

CMS_POLICY_CHUNKS: list[dict] = [
    {
        "id": "ncd-back-pain-mri",
        "title": "Synthetic NCD: MRI for Low Back Pain",
        "policy_id": "NCD-220.2-MOCK",
        "category": "imaging",
        "text": (
            "MRI of the lumbar spine may be considered medically necessary when the patient "
            "has low back pain lasting more than 6 weeks despite conservative therapy such as "
            "physical therapy, NSAIDs, or activity modification. Red-flag symptoms (cancer "
            "history, infection suspicion, progressive neurologic deficit, cauda equina) "
            "may justify earlier imaging. Routine MRI for acute uncomplicated back pain "
            "under 6 weeks is generally not covered."
        ),
    },
    {
        "id": "lcd-pt-outpatient",
        "title": "Synthetic LCD: Outpatient Physical Therapy",
        "policy_id": "LCD-L34000-MOCK",
        "category": "therapy",
        "text": (
            "Outpatient physical therapy (CPT 97110 therapeutic exercises) is covered when "
            "ordered by a physician for a documented functional deficit with measurable "
            "goals. Documentation must include objective findings, plan of care, and "
            "progress. Maintenance-only therapy without skilled need is not covered. "
            "Prior authorization may apply after a visit threshold."
        ),
    },
    {
        "id": "ncd-med-necessity",
        "title": "Synthetic NCD: Medical Necessity Standard",
        "policy_id": "NCD-GEN-50-MOCK",
        "category": "medical_necessity",
        "text": (
            "Services must be reasonable and necessary for diagnosis or treatment of illness "
            "or injury. Denial code CO-50 (not deemed a medical necessity) is used when "
            "clinical documentation does not support the service. Appeals should include "
            "clinical notes, diagnosis codes, treatment history, and citations to coverage "
            "policy that support medical necessity."
        ),
    },
    {
        "id": "elig-timely-filing",
        "title": "Synthetic Policy: Timely Filing & Eligibility",
        "policy_id": "RCM-TF-01-MOCK",
        "category": "eligibility",
        "text": (
            "Claims must be filed within the payer timely-filing window (commonly 90–365 days "
            "from service date). Eligibility should be verified before the encounter. "
            "Inactive or terminated coverage on the service date is a common denial reason. "
            "Corrective action: re-verify eligibility, update insurance, or bill the patient."
        ),
    },
    {
        "id": "auth-prior",
        "title": "Synthetic Policy: Prior Authorization",
        "policy_id": "RCM-PA-02-MOCK",
        "category": "authorization",
        "text": (
            "Certain CPT codes require prior authorization before the service date. Missing "
            "authorization denials are often non-appealable for payment unless the payer "
            "allows retrospective auth for emergencies. Always check the payer auth list "
            "during scheduling and document the auth number on the claim."
        ),
    },
    {
        "id": "coding-99213",
        "title": "Synthetic Coding Tip: E/M 99213",
        "policy_id": "CODING-EM-99213-MOCK",
        "category": "coding",
        "text": (
            "CPT 99213 is an established patient office visit of low complexity. Documentation "
            "should support medical decision making or time. Pair with accurate ICD-10 codes "
            "(example M54.5 low back pain). Upcoding or insufficient documentation can cause "
            "coding denials."
        ),
    },
    {
        "id": "appeal-best-practice",
        "title": "Synthetic Appeal Letter Best Practices",
        "policy_id": "RCM-APPEAL-01-MOCK",
        "category": "appeals",
        "text": (
            "A strong appeal letter restates the denial code, summarizes clinical history, "
            "quotes the relevant coverage policy (NCD/LCD), attaches supporting medical "
            "records, and clearly requests reconsideration or payment. Keep tone factual. "
            "Include dates of conservative care when appealing medical-necessity denials "
            "for imaging or therapy."
        ),
    },
    {
        "id": "eob-reading",
        "title": "Synthetic Guide: Reading an EOB",
        "policy_id": "RCM-EOB-01-MOCK",
        "category": "billing",
        "text": (
            "An Explanation of Benefits (EOB) shows billed amount, allowed amount, paid amount, "
            "patient responsibility, and any denial/adjustment codes (CARC/RARC). CO-50 means "
            "not medically necessary. PR codes indicate patient responsibility. Use OCR on "
            "EOBs to auto-create denial work items in RCM workflows."
        ),
    },
]
