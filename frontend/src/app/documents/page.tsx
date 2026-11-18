"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { ModuleGuide } from "@/components/learn/ModuleGuide";
import { GUIDES } from "@/components/learn/guideContent";
import { DataTable } from "@/components/ui/DataTable";
import { API_BASE } from "@/services/api";

type DocType = { id: string; label: string; eli5: string };
type Doc = {
  id: string;
  filename: string;
  doc_type: string;
  ocr_provider: string;
  ocr_status: string;
  extracted_fields?: Record<string, unknown>;
  notes?: string;
  created_at?: string;
};

export default function DocumentsPage() {
  const [types, setTypes] = useState<DocType[]>([]);
  const [items, setItems] = useState<Doc[]>([]);
  const [docType, setDocType] = useState("insurance_card");
  const [busy, setBusy] = useState(false);
  const [last, setLast] = useState<Doc | null>(null);

  async function load() {
    const [t, d] = await Promise.all([
      fetch(`${API_BASE}/documents/types`).then((r) => r.json()),
      fetch(`${API_BASE}/documents`).then((r) => r.json()),
    ]);
    setTypes(t.types ?? []);
    setItems(d.items ?? []);
  }

  useEffect(() => {
    void load();
  }, []);

  async function runExtract() {
    setBusy(true);
    try {
      const res = await fetch(`${API_BASE}/documents/extract`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          filename: `demo-${docType}.pdf`,
          doc_type: docType,
          use_azure: false,
        }),
      });
      const data = await res.json();
      setLast(data);
      await load();
    } finally {
      setBusy(false);
    }
  }

  return (
    <AppShell activeHref="/documents">
      <div className="space-y-6">
        <header>
          <h2 className="text-2xl font-semibold">Healthcare Documents (OCR)</h2>
          <p className="mt-1 text-sm text-slate-600">
            Read insurance cards, EOBs, and notes into structured fields.
          </p>
        </header>
        <ModuleGuide {...GUIDES.documents} />

        <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h3 className="text-sm font-semibold">Run mock extraction</h3>
          <div className="mt-3 flex flex-wrap items-end gap-3">
            <label className="text-sm">
              <span className="text-slate-500">Document type</span>
              <select
                className="mt-1 block rounded-md border border-slate-300 px-3 py-2"
                value={docType}
                onChange={(e) => setDocType(e.target.value)}
              >
                {types.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.label}
                  </option>
                ))}
              </select>
            </label>
            <button
              onClick={() => void runExtract()}
              disabled={busy}
              className="rounded-md bg-teal-700 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
            >
              {busy ? "Reading…" : "Extract with Mock Azure DI"}
            </button>
          </div>
          <ul className="mt-4 space-y-1 text-xs text-slate-600">
            {types.map((t) => (
              <li key={t.id}>
                <strong>{t.label}:</strong> {t.eli5}
              </li>
            ))}
          </ul>
        </section>

        {last?.extracted_fields ? (
          <section className="rounded-xl border border-teal-200 bg-teal-50/40 p-5">
            <h3 className="text-sm font-semibold">Last extraction fields</h3>
            <pre className="mt-2 overflow-auto rounded-md bg-white p-3 text-xs">
              {JSON.stringify(last.extracted_fields, null, 2)}
            </pre>
            <p className="mt-2 text-xs text-amber-800">{last.notes}</p>
          </section>
        ) : null}

        <DataTable
          headers={["File", "Type", "Provider", "Status", "When"]}
          empty={!items.length}
        >
          {items.map((d) => (
            <tr key={d.id} className="hover:bg-slate-50">
              <td className="px-4 py-3 font-medium">{d.filename}</td>
              <td className="px-4 py-3">{d.doc_type}</td>
              <td className="px-4 py-3 text-xs">{d.ocr_provider}</td>
              <td className="px-4 py-3">{d.ocr_status}</td>
              <td className="px-4 py-3 text-xs">
                {d.created_at ? new Date(d.created_at).toLocaleString() : "—"}
              </td>
            </tr>
          ))}
        </DataTable>
      </div>
    </AppShell>
  );
}
