# Smart RCM – Patient & Insurance Eligibility Management

End-to-end RCM eligibility POC using **HAPI FHIR R4** as a mock EHR and an **internal Mock Eligibility Provider**.

> **MOCK DATA – NOT REAL INSURANCE VERIFICATION**  
> No Availity. No real payer credentials. Synthetic data only.

> Note: The older `smart-rcm/` folder in this workspace is a separate learning lab (claims/denials). This project lives in **`smart-rcm-eligibility/`**.

---

## Phase status

| Phase | Status |
|---|---|
| 1 – Foundation (this) | ✅ Done |
| 2 – HAPI FHIR adapter | ⏳ Waiting approval |
| 3 – DB models + patient/insurance APIs & UI | Planned |
| 4 – Payers | Planned |
| 5 – Mock eligibility engine | Planned |
| 6 – Dashboard metrics & tests | Planned |
| 7 – Docs / handover | Planned |

---

## Stack

- **Frontend:** Next.js, TypeScript, Tailwind CSS, TanStack Query, React Hook Form, Zod, Recharts
- **Backend:** FastAPI, Pydantic, SQLAlchemy 2.x, Alembic, httpx, Pytest
- **Database:** PostgreSQL
- **EHR:** https://hapi.fhir.org/baseR4
- **Eligibility:** Internal mock provider (Phase 5)

---

## Prerequisites

- Python 3.11+ (3.14 works with current pins)
- Node.js 20+
- PostgreSQL 14+ (optional for Phase 1 smoke — health returns `degraded` if DB is down)

Create the database once Postgres is available:

```bash
createdb smart_rcm_eligibility
# or via psql: CREATE DATABASE smart_rcm_eligibility;
```

---

## Backend

```bash
cd smart-rcm-eligibility/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit DATABASE_URL if needed

alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

- API docs: http://localhost:8000/docs  
- Health: http://localhost:8000/api/health  
- Integrations: http://localhost:8000/api/integrations/status  

### Tests

```bash
cd smart-rcm-eligibility/backend
source .venv/bin/activate
pytest -q
```

---

## Frontend

```bash
cd smart-rcm-eligibility/frontend
npm install
cp .env.local.example .env.local
npm run dev
```

UI: http://localhost:3000 (redirects to `/dashboard`)

---

## Environment

**Backend `.env`** (from `.env.example`):

```
DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/smart_rcm_eligibility
HAPI_FHIR_BASE_URL=https://hapi.fhir.org/baseR4
APP_ENV=development
LOG_LEVEL=INFO
```

**Frontend `.env.local`:**

```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
```

No `AVAILITY_*` variables. Never put DB credentials in frontend env.

---

## Architecture (Phase 1)

```
smart-rcm-eligibility/
  backend/
    app/
      main.py
      core/          # config, database, logging
      api/routes/    # health (+ later domains)
      models/        # Phase 3+
      schemas/
      services/
      integrations/ehr|eligibility/  # Phase 2 / 5
    alembic/
    tests/
  frontend/
    src/app/dashboard|patients|encounters|insurance|payers|eligibility|history
    src/components/layout|dashboard
    src/services/api.ts
```

---

## What’s next

Reply **approve Phase 2** to implement the HAPI FHIR R4 adapter (`/metadata`, Patient/Encounter/Coverage retrieval, sync endpoints, Epic/Oracle placeholders).
