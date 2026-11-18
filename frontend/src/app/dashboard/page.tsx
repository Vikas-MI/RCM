"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { StatCard } from "@/components/dashboard/StatCard";
import { ModuleGuide } from "@/components/learn/ModuleGuide";
import { GUIDES } from "@/components/learn/guideContent";
import { API_BASE } from "@/services/api";

type Metrics = {
  patients: number;
  encounters: number;
  insurance_policies: number;
  eligibility_verifications: number;
  documents?: number;
  claims?: number;
  denials?: number;
  appeals?: number;
  active_eligibility: number;
  inactive_eligibility: number;
  pending_eligibility: number;
  recent_activity: Array<{
    id: string;
    status: string;
    scenario: string;
    member_id: string;
    requested_at: string;
  }>;
  disclaimer: string;
};

type Health = {
  status: string;
  app: string;
  env: string;
  database: { connected: boolean };
};

type Integrations = {
  ehr?: {
    epic?: { mode: string; live: boolean };
    oracle_health?: { mode: string; live: boolean };
    hapi_fhir?: { mode: string; base_url?: string };
  };
  eligibility_provider?: { active: string; status: string };
  availity?: { mode?: string; live?: boolean; enabled?: boolean; note?: string };
  disclaimer?: string;
  hapi_fhir?: { base_url: string };
};

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [health, setHealth] = useState<Health | null>(null);
  const [integrations, setIntegrations] = useState<Integrations | null>(null);

  useEffect(() => {
    void (async () => {
      try {
        const [m, h, i] = await Promise.all([
          fetch(`${API_BASE}/dashboard/metrics`, { cache: "no-store" }).then((r) =>
            r.json(),
          ),
          fetch(`${API_BASE}/health`, { cache: "no-store" }).then((r) => r.json()),
          fetch(`${API_BASE}/integrations/status`, { cache: "no-store" }).then((r) =>
            r.json(),
          ),
        ]);
        setMetrics(m);
        setHealth(h);
        setIntegrations(i);
      } catch {
        /* API down */
      }
    })();
  }, []);

  return (
    <AppShell activeHref="/dashboard">
      <div className="space-y-6">
        <header>
          <h2 className="text-2xl font-semibold text-slate-900">Dashboard</h2>
          <p className="mt-1 text-sm text-slate-600">
            The scoreboard for the whole practice sandbox.
          </p>
        </header>
        <ModuleGuide {...GUIDES.dashboard} />

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard label="Patients" value={String(metrics?.patients ?? "—")} />
          <StatCard
            label="Encounters"
            value={String(metrics?.encounters ?? "—")}
          />
          <StatCard
            label="Insurance policies"
            value={String(metrics?.insurance_policies ?? "—")}
          />
          <StatCard
            label="Eligibility checks"
            value={String(metrics?.eligibility_verifications ?? "—")}
          />
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard
            label="Documents (OCR)"
            value={String(metrics?.documents ?? 0)}
          />
          <StatCard label="Claims" value={String(metrics?.claims ?? 0)} />
          <StatCard label="Denials" value={String(metrics?.denials ?? 0)} />
          <StatCard label="Appeals" value={String(metrics?.appeals ?? 0)} />
        </div>

        <div className="grid gap-4 sm:grid-cols-3">
          <StatCard
            label="Active (mock)"
            value={String(metrics?.active_eligibility ?? 0)}
          />
          <StatCard
            label="Inactive/Terminated"
            value={String(metrics?.inactive_eligibility ?? 0)}
          />
          <StatCard
            label="Pending"
            value={String(metrics?.pending_eligibility ?? 0)}
          />
        </div>

        <div className="grid gap-4 lg:grid-cols-2">
          <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <h3 className="text-sm font-semibold">Backend health</h3>
            <dl className="mt-3 space-y-2 text-sm">
              <div className="flex justify-between">
                <dt className="text-slate-500">API status</dt>
                <dd className="font-medium capitalize">
                  {health?.status ?? "—"}
                </dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-slate-500">App</dt>
                <dd>{health?.app ?? "—"}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-slate-500">Environment</dt>
                <dd>{health?.env ?? "—"}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-slate-500">PostgreSQL</dt>
                <dd>
                  {health?.database?.connected ? "Connected" : "Not connected"}
                </dd>
              </div>
            </dl>
          </section>

          <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <h3 className="text-sm font-semibold">Integrations (all mock)</h3>
            <dl className="mt-3 space-y-2 text-sm">
              <div className="flex justify-between gap-2">
                <dt className="text-slate-500">Epic</dt>
                <dd>{integrations?.ehr?.epic?.mode ?? "MOCK"} (not live)</dd>
              </div>
              <div className="flex justify-between gap-2">
                <dt className="text-slate-500">Oracle Health</dt>
                <dd>
                  {integrations?.ehr?.oracle_health?.mode ?? "MOCK"} (not live)
                </dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-slate-500">Availity</dt>
                <dd>
                  {integrations?.availity?.mode ?? "MOCK"} — simulated 270/271
                </dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-slate-500">Eligibility engine</dt>
                <dd className="uppercase">
                  {integrations?.eligibility_provider?.active ?? "MOCK_AVAILITY"}
                </dd>
              </div>
            </dl>
            <p className="mt-3 text-xs text-amber-900">
              {integrations?.disclaimer ??
                "Simulated integrations only — not live Epic, Oracle Health, or Availity."}
            </p>
          </section>
        </div>

        <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h3 className="text-sm font-semibold text-slate-900">
            Recent eligibility activity
          </h3>
          {metrics?.recent_activity?.length ? (
            <ul className="mt-3 space-y-2 text-sm">
              {metrics.recent_activity.map((a) => (
                <li
                  key={a.id}
                  className="flex flex-wrap items-center justify-between gap-2 rounded-md bg-slate-50 px-3 py-2"
                >
                  <span>
                    <strong>{a.status}</strong> · {a.scenario} · {a.member_id}
                  </span>
                  <span className="text-xs text-slate-500">
                    {new Date(a.requested_at).toLocaleString()}
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="mt-3 text-sm text-slate-500">
              No eligibility checks yet. Go to Eligibility and run a mock
              scenario.
            </p>
          )}
          <p className="mt-4 text-xs font-medium text-amber-800">
            {metrics?.disclaimer ??
              "MOCK DATA – NOT REAL INSURANCE VERIFICATION"}
          </p>
        </section>
      </div>
    </AppShell>
  );
}
