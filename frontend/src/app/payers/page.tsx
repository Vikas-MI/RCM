"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { ModuleGuide } from "@/components/learn/ModuleGuide";
import { GUIDES } from "@/components/learn/guideContent";
import { DataTable } from "@/components/ui/DataTable";
import { API_BASE } from "@/services/api";

type Payer = {
  id: string;
  payer_name: string;
  payer_code: string;
  description?: string;
  is_active: boolean;
};

type Mapping = {
  id: string;
  internal_payer_id: string;
  external_payer_identifier: string;
  mapping_source: string;
};

type AvailityPayer = {
  availity_payer_id: string;
  payer_name: string;
  internal_payer_code: string;
};

export default function PayersPage() {
  const [items, setItems] = useState<Payer[]>([]);
  const [mappings, setMappings] = useState<Mapping[]>([]);
  const [availity, setAvaility] = useState<AvailityPayer[]>([]);
  const [msg, setMsg] = useState("");
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    try {
      const [p, m, a] = await Promise.all([
        fetch(`${API_BASE}/payers`).then((r) => r.json()),
        fetch(`${API_BASE}/payer-mappings`).then((r) => r.json()),
        fetch(`${API_BASE}/availity/payers`).then((r) => r.json()),
      ]);
      setItems(p.items ?? []);
      setMappings(m ?? []);
      setAvaility(a.payers ?? []);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, []);

  async function syncAvailityMaps() {
    setMsg("Writing Mock Availity payer IDs into PostgreSQL…");
    const res = await fetch(`${API_BASE}/availity/payers/sync-mappings`, {
      method: "POST",
    });
    const data = await res.json();
    setMsg(`${data.disclaimer ?? ""} · ${JSON.stringify(data)}`);
    await load();
  }

  const availityMaps = mappings.filter((m) => m.mapping_source === "MOCK_AVAILITY");

  return (
    <AppShell activeHref="/payers">
      <div className="space-y-6">
        <header className="flex flex-wrap items-end justify-between gap-3">
          <div>
            <h2 className="text-2xl font-semibold">Payers & Availity ID mapping</h2>
            <p className="mt-1 text-sm text-slate-600">
              Internal payers in Postgres mapped to Mock Availity payer IDs.
            </p>
          </div>
          <button
            onClick={() => void syncAvailityMaps()}
            className="rounded-md bg-teal-700 px-4 py-2 text-sm font-medium text-white"
          >
            Sync Mock Availity mappings
          </button>
        </header>
        <p className="text-xs font-medium text-amber-900">
          MOCK AVAILITY directory — not live Availity supported-payer API.
        </p>
        <ModuleGuide {...GUIDES.payers} />
        {msg ? <p className="text-xs text-slate-600">{msg}</p> : null}
        {loading ? (
          <p className="text-sm text-slate-500">Loading…</p>
        ) : (
          <>
            <DataTable
              headers={["Name", "Internal code", "Description", "Active"]}
              empty={!items.length}
            >
              {items.map((p) => (
                <tr key={p.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-medium">{p.payer_name}</td>
                  <td className="px-4 py-3 font-mono text-xs">{p.payer_code}</td>
                  <td className="px-4 py-3 text-slate-600">
                    {p.description ?? "—"}
                  </td>
                  <td className="px-4 py-3">{p.is_active ? "Yes" : "No"}</td>
                </tr>
              ))}
            </DataTable>

            <section>
              <h3 className="mb-2 text-sm font-semibold">
                Mock Availity payer directory
              </h3>
              <DataTable
                headers={["Availity payer ID", "Name", "Internal code"]}
                empty={!availity.length}
              >
                {availity.map((a) => (
                  <tr key={a.availity_payer_id} className="hover:bg-slate-50">
                    <td className="px-4 py-3 font-mono text-xs">
                      {a.availity_payer_id}
                    </td>
                    <td className="px-4 py-3">{a.payer_name}</td>
                    <td className="px-4 py-3 font-mono text-xs">
                      {a.internal_payer_code}
                    </td>
                  </tr>
                ))}
              </DataTable>
            </section>

            <section>
              <h3 className="mb-2 text-sm font-semibold">
                PostgreSQL mappings (MOCK_AVAILITY)
              </h3>
              <DataTable
                headers={["Availity / external ID", "Source", "Internal payer"]}
                empty={!availityMaps.length}
              >
                {availityMaps.map((m) => (
                  <tr key={m.id} className="hover:bg-slate-50">
                    <td className="px-4 py-3 font-mono text-xs">
                      {m.external_payer_identifier}
                    </td>
                    <td className="px-4 py-3">{m.mapping_source}</td>
                    <td className="px-4 py-3 text-xs text-slate-500">
                      {m.internal_payer_id.slice(0, 8)}…
                    </td>
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
