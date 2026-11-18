"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { AppShell } from "@/components/layout/AppShell";
import { API_BASE } from "@/services/api";

type Patient = {
  id: string;
  first_name: string;
  last_name: string;
  date_of_birth?: string;
  gender?: string;
  phone?: string;
  email?: string;
  city?: string;
  state?: string;
  source: string;
  external_ehr_patient_id?: string;
};

type Encounter = {
  id: string;
  encounter_type?: string;
  encounter_status?: string;
  start_date?: string;
  reason?: string;
};

type Policy = {
  id: string;
  member_id: string;
  payer_name?: string;
  coverage_status: string;
  coverage_start_date?: string;
  coverage_end_date?: string;
};

export default function PatientDetailPage() {
  const params = useParams<{ id: string }>();
  const id = params.id;
  const [patient, setPatient] = useState<Patient | null>(null);
  const [encounters, setEncounters] = useState<Encounter[]>([]);
  const [policies, setPolicies] = useState<Policy[]>([]);

  useEffect(() => {
    if (!id) return;
    void (async () => {
      const [p, e, i] = await Promise.all([
        fetch(`${API_BASE}/patients/${id}`).then((r) => r.json()),
        fetch(`${API_BASE}/patients/${id}/encounters`).then((r) => r.json()),
        fetch(`${API_BASE}/patients/${id}/insurance`).then((r) => r.json()),
      ]);
      setPatient(p);
      setEncounters(e.items ?? []);
      setPolicies(i.items ?? []);
    })();
  }, [id]);

  return (
    <AppShell activeHref="/patients">
      <div className="space-y-6">
        <Link href="/patients" className="text-sm text-teal-700 hover:underline">
          ← Back to patients
        </Link>
        {!patient ? (
          <p className="text-sm text-slate-500">Loading…</p>
        ) : (
          <>
            <header>
              <h2 className="text-2xl font-semibold">
                {patient.first_name} {patient.last_name}
              </h2>
              <p className="mt-1 text-sm text-slate-600">
                One person&apos;s chart: who they are, their visits, and their
                insurance cards. If this is Ava Chen, you are on the main demo
                path from the walkthrough.
              </p>
              <p className="mt-2 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-950">
                Practice data only (source: {patient.source}
                {patient.external_ehr_patient_id
                  ? ` · chart id ${patient.external_ehr_patient_id}`
                  : ""}
                ). Not a real patient.
              </p>
            </header>
            <p className="text-sm text-slate-600">
              Next: verify coverage on{" "}
              <Link href="/eligibility" className="text-teal-700 underline">
                Eligibility
              </Link>
              , or jump to{" "}
              <Link href="/claims" className="text-teal-700 underline">
                Claims
              </Link>{" "}
              if you are following Ava&apos;s MRI denial story.
            </p>

            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 text-sm">
              <Info label="DOB" value={patient.date_of_birth} />
              <Info label="Gender" value={patient.gender} />
              <Info label="Phone" value={patient.phone} />
              <Info
                label="City"
                value={[patient.city, patient.state].filter(Boolean).join(", ")}
              />
            </div>

            <section>
              <h3 className="mb-2 text-sm font-semibold">Encounters</h3>
              <ul className="space-y-2 text-sm">
                {encounters.map((e) => (
                  <li
                    key={e.id}
                    className="rounded-lg border border-slate-200 bg-white px-4 py-3"
                  >
                    <strong>{e.encounter_type ?? "Visit"}</strong> ·{" "}
                    {e.encounter_status} ·{" "}
                    {e.start_date
                      ? new Date(e.start_date).toLocaleDateString()
                      : "—"}
                    {e.reason ? (
                      <span className="text-slate-500"> — {e.reason}</span>
                    ) : null}
                  </li>
                ))}
                {!encounters.length ? (
                  <li className="text-slate-500">No encounters</li>
                ) : null}
              </ul>
            </section>

            <section>
              <h3 className="mb-2 text-sm font-semibold">Insurance</h3>
              <ul className="space-y-2 text-sm">
                {policies.map((p) => (
                  <li
                    key={p.id}
                    className="rounded-lg border border-slate-200 bg-white px-4 py-3"
                  >
                    <strong>{p.payer_name ?? "Payer"}</strong> · member{" "}
                    {p.member_id} · {p.coverage_status}
                    <div className="text-xs text-slate-500">
                      {p.coverage_start_date} → {p.coverage_end_date ?? "open"}
                    </div>
                  </li>
                ))}
                {!policies.length ? (
                  <li className="text-slate-500">No policies</li>
                ) : null}
              </ul>
              {policies.length ? (
                <Link
                  href={`/eligibility?patient_id=${id}&insurance_policy_id=${policies[0].id}`}
                  className="mt-3 inline-block rounded-md bg-teal-700 px-4 py-2 text-sm font-medium text-white"
                >
                  Verify eligibility for this patient
                </Link>
              ) : null}
            </section>
          </>
        )}
      </div>
    </AppShell>
  );
}

function Info({ label, value }: { label: string; value?: string }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white px-4 py-3">
      <div className="text-xs uppercase text-slate-500">{label}</div>
      <div className="mt-1 font-medium">{value || "—"}</div>
    </div>
  );
}
