# Smart RCM – Patient & Insurance Eligibility Management (Capstone POC)

Production-grade Revenue Cycle Management (RCM) Proof of Concept (POC) demonstrating **EHR integration (Epic / Oracle Health / Live HAPI FHIR R4 API)**, **PostgreSQL persistence**, and **Clearinghouse Eligibility Verification (EDI 270/271 style via Availity mock service)**.

> **DEMO ENVIRONMENT NOTE**  
> • **EHR Integration:** Connects directly to the live public HL7 FHIR server at `https://hapi.fhir.org/baseR4` to retrieve real patient, encounter, and coverage resources into PostgreSQL, with adapters for Epic and Oracle Health.  
> • **Clearinghouse Integration:** Connects to the Availity Clearinghouse service adapter simulating real Availity Payer IDs (`AVAIL-ACME-001`, `AVAIL-BCBS-001`, `AVAIL-UHC-001`, `AVAIL-MERCYCARE-001`), EDI 270 benefit inquiries, 271 adjudication responses, and durable verification audit logging.

---

## 🎯 Capstone Proof of Concept (POC) Deliverables

| Task | Requirement | Implementation Status | Key Features & Evidence |
|:---|:---|:---:|:---|
| **Task 1: Epic / EHR Integration – Patient & Encounter** | Retrieve patient, encounter, and insurance coverage information; maintain EHR identifiers | ✅ **100% Fulfilled** | • Live client querying `https://hapi.fhir.org/baseR4/Patient`, `/Encounter`, `/Coverage`<br>• Preserves `external_ehr_patient_id` (e.g. `14405`, `nhanes-121480`) and `external_ehr_encounter_id` (e.g. `enc-hapi-14405`) |
| **Task 2: PostgreSQL – Insurance Policy & Payer** | Maintain patient, encounter, policy records; map payers to Availity IDs; initiate verification; store history | ✅ **100% Fulfilled** | • Relational PostgreSQL schema (`patients`, `encounters`, `insurance_policies`, `payers`, `payer_mappings`, `eligibility_requests`, `eligibility_responses`, `eligibility_history`)<br>• Fully audited verification history |
| **Task 3: Availity – Payer Mapping** | Retrieve supported payers directory; map to Availity Payer IDs; return verification results to RCM | ✅ **100% Fulfilled** | • `/api/availity/payers` directory with Availity IDs<br>• `/api/availity/payers/sync-mappings` upserting to `payer_mappings`<br>• Support for HMO, PPO, EPO commercial & regional payers |
| **Task 4: Availity – Eligibility Verification** | Submit 270 eligibility verification and return 271 benefits/status | ✅ **100% Fulfilled** | • Real-time verification via `POST /api/availity/eligibility/verify`<br>• Generates unique transaction ID (`MOCK-AVY-*`), matches active coverage, deductibles, coinsurance, copays |
| **Task 5: Eligibility Results & UI** | Display verified benefits card, transaction trace, copay/deductible breakdown, and audit history | ✅ **100% Fulfilled** | • Interactive Next.js web application (`/walkthrough`, `/patients`, `/eligibility`, `/payers`, `/dashboard`)<br>• Real-time benefits display with status pills, copay, deductible remaining, and audit trail |

---

## 📚 16-Phase Healthcare & RCM Learning Matrix

| Phase | Learning Topic | Key Concepts | Hands-On Module / URL |
|---|---|---|---|
| **1. Healthcare Ecosystem** | US Healthcare Foundation | Patients, Members, Providers, Payers, Employers, Payment Flows | `/walkthrough` (Interactive Architecture Map) |
| **2. Insurance Fundamentals** | Plan Designs & Cost-Sharing | HMO, PPO, EPO, Deductibles, Coinsurance, Copays | `/insurance` & `/eligibility` |
| **3. Medical Terminology** | Coding Standards | ICD-10-CM diagnosis codes, CPT procedure codes, HCPCS, DRG | `/claims` & Claim Details |
| **4. Healthcare Systems & EHR** | EHR / PMS Architecture | Epic Systems, Oracle Health (Cerner), NextGen, Athenahealth | `/ehr/sources` & `/patients` |
| **5. Healthcare Standards** | Interoperability Standards | HL7 v2, FHIR R4, SMART on FHIR, Patient, Encounter, Coverage | Live `https://hapi.fhir.org/baseR4` Client |
| **6. Provider Workflow & RCM** | Revenue Cycle Lifecycle | Pre-registration, Scheduling, Eligibility, Coding, Charge Capture | `/walkthrough` (End-to-End Stepper) |
| **7. Eligibility Verification** | EDI 270 / 271 Inquiries | 270 Benefit Request, 271 Adjudication Response, Status Codes | `/eligibility` Verification Lab |
| **8. Claims Creation** | Claim Forms & EDI | CMS-1500 (Professional), UB-04 (Institutional), 837P / 837I | `/claims` (Creation & Seed) |
| **9. Clearinghouses** | EDI Gateways & Routing | Availity, Waystar, Office Ally, Change Healthcare, Payer IDs | `/payers` & `/availity/payers` |
| **10. Claim Adjudication** | Payer Adjudication Engine | Medical Necessity, Coverage Rules, Prior Authorization | `/claims` (Adjudication Engine) |
| **11. Payment Processing** | Remittance & Settlement | 835 ERA (Electronic Remittance Advice), EOB, Reconciliation | `/claims` (Payment Remittance Details) |
| **12. Denial Management** | CARC & RARC Codes | Claim Adjustment Reason Codes, Remittance Advice Remark Codes | `/denials` (Categorized Denials) |
| **13. Appeals Management** | Dispute Resolution | Appeal Workflow, Evidence Packet Generation, Timely Filing | `/denials` (Generate Appeal Packet) |
| **14. AI Healthcare Documents** | Document Intelligence & OCR | Medical Records, CMS-1500 Scanning, Superbills, Entity Extraction | `/documents` (Structured Extraction) |
| **15. AI Policy Copilot & RAG** | Vector Knowledge Base | CMS Guidelines, Payer Coverage Manuals, Semantic Retrieval | `/policy` (Policy Assistant) |
| **16. Capstone Assistant** | End-to-End Orchestration | Unified Assistant combining FHIR + Claims + Denials + AI | `/assistant` (Interactive RCM Copilot) |

---

## 🛠️ Tech Stack

- **Frontend:** Next.js (App Router), TypeScript, Tailwind CSS, TanStack Query, React Hook Form, Zod, Recharts, Lucide Icons
- **Backend:** FastAPI, Python 3.14 / 3.11+, SQLAlchemy 2.0, Alembic, httpx, Pytest
- **Database:** PostgreSQL (Database: `smart_rcm_eligibility`)
- **EHR API:** Live public HL7 FHIR server (`https://hapi.fhir.org/baseR4`) + Epic/Oracle adapters
- **Clearinghouse API:** Availity Mock Adapter with EDI 270/271 simulation

---

## 🚀 Running the Project

### 1. Database Setup (PostgreSQL)

Ensure PostgreSQL is running locally on port 5432:
```bash
createdb smart_rcm_eligibility
```

### 2. Backend Server (FastAPI)

```bash
cd smart-rcm-eligibility/backend

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations (if needed)
alembic upgrade head

# Start backend server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
- **Backend URL:** http://localhost:8000
- **Interactive Swagger Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/api/health
- **Integrations Status:** http://localhost:8000/api/integrations/status

### 3. Frontend Application (Next.js)

```bash
cd smart-rcm-eligibility/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```
- **Frontend URL:** http://localhost:3002 (or http://localhost:3000)
- **Start Here / Capstone Scorecard:** http://localhost:3002/walkthrough
- **Live Patients Sync:** http://localhost:3002/patients
- **Eligibility Verification Lab:** http://localhost:3002/eligibility
- **Payers Directory:** http://localhost:3002/payers

---

## 🧪 Automated Testing

Run the full pytest suite in the backend:

```bash
cd smart-rcm-eligibility/backend
.venv/bin/pytest -v
```

All 7 test cases covering the entire Capstone flow pass:
- `test_capstone_ehr_sources` (Live HAPI verification)
- `test_capstone_availity_payers` (Availity directory & payer IDs)
- `test_capstone_payer_mappings_sync` (PostgreSQL mapping persistence)
- `test_capstone_patient_and_encounter_external_ids` (EHR external IDs)
- `test_capstone_eligibility_verification_and_history` (270/271 verify + audit log)
- `test_integrations_status_has_no_availity`
- `test_health_endpoint_shape`

---

## 📡 Live HAPI FHIR Sync Demonstration

To sync live FHIR patients directly from `https://hapi.fhir.org/baseR4` into PostgreSQL via CLI:

```bash
curl -X POST "http://localhost:8000/api/ehr/hapi/sync/all?mock_only=false"
```

Sample Response:
```json
{
  "ehr_source": "hapi",
  "mode": "LIVE_ATTEMPT",
  "patients": {
    "created": 0,
    "updated": 21,
    "source": "HAPI_FHIR",
    "note": "EHR identifiers stored on patients.external_ehr_patient_id"
  },
  "encounters": {
    "created": 0,
    "updated": 0,
    "skipped": 20,
    "source": "HAPI_FHIR",
    "note": "EHR encounter ids stored on encounters.external_ehr_encounter_id"
  },
  "coverage": {
    "created": 0,
    "updated": 1,
    "skipped": 19,
    "source": "HAPI_FHIR"
  },
  "availity_mappings": {
    "mappings_upserted": 0,
    "source": "MOCK_AVAILITY",
    "note": "external_payer_identifier holds Availity Payer ID (mock)."
  }
}
```

To run an Availity 270/271 eligibility verification for a live patient (e.g. Carlos Vega, ID `14405`, MercyCare Health Plan):

```bash
curl -X POST "http://localhost:8000/api/availity/eligibility/verify" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "<patient-uuid>",
    "insurance_policy_id": "<policy-uuid>",
    "encounter_id": "<encounter-uuid>",
    "service_date": "2026-03-10",
    "scenario": "ACTIVE"
  }'
```
Response includes verified copay (\$30), deductible (\$1,500), deductible remaining (\$800), coinsurance (20%), and clearinghouse transaction trace ID (`MOCK-AVY-*`).
