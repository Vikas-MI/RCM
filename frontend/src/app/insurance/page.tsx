"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AppShell } from "@/components/layout/AppShell";
import { ModuleGuide } from "@/components/learn/ModuleGuide";
import { GUIDES } from "@/components/learn/guideContent";
import { DataTable } from "@/components/ui/DataTable";
import { API_BASE } from "@/services/api";

type Policy = {
  id: string;
  patient_id: string;
  payer_id: string;
  payer_name?: string;
  member_id: string;
  group_number?: string;
  policy_number?: string;
  coverage_status: string;
  coverage_start_date?: string;
  coverage_end_date?: string;
  is_primary: boolean;
  is_active: boolean;
};

export default function InsurancePage() {
  const [items, setItems] = useState<Policy[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    void (async () => {
      try {
        const res = await fetch(`${API_BASE}/insurance`, { cache: "no-store" });
        const data = await res.json();
        setItems(data.items ?? []);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  return (
    <AppShell activeHref="/insurance">
      <div className="space-y-6">
        <header>
          <h2 className="text-2xl font-semibold">Insurance</h2>
          <p className="mt-1 text-sm text-slate-600">
            Insurance-card details stored for each patient.
          </p>
        </header>
        <ModuleGuide {...GUIDES.insurance} />
        {loading ? (
          <p className="text-sm text-slate-500">Loading…</p>
        ) : (
          <DataTable
            headers={[
              "Payer",
              "Member ID",
              "Status",
              "Dates",
              "Primary",
              "Patient",
            ]}
            empty={!items.length}
          >
            {items.map((p) => (
              <tr key={p.id} className="hover:bg-slate-50">
                <td className="px-4 py-3 font-medium">
                  {p.payer_name ?? p.payer_id.slice(0, 8)}
                </td>
                <td className="px-4 py-3 font-mono text-xs">{p.member_id}</td>
                <td className="px-4 py-3">{p.coverage_status}</td>
                <td className="px-4 py-3 text-xs">
                  {p.coverage_start_date ?? "?"} →{" "}
                  {p.coverage_end_date ?? "open"}
                </td>
                <td className="px-4 py-3">
                  {p.is_primary ? "Yes" : "No"}
                </td>
                <td className="px-4 py-3">
                  <Link
                    href={`/patients/${p.patient_id}`}
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
