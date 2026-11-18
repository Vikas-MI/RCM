"use client";

import Link from "next/link";
import { AppShell } from "@/components/layout/AppShell";

const STEPS = [
  {
    n: 1,
    href: "/patients",
    title: "Sync Mock Epic → patients & encounters",
    body: "On Patients, choose Mock Epic and click Sync EHR → Postgres. This pulls patient, encounter, and insurance coverage into PostgreSQL and keeps EHR identifiers (epic-…).",
    term: "EHR = Electronic Health Record. This demo uses MOCK Epic — not live Epic credentials.",
  },
  {
    n: 2,
    href: "/encounters",
    title: "Confirm encounters in Postgres",
    body: "Open Encounters. Each visit is stored with an external EHR encounter ID for reference.",
    term: "Encounter = one visit tied to a patient and date.",
  },
  {
    n: 3,
    href: "/insurance",
    title: "Confirm insurance policies",
    body: "Insurance shows member IDs and coverage dates pulled from the mock EHR Coverage resources.",
    term: "Insurance policy = the patient’s coverage card on file in Postgres.",
  },
  {
    n: 4,
    href: "/payers",
    title: "Map payers → Mock Availity IDs",
    body: "Open Payers. Click Sync Mock Availity mappings. Internal payer codes (PAYER001…) map to Availity-style IDs (AVAIL-ACME-001…). Stored in PostgreSQL payer_mappings.",
    term: "Availity payer ID = clearinghouse identifier for a payer. Here it is MOCK only.",
  },
  {
    n: 5,
    href: "/eligibility",
    title: "Verify eligibility via Mock Availity",
    body: "Pick Ava Chen + her Acme policy + scenario ACTIVE. Click Verify via Mock Availity. You should see status ACTIVE, benefits, Availity payer ID, and a mock transaction ID.",
    term: "Eligibility = asking the clearinghouse if coverage is active for a service date.",
  },
  {
    n: 6,
    href: "/history",
    title: "Show results & history",
    body: "History lists every verification (action VERIFY_MOCK_AVAILITY) stored in PostgreSQL for audit.",
    term: "Verification history = durable log of requests and status changes.",
  },
  {
    n: 7,
    href: "/dashboard",
    title: "Dashboard scoreboard",
    body: "Dashboard shows Postgres counts and integration modes (Epic/Oracle/Availity all labeled MOCK).",
    term: "POC = Proof of Concept using simulated integrations end-to-end.",
  },
];

export default function WalkthroughPage() {
  return (
    <AppShell activeHref="/walkthrough">
      <div className="space-y-6">
        <header className="space-y-3">
          <h2 className="text-2xl font-semibold text-slate-900">
            POC demo walkthrough (8 PM ready)
          </h2>
          <p className="max-w-3xl text-sm leading-relaxed text-slate-700">
            This path matches the RCM POC definition: Mock EHR (Epic/Oracle) →
            PostgreSQL patients/encounters/insurance → Mock Availity payer IDs →
            eligibility verify → results/history → UI. Follow Ava Chen.
          </p>
          <div className="rounded-xl border border-amber-300 bg-amber-50 px-4 py-3 text-sm text-amber-950">
            <p className="font-semibold">Say this in the demo</p>
            <ul className="mt-2 list-disc space-y-1 pl-5">
              <li>
                Epic / Oracle Health are <strong>simulated</strong> — no live
                credentials.
              </li>
              <li>
                Availity is a <strong>Mock Availity</strong> clearinghouse — not
                live X12 / Availity API.
              </li>
              <li>
                All durable records live in <strong>PostgreSQL</strong>{" "}
                (policies, mappings, eligibility history).
              </li>
            </ul>
          </div>
        </header>

        <ol className="space-y-4">
          {STEPS.map((step) => (
            <li
              key={step.n}
              className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
            >
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wide text-teal-700">
                    Step {step.n}
                  </p>
                  <h3 className="mt-1 text-lg font-semibold text-slate-900">
                    {step.title}
                  </h3>
                </div>
                <Link
                  href={step.href}
                  className="rounded-md bg-teal-700 px-3 py-2 text-sm font-medium text-white hover:bg-teal-800"
                >
                  Open this screen
                </Link>
              </div>
              <p className="mt-3 text-sm leading-relaxed text-slate-700">
                {step.body}
              </p>
              <p className="mt-2 rounded-md bg-slate-50 px-3 py-2 text-xs text-slate-600">
                <span className="font-semibold text-slate-800">Note: </span>
                {step.term}
              </p>
            </li>
          ))}
        </ol>
      </div>
    </AppShell>
  );
}
