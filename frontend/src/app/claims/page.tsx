"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { ModuleGuide } from "@/components/learn/ModuleGuide";
import { GUIDES } from "@/components/learn/guideContent";
import { DataTable } from "@/components/ui/DataTable";
import { API_BASE } from "@/services/api";

type Denial = {
  id: string;
  denial_code: string;
  denial_reason: string;
  category: string;
  is_appealable: boolean;
};
type Appeal = {
  id: string;
  appeal_status: string;
  appeal_letter?: string;
  policy_citations?: unknown[];
};
type Claim = {
  id: string;
  claim_number: string;
  claim_status: string;
  service_date?: string;
  cpt_codes?: string[];
  billed_amount?: string;
  paid_amount?: string;
  notes?: string;
  denials: Denial[];
  appeals: Appeal[];
};

export default function ClaimsPage() {
  const [items, setItems] = useState<Claim[]>([]);
  const [letter, setLetter] = useState("");
  const [msg, setMsg] = useState("");
  const [busy, setBusy] = useState(false);

  async function load() {
    const res = await fetch(`${API_BASE}/claims`, { cache: "no-store" });
    const data = await res.json();
    setItems(data.items ?? []);
  }

  useEffect(() => {
    void load();
  }, []);

  async function seed() {
    setMsg("Seeding demo claims…");
    await fetch(`${API_BASE}/claims/seed`, { method: "POST" });
    setMsg("Seeded (or already present).");
    await load();
  }

  async function appeal(denialId: string) {
    setBusy(true);
    setLetter("");
    try {
      const res = await fetch(`${API_BASE}/denials/${denialId}/appeal`, {
        method: "POST",
      });
      const data = await res.json();
      setLetter(data.appeal_letter ?? JSON.stringify(data));
      await load();
    } finally {
      setBusy(false);
    }
  }

  return (
    <AppShell activeHref="/claims">
      <div className="space-y-6">
        <header className="flex flex-wrap items-end justify-between gap-3">
          <div>
            <h2 className="text-2xl font-semibold">Claims · Denials · Appeals</h2>
            <p className="mt-1 text-sm text-slate-600">
              Bills sent to insurance, refusals to pay, and letters asking again.
            </p>
          </div>
          <button
            onClick={() => void seed()}
            className="rounded-md border border-slate-300 bg-white px-3 py-2 text-sm"
          >
            Seed demo claims
          </button>
        </header>
        <ModuleGuide {...GUIDES.claims} />
        {msg ? <p className="text-xs text-slate-500">{msg}</p> : null}

        <DataTable
          headers={[
            "Claim #",
            "Status",
            "Service",
            "CPT",
            "Billed",
            "Paid",
            "Denials",
          ]}
          empty={!items.length}
        >
          {items.map((c) => (
            <tr key={c.id} className="hover:bg-slate-50 align-top">
              <td className="px-4 py-3 font-medium">{c.claim_number}</td>
              <td className="px-4 py-3">{c.claim_status}</td>
              <td className="px-4 py-3 text-xs">{c.service_date ?? "—"}</td>
              <td className="px-4 py-3 text-xs">
                {(c.cpt_codes ?? []).join(", ") || "—"}
              </td>
              <td className="px-4 py-3">{c.billed_amount ?? "—"}</td>
              <td className="px-4 py-3">{c.paid_amount ?? "—"}</td>
              <td className="px-4 py-3 text-xs">
                {c.denials?.length
                  ? c.denials.map((d) => (
                      <div key={d.id} className="mb-2">
                        <div>
                          <strong>{d.denial_code}</strong> — {d.denial_reason}
                        </div>
                        {d.is_appealable ? (
                          <button
                            disabled={busy}
                            onClick={() => void appeal(d.id)}
                            className="mt-1 text-teal-700 hover:underline"
                          >
                            Draft AI appeal
                          </button>
                        ) : null}
                      </div>
                    ))
                  : "—"}
                {c.appeals?.length ? (
                  <div className="mt-1 text-slate-500">
                    Appeals: {c.appeals.map((a) => a.appeal_status).join(", ")}
                  </div>
                ) : null}
              </td>
            </tr>
          ))}
        </DataTable>

        {letter ? (
          <section className="rounded-xl border border-teal-200 bg-teal-50/40 p-5">
            <h3 className="text-sm font-semibold">AI appeal letter draft</h3>
            <pre className="mt-2 whitespace-pre-wrap font-sans text-sm text-slate-800">
              {letter}
            </pre>
          </section>
        ) : null}
      </div>
    </AppShell>
  );
}
