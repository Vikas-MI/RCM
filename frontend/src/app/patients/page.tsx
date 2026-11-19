"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AppShell } from "@/components/layout/AppShell";
import { ModuleGuide } from "@/components/learn/ModuleGuide";
import { GUIDES } from "@/components/learn/guideContent";
import { DataTable } from "@/components/ui/DataTable";
import { API_BASE } from "@/services/api";

type Patient = {
  id: string;
  first_name: string;
  last_name: string;
  date_of_birth?: string;
  gender?: string;
  phone?: string;
  city?: string;
  source: string;
  external_ehr_patient_id?: string;
};

export default function PatientsPage() {
  const [items, setItems] = useState<Patient[]>([]);
  const [q, setQ] = useState("");
  const [msg, setMsg] = useState("");
  const [loading, setLoading] = useState(true);
  const [ehrSource, setEhrSource] = useState("hapi");

  async function load(search = q) {
    setLoading(true);
    try {
      const res = await fetch(
        `${API_BASE}/patients?q=${encodeURIComponent(search)}`,
        { cache: "no-store" },
      );
      const data = await res.json();
      setItems(data.items ?? []);
    } catch {
      setMsg("Could not reach API. Is the backend running on :8000?");
    } finally {
      setLoading(false);
    }
  }

  async function syncEhr() {
    const isLiveHapi = ehrSource === "hapi";
    setMsg(
      isLiveHapi
        ? `Syncing LIVE HAPI FHIR (https://hapi.fhir.org/baseR4) → PostgreSQL (patients, encounters, insurance)…`
        : `Syncing Mock ${ehrSource.toUpperCase()} → PostgreSQL (patients, encounters, insurance)…`,
    );
    const res = await fetch(
      `${API_BASE}/ehr/${ehrSource}/sync/all?mock_only=${!isLiveHapi}`,
      { method: "POST" },
    );
    const data = await res.json();
    setMsg(
      isLiveHapi
        ? `✅ Live HAPI FHIR Sync Complete: ${data.patients?.created ?? 0} created, ${data.patients?.updated ?? 0} updated in PostgreSQL.`
        : `${data.disclaimer ?? "MOCK EHR"} · patients ${JSON.stringify(data.patients)} · Availity maps ${JSON.stringify(data.availity_mappings)}`,
    );
    await load();
  }

  useEffect(() => {
    void load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <AppShell activeHref="/patients">
      <div className="space-y-6">
        <header className="flex flex-wrap items-end justify-between gap-3">
          <div>
            <h2 className="text-2xl font-semibold">Patients</h2>
            <p className="mt-1 text-sm text-slate-600">
              EHR patient roster synced to PostgreSQL. Includes live public HAPI FHIR test patients and simulated Epic/Oracle charts.
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <select
              value={ehrSource}
              onChange={(e) => setEhrSource(e.target.value)}
              className="rounded-md border border-slate-300 px-3 py-2 text-sm font-medium"
            >
              <option value="hapi">HAPI FHIR (Live API: hapi.fhir.org)</option>
              <option value="epic">Mock Epic</option>
              <option value="oracle">Mock Oracle Health</option>
              <option value="mock">Mock FHIR (Generic)</option>
            </select>
            <button
              onClick={() => void syncEhr()}
              className="rounded-md bg-teal-700 px-4 py-2 text-sm font-medium text-white hover:bg-teal-800"
            >
              Sync EHR → Postgres
            </button>
          </div>
        </header>
        <p className="text-xs font-medium text-teal-800 bg-teal-50 border border-teal-200 rounded px-3 py-1.5">
          🌐 <b>Live HAPI FHIR Integration Active:</b> Connects directly to <code>https://hapi.fhir.org/baseR4</code> for Patient, Encounter, and Coverage resources.
        </p>
        <ModuleGuide {...GUIDES.patients} />

        <div className="flex gap-2">
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search name or EHR id"
            className="w-full max-w-sm rounded-md border border-slate-300 px-3 py-2 text-sm"
          />
          <button
            onClick={() => void load()}
            className="rounded-md border border-slate-300 bg-white px-3 py-2 text-sm"
          >
            Search
          </button>
        </div>

        {msg ? <p className="text-xs text-slate-600">{msg}</p> : null}
        {loading ? (
          <p className="text-sm text-slate-500">Loading…</p>
        ) : (
          <DataTable
            headers={["Name", "DOB", "Gender", "Phone", "City", "Source", ""]}
            empty={!items.length}
          >
            {items.map((p) => (
              <tr key={p.id} className="hover:bg-slate-50">
                <td className="px-4 py-3 font-medium">
                  {p.first_name} {p.last_name}
                  <div className="text-xs text-slate-400">
                    {p.external_ehr_patient_id}
                  </div>
                </td>
                <td className="px-4 py-3">{p.date_of_birth ?? "—"}</td>
                <td className="px-4 py-3">{p.gender ?? "—"}</td>
                <td className="px-4 py-3">{p.phone ?? "—"}</td>
                <td className="px-4 py-3">{p.city ?? "—"}</td>
                <td className="px-4 py-3">{p.source}</td>
                <td className="px-4 py-3">
                  <Link
                    href={`/patients/${p.id}`}
                    className="text-teal-700 hover:underline"
                  >
                    Open
                  </Link>
                </td>
              </tr>
            ))}
          </DataTable>
        )}
      </div>
    </AppShell>
  );
}
