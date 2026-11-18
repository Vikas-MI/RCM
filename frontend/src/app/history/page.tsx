"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AppShell } from "@/components/layout/AppShell";
import { ModuleGuide } from "@/components/learn/ModuleGuide";
import { GUIDES } from "@/components/learn/guideContent";
import { DataTable } from "@/components/ui/DataTable";
import { API_BASE } from "@/services/api";

type HistoryRow = {
  id: string;
  patient_id: string;
  insurance_policy_id: string;
  eligibility_request_id: string;
  previous_status?: string;
  current_status: string;
  action: string;
  created_at: string;
};

type EligibilityRow = {
  id: string;
  patient_id: string;
  member_id: string;
  request_status: string;
  scenario: string;
  service_date: string;
  requested_at: string;
};

export default function HistoryPage() {
  const [history, setHistory] = useState<HistoryRow[]>([]);
  const [requests, setRequests] = useState<EligibilityRow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    void (async () => {
      try {
        const [h, e] = await Promise.all([
          fetch(`${API_BASE}/eligibility-history`).then((r) => r.json()),
          fetch(`${API_BASE}/eligibility`).then((r) => r.json()),
        ]);
        setHistory(h ?? []);
        setRequests(e.items ?? []);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  return (
    <AppShell activeHref="/history">
      <div className="space-y-6">
        <header>
          <h2 className="text-2xl font-semibold">Eligibility History</h2>
          <p className="mt-1 text-sm text-slate-600">
            A diary of coverage checks you already ran.
          </p>
        </header>
        <ModuleGuide {...GUIDES.history} />

        {loading ? (
          <p className="text-sm text-slate-500">Loading…</p>
        ) : (
          <>
            <section>
              <h3 className="mb-2 text-sm font-semibold">Status change log</h3>
              <DataTable
                headers={[
                  "When",
                  "Action",
                  "Previous",
                  "Current",
                  "Patient",
                ]}
                empty={!history.length}
              >
                {history.map((h) => (
                  <tr key={h.id} className="hover:bg-slate-50">
                    <td className="px-4 py-3 text-xs">
                      {new Date(h.created_at).toLocaleString()}
                    </td>
                    <td className="px-4 py-3">{h.action}</td>
                    <td className="px-4 py-3">{h.previous_status ?? "—"}</td>
                    <td className="px-4 py-3 font-medium">
                      {h.current_status}
                    </td>
                    <td className="px-4 py-3">
                      <Link
                        href={`/patients/${h.patient_id}`}
                        className="text-teal-700 hover:underline"
                      >
                        Open
                      </Link>
                    </td>
                  </tr>
                ))}
              </DataTable>
            </section>

            <section>
              <h3 className="mb-2 text-sm font-semibold">
                All eligibility requests
              </h3>
              <DataTable
                headers={[
                  "When",
                  "Status",
                  "Scenario",
                  "Member",
                  "Service date",
                ]}
                empty={!requests.length}
              >
                {requests.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-50">
                    <td className="px-4 py-3 text-xs">
                      {new Date(r.requested_at).toLocaleString()}
                    </td>
                    <td className="px-4 py-3 font-medium">
                      {r.request_status}
                    </td>
                    <td className="px-4 py-3">{r.scenario}</td>
                    <td className="px-4 py-3 font-mono text-xs">
                      {r.member_id}
                    </td>
                    <td className="px-4 py-3">{r.service_date}</td>
                  </tr>
                ))}
              </DataTable>
            </section>
          </>
        )}
      </div>
    </AppShell>
  );
}
