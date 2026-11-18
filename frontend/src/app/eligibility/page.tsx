"use client";

import { Suspense, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { AppShell } from "@/components/layout/AppShell";
import { ModuleGuide } from "@/components/learn/ModuleGuide";
import { GUIDES } from "@/components/learn/guideContent";
import { API_BASE } from "@/services/api";

type Patient = { id: string; first_name: string; last_name: string };
type Policy = {
  id: string;
  patient_id: string;
  member_id: string;
  payer_name?: string;
};
type ScenarioList = { scenarios: string[]; disclaimer: string };
type Result = {
  id: string;
  request_status: string;
  scenario: string;
  member_id: string;
  service_date: string;
  response?: {
    eligibility_status: string;
    copay?: number;
    deductible?: number;
    deductible_remaining?: number;
    coinsurance?: string;
    benefits?: Record<string, string>;
    response_message?: string;
    payer_name?: string;
    source?: string;
    response_payload?: {
      availity_payer_id?: string;
      transaction_id?: string;
      source?: string;
    };
  };
};

export default function EligibilityPage() {
  return (
    <AppShell activeHref="/eligibility">
      <Suspense fallback={<p className="text-sm text-slate-500">Loading…</p>}>
        <EligibilityForm />
      </Suspense>
    </AppShell>
  );
}

function EligibilityForm() {
  const search = useSearchParams();
  const [patients, setPatients] = useState<Patient[]>([]);
  const [policies, setPolicies] = useState<Policy[]>([]);
  const [scenarios, setScenarios] = useState<string[]>([]);
  const [disclaimer, setDisclaimer] = useState("");
  const [patientId, setPatientId] = useState(
    search.get("patient_id") ?? "",
  );
  const [policyId, setPolicyId] = useState(
    search.get("insurance_policy_id") ?? "",
  );
  const [scenario, setScenario] = useState("ACTIVE");
  const [serviceDate, setServiceDate] = useState(
    new Date().toISOString().slice(0, 10),
  );
  const [result, setResult] = useState<Result | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    void (async () => {
      const [p, i, s] = await Promise.all([
        fetch(`${API_BASE}/patients`).then((r) => r.json()),
        fetch(`${API_BASE}/insurance`).then((r) => r.json()),
        fetch(`${API_BASE}/eligibility/mock-scenarios`).then((r) => r.json()),
      ]);
      setPatients(p.items ?? []);
      setPolicies(i.items ?? []);
      const sc = s as ScenarioList;
      setScenarios(sc.scenarios ?? []);
      setDisclaimer(sc.disclaimer ?? "");
      if (!patientId && p.items?.[0]) setPatientId(p.items[0].id);
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const patientPolicies = useMemo(
    () => policies.filter((p) => p.patient_id === patientId),
    [policies, patientId],
  );

  useEffect(() => {
    if (
      patientPolicies.length &&
      !patientPolicies.some((p) => p.id === policyId)
    ) {
      setPolicyId(patientPolicies[0].id);
    }
  }, [patientPolicies, policyId]);

  async function verify() {
    setBusy(true);
    setError("");
    setResult(null);
    try {
      const res = await fetch(`${API_BASE}/availity/eligibility/verify`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          patient_id: patientId,
          insurance_policy_id: policyId,
          service_date: serviceDate,
          scenario,
        }),
      });
      if (!res.ok) {
        const body = await res.text();
        throw new Error(body || `HTTP ${res.status}`);
      }
      setResult(await res.json());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Verify failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-6">
      <header>
        <h2 className="text-2xl font-semibold">
          Eligibility Verification (Mock Availity)
        </h2>
        <p className="mt-1 text-sm text-slate-600">
          Submit a mock 270-style request through Mock Availity; store results
          and history in PostgreSQL.
        </p>
        <p className="mt-2 text-xs font-medium text-red-700">
          MOCK AVAILITY – NOT live Availity / not real payer credentials
        </p>
      </header>
      <ModuleGuide {...GUIDES.eligibility} />

      <div className="grid gap-4 rounded-xl border border-slate-200 bg-white p-5 shadow-sm md:grid-cols-2">
        <label className="block text-sm">
          <span className="text-slate-500">Patient</span>
          <select
            className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2"
            value={patientId}
            onChange={(e) => setPatientId(e.target.value)}
          >
            {patients.map((p) => (
              <option key={p.id} value={p.id}>
                {p.first_name} {p.last_name}
              </option>
            ))}
          </select>
        </label>
        <label className="block text-sm">
          <span className="text-slate-500">Insurance policy</span>
          <select
            className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2"
            value={policyId}
            onChange={(e) => setPolicyId(e.target.value)}
          >
            {patientPolicies.map((p) => (
              <option key={p.id} value={p.id}>
                {p.payer_name ?? "Payer"} · {p.member_id}
              </option>
            ))}
          </select>
        </label>
        <label className="block text-sm">
          <span className="text-slate-500">Service date</span>
          <input
            type="date"
            className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2"
            value={serviceDate}
            onChange={(e) => setServiceDate(e.target.value)}
          />
        </label>
        <label className="block text-sm">
          <span className="text-slate-500">Mock scenario</span>
          <select
            className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2"
            value={scenario}
            onChange={(e) => setScenario(e.target.value)}
          >
            {scenarios.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </label>
      </div>

      <button
        onClick={() => void verify()}
        disabled={busy || !patientId || !policyId}
        className="rounded-md bg-teal-700 px-5 py-2.5 text-sm font-medium text-white hover:bg-teal-800 disabled:opacity-50"
      >
        {busy ? "Checking Mock Availity…" : "Verify via Mock Availity"}
      </button>

      {error ? (
        <pre className="overflow-auto rounded-lg bg-red-50 p-3 text-xs text-red-800">
          {error}
        </pre>
      ) : null}

      {result ? (
        <section className="rounded-xl border border-teal-200 bg-teal-50/40 p-5">
          <h3 className="text-sm font-semibold">
            Result:{" "}
            {result.response?.eligibility_status ?? result.request_status}
          </h3>
          <p className="mt-1 text-sm text-slate-700">
            {result.response?.response_message}
          </p>
          <dl className="mt-4 grid gap-2 text-sm sm:grid-cols-2">
            <Row label="Scenario" value={result.scenario} />
            <Row label="Member" value={result.member_id} />
            <Row label="Service date" value={result.service_date} />
            <Row label="Payer" value={result.response?.payer_name} />
            <Row
              label="Source"
              value={
                result.response?.source ??
                result.response?.response_payload?.source ??
                "MOCK_AVAILITY"
              }
            />
            <Row
              label="Availity payer ID"
              value={String(
                result.response?.response_payload?.availity_payer_id ?? "—",
              )}
            />
            <Row
              label="Transaction ID"
              value={String(
                result.response?.response_payload?.transaction_id ?? "—",
              )}
            />
            <Row label="Copay" value={fmtMoney(result.response?.copay)} />
            <Row
              label="Deductible"
              value={fmtMoney(result.response?.deductible)}
            />
            <Row
              label="Deductible remaining"
              value={fmtMoney(result.response?.deductible_remaining)}
            />
            <Row label="Coinsurance" value={result.response?.coinsurance} />
          </dl>
          {result.response?.benefits ? (
            <ul className="mt-3 space-y-1 text-xs text-slate-600">
              {Object.entries(result.response.benefits).map(([k, v]) => (
                <li key={k}>
                  <strong>{k}:</strong> {v}
                </li>
              ))}
            </ul>
          ) : null}
        </section>
      ) : null}

      <p className="text-xs text-slate-500">{disclaimer}</p>
    </div>
  );
}

function Row({ label, value }: { label: string; value?: string | null }) {
  return (
    <div className="flex justify-between gap-2 rounded-md bg-white/70 px-3 py-2">
      <dt className="text-slate-500">{label}</dt>
      <dd className="font-medium">{value ?? "—"}</dd>
    </div>
  );
}

function fmtMoney(n?: number | null) {
  if (n == null) return "—";
  return `$${Number(n).toFixed(2)}`;
}
