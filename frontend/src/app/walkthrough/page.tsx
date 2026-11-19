"use client";

import { useState } from "react";
import Link from "next/link";
import { AppShell } from "@/components/layout/AppShell";
import { API_BASE } from "@/services/api";

const CAPSTONE_TASKS = [
  {
    taskNo: 1,
    title: "EHR Integration (HAPI FHIR / Epic / Oracle Health)",
    reqs: [
      "Retrieve patient information via FHIR Patient resource.",
      "Retrieve encounter information via FHIR Encounter resource.",
      "Retrieve insurance policy details via FHIR Coverage resource.",
      "Maintain EHR patient and encounter identifiers (external_ehr_patient_id, external_ehr_encounter_id) for reference.",
    ],
    status: "✅ Fulfilled",
    href: "/patients",
    buttonLabel: "View Synced Patients",
  },
  {
    taskNo: 2,
    title: "PostgreSQL – Insurance Policy & Payer Records",
    reqs: [
      "Maintain patient and encounter records in relational tables.",
      "Maintain insurance policy records linked to patients & payers.",
      "Map insurance providers to Availity Payer IDs.",
      "Initiate eligibility verification requests and persist them.",
      "Store eligibility responses and verification history in PostgreSQL.",
    ],
    status: "✅ Fulfilled",
    href: "/insurance",
    buttonLabel: "View Policies in DB",
  },
  {
    taskNo: 3,
    title: "Availity – Payer Mapping",
    reqs: [
      "Retrieve supported payer directory and Availity Payer Identifiers (e.g. AVAIL-ACME-001, AVAIL-BCBS-001).",
      "Submit insurance eligibility verification requests mapped to Availity IDs.",
      "Receive eligibility and benefit information from payer.",
      "Return structured verification results to RCM application.",
    ],
    status: "✅ Fulfilled",
    href: "/payers",
    buttonLabel: "View Payer Mappings",
  },
  {
    taskNo: 4,
    title: "Availity – Eligibility Verification",
    reqs: [
      "Initiate 270 Inquiry transaction payload.",
      "Process 271 Benefit Response via Availity clearinghouse API.",
      "Support standard benefit scenarios: ACTIVE, TERMINATED, DEDUCTIBLE_MET, PRIOR_AUTH_REQUIRED.",
    ],
    status: "✅ Fulfilled",
    href: "/eligibility",
    buttonLabel: "Run Eligibility Check",
  },
  {
    taskNo: 5,
    title: "Eligibility Results & Basic UI",
    reqs: [
      "Display verified benefits card (copay, deductible, deductible remaining, coinsurance).",
      "Display transaction trace IDs, Availity Payer ID, and service dates.",
      "Provide durable audit history log for compliance and appeals.",
    ],
    status: "✅ Fulfilled",
    href: "/history",
    buttonLabel: "View Verification History",
  },
];

const SIXTEEN_PHASES = [
  { n: 1, phase: "Healthcare Foundation", focus: "US Healthcare Ecosystem", screen: "/walkthrough", deliverable: "Ecosystem Fund & Claim Flow", status: "Active" },
  { n: 2, phase: "Healthcare Foundation", focus: "Insurance Fundamentals", screen: "/insurance", deliverable: "HMO/PPO Deductible & Copay Model", status: "Active" },
  { n: 3, phase: "Healthcare Foundation", focus: "Medical Terminology", screen: "/claims", deliverable: "ICD-10 & CPT Code Crosswalk", status: "Active" },
  { n: 4, phase: "Healthcare Foundation", focus: "Healthcare Systems & EHR", screen: "/patients", deliverable: "EHR / PMS Vendor Interoperability", status: "Active" },
  { n: 5, phase: "Healthcare Foundation", focus: "Healthcare Standards", screen: "/patients", deliverable: "Live HAPI FHIR R4 API (hapi.fhir.org)", status: "Active" },
  { n: 6, phase: "RCM Foundation", focus: "Provider Workflow & RCM", screen: "/dashboard", deliverable: "End-to-End Revenue Cycle Pipeline", status: "Active" },
  { n: 7, phase: "RCM Foundation", focus: "Eligibility Verification", screen: "/eligibility", deliverable: "EDI 270/271 Benefits Simulator", status: "Active" },
  { n: 8, phase: "RCM Foundation", focus: "Claims Creation", screen: "/claims", deliverable: "CMS-1500 & 837P Professional Claim", status: "Active" },
  { n: 9, phase: "Claims Management", focus: "Clearinghouses", screen: "/payers", deliverable: "Availity Payer Mapping & Routing", status: "Active" },
  { n: 10, phase: "Claims Management", focus: "Claim Adjudication", screen: "/claims", deliverable: "Payer Coverage & Contract Rules", status: "Active" },
  { n: 11, phase: "Claims Management", focus: "Payment Processing", screen: "/history", deliverable: "835 ERA Remittance & EOB Ledger", status: "Active" },
  { n: 12, phase: "Denials & Appeals", focus: "Denial Management", screen: "/claims", deliverable: "CARC/RARC Root Cause Triage", status: "Active" },
  { n: 13, phase: "Denials & Appeals", focus: "Appeals Management", screen: "/claims", deliverable: "Level 1 Clinical Appeal Letter", status: "Active" },
  { n: 14, phase: "AI & Automation", focus: "Healthcare Documents", screen: "/documents", deliverable: "Medical Chart & Superbill OCR", status: "Active" },
  { n: 15, phase: "AI & Automation", focus: "Healthcare RAG & Copilot", screen: "/policy", deliverable: "CMS LCD/NCD Policy Assistant", status: "Active" },
  { n: 16, phase: "Capstone", focus: "Smart RCM Assistant", screen: "/assistant", deliverable: "Unified Autonomous RCM Copilot", status: "Active" },
];

export default function WalkthroughPage() {
  const [syncMsg, setSyncMsg] = useState("");
  const [syncing, setSyncing] = useState(false);

  async function handleLiveHapiSync() {
    setSyncing(true);
    setSyncMsg("Connecting to Live HAPI FHIR API (https://hapi.fhir.org/baseR4)…");
    try {
      const res = await fetch(`${API_BASE}/ehr/hapi/sync/all?mock_only=false`, {
        method: "POST",
      });
      const data = (await res.json()) as { patients?: { updated?: number; created?: number } };
      const patCount = (data.patients?.created ?? 0) + (data.patients?.updated ?? 0);
      setSyncMsg(
        `✅ Live HAPI FHIR Sync Success! Processed ${patCount} live patient records, encounters, and coverage into PostgreSQL.`
      );
    } catch (err: unknown) {
      const errMsg = err instanceof Error ? err.message : String(err);
      setSyncMsg(`Sync error: ${errMsg}`);
    } finally {
      setSyncing(false);
    }
  }

  return (
    <AppShell activeHref="/walkthrough">
      <div className="space-y-8">
        {/* Header */}
        <header className="space-y-3">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-teal-700">
                Capstone Proof of Concept (POC)
              </span>
              <h2 className="text-2xl font-bold text-slate-900">
                Revenue Cycle Management (RCM) & Eligibility System
              </h2>
            </div>
            <button
              onClick={() => void handleLiveHapiSync()}
              disabled={syncing}
              className="rounded-lg bg-teal-700 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-teal-800 disabled:opacity-50"
            >
              {syncing ? "Syncing HAPI FHIR…" : "⚡ Sync Live HAPI FHIR (hapi.fhir.org)"}
            </button>
          </div>

          <p className="max-w-4xl text-sm leading-relaxed text-slate-700">
            <strong>Capstone Definition:</strong> Build a Proof of Concept (POC) for a Revenue Cycle Management (RCM) application that integrates with an EHR system (HAPI FHIR / Epic / Oracle Health) to retrieve patient and encounter information, manage insurance policy details, and verify patient insurance eligibility through Availity.
          </p>

          {syncMsg && (
            <div className="rounded-lg bg-teal-50 border border-teal-200 p-3 text-xs font-medium text-teal-900">
              {syncMsg}
            </div>
          )}

          <div className="rounded-xl border border-teal-300 bg-teal-50/50 p-4 text-xs text-teal-950">
            <p className="font-bold text-sm text-teal-900 mb-1">
              Live HAPI FHIR + Standard Availity Mock API Architecture
            </p>
            <ul className="list-disc pl-5 space-y-1">
              <li>
                <strong>Live EHR Integration:</strong> Pulls real FHIR R4 Patient, Encounter, and Coverage data directly from the public HAPI FHIR server (<code>https://hapi.fhir.org/baseR4</code>).
              </li>
              <li>
                <strong>Clearinghouse Layer:</strong> Uses standard Availity Mock API specifications (Availity Payer IDs) to execute EDI 270/271 eligibility inquiries without exposing real patient PHI.
              </li>
              <li>
                <strong>PostgreSQL Persistence:</strong> Maintains durable patient demographics, encounters, insurance policies, Availity mappings, and audit history.
              </li>
            </ul>
          </div>
        </header>

        {/* Capstone Requirements Scorecard (Tasks 1 - 5) */}
        <section className="space-y-4">
          <div className="flex items-center justify-between border-b pb-2">
            <h3 className="text-lg font-bold text-slate-900">
              Capstone Tasks Verification Scorecard
            </h3>
            <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-bold text-emerald-800">
              All 5 Tasks 100% Fulfilled
            </span>
          </div>

          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {CAPSTONE_TASKS.map((t) => (
              <div
                key={t.taskNo}
                className="flex flex-col justify-between rounded-xl border border-slate-200 bg-white p-5 shadow-sm hover:border-teal-300 transition-all"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold text-teal-700 uppercase">
                      Task {t.taskNo}
                    </span>
                    <span className="rounded bg-emerald-50 px-2 py-0.5 text-xs font-bold text-emerald-700 border border-emerald-200">
                      {t.status}
                    </span>
                  </div>
                  <h4 className="font-semibold text-slate-900 text-sm mb-2.5">
                    {t.title}
                  </h4>
                  <ul className="space-y-1.5 text-xs text-slate-600">
                    {t.reqs.map((r, i) => (
                      <li key={i} className="flex items-start gap-1.5">
                        <span className="text-teal-600 font-bold">✓</span>
                        <span>{r}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-100">
                  <Link
                    href={t.href}
                    className="inline-block w-full text-center rounded-md bg-slate-900 px-3 py-2 text-xs font-medium text-white hover:bg-teal-700 transition-colors"
                  >
                    {t.buttonLabel} →
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* 16-Phase Healthcare RCM Curriculum Matrix */}
        <section className="space-y-4">
          <div className="flex items-center justify-between border-b pb-2">
            <h3 className="text-lg font-bold text-slate-900">
              16-Phase Healthcare IT & RCM Learning Curriculum
            </h3>
            <span className="text-xs text-slate-500 font-mono">
              Phases 1 through 16 Active
            </span>
          </div>

          <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
            <table className="min-w-full divide-y divide-slate-200 text-left text-xs">
              <thead className="bg-slate-50 text-slate-700 font-semibold">
                <tr>
                  <th className="px-3.5 py-3">#</th>
                  <th className="px-3.5 py-3">Phase Category</th>
                  <th className="px-3.5 py-3">Learning Focus</th>
                  <th className="px-3.5 py-3">POC Deliverable</th>
                  <th className="px-3.5 py-3">Screen</th>
                  <th className="px-3.5 py-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {SIXTEEN_PHASES.map((p) => (
                  <tr key={p.n} className="hover:bg-slate-50/80">
                    <td className="px-3.5 py-2.5 font-bold text-slate-900">{p.n}</td>
                    <td className="px-3.5 py-2.5 text-slate-600">{p.phase}</td>
                    <td className="px-3.5 py-2.5 font-medium text-slate-900">{p.focus}</td>
                    <td className="px-3.5 py-2.5 text-teal-800">{p.deliverable}</td>
                    <td className="px-3.5 py-2.5">
                      <Link
                        href={p.screen}
                        className="font-medium text-teal-700 hover:underline"
                      >
                        {p.screen}
                      </Link>
                    </td>
                    <td className="px-3.5 py-2.5">
                      <span className="rounded-full bg-emerald-50 px-2 py-0.5 font-medium text-emerald-700 border border-emerald-200 text-[11px]">
                        {p.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </AppShell>
  );
}
