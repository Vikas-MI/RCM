"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AppShell } from "@/components/layout/AppShell";
import { ModuleGuide } from "@/components/learn/ModuleGuide";
import { GUIDES } from "@/components/learn/guideContent";
import { DataTable } from "@/components/ui/DataTable";
import { API_BASE } from "@/services/api";

type Encounter = {
  id: string;
  patient_id: string;
  external_ehr_encounter_id?: string;
  encounter_type?: string;
  encounter_status?: string;
  encounter_class?: string;
  start_date?: string;
  reason?: string;
};

export default function EncountersPage() {
  const [items, setItems] = useState<Encounter[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    void (async () => {
      try {
        const res = await fetch(`${API_BASE}/encounters`, { cache: "no-store" });
        const data = await res.json();
        setItems(data.items ?? []);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  return (
    <AppShell activeHref="/encounters">
      <div className="space-y-6">
        <header>
          <h2 className="text-2xl font-semibold">Encounters</h2>
          <p className="mt-1 text-sm text-slate-600">
            Visits and appointments tied to a patient and a date.
          </p>
        </header>
        <ModuleGuide {...GUIDES.encounters} />
        {loading ? (
          <p className="text-sm text-slate-500">Loading…</p>
        ) : (
          <DataTable
            headers={[
              "Type",
              "Status",
              "Class",
              "Start",
              "Reason",
              "EHR id",
              "Patient",
            ]}
            empty={!items.length}
          >
            {items.map((e) => (
              <tr key={e.id} className="hover:bg-slate-50">
                <td className="px-4 py-3 font-medium">
                  {e.encounter_type ?? "—"}
                </td>
                <td className="px-4 py-3">{e.encounter_status ?? "—"}</td>
                <td className="px-4 py-3">{e.encounter_class ?? "—"}</td>
                <td className="px-4 py-3">
                  {e.start_date
                    ? new Date(e.start_date).toLocaleString()
                    : "—"}
                </td>
                <td className="px-4 py-3">{e.reason ?? "—"}</td>
                <td className="px-4 py-3 text-xs text-slate-500">
                  {e.external_ehr_encounter_id ?? "—"}
                </td>
                <td className="px-4 py-3">
                  <Link
                    href={`/patients/${e.patient_id}`}
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
