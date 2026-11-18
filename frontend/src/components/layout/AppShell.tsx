import Link from "next/link";
import type { ReactNode } from "react";

const NAV = [
  { href: "/walkthrough", label: "Start here" },
  { href: "/dashboard", label: "Dashboard" },
  { href: "/patients", label: "Patients" },
  { href: "/encounters", label: "Encounters" },
  { href: "/insurance", label: "Insurance" },
  { href: "/payers", label: "Payers" },
  { href: "/eligibility", label: "Eligibility" },
  { href: "/documents", label: "Documents" },
  { href: "/policy", label: "Policy Copilot" },
  { href: "/claims", label: "Claims" },
  { href: "/assistant", label: "Capstone AI" },
  { href: "/history", label: "History" },
];

export function AppShell({
  children,
  activeHref,
}: {
  children: ReactNode;
  activeHref?: string;
}) {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <div className="border-b border-amber-300 bg-amber-50 px-4 py-2 text-center text-xs font-medium text-amber-950">
        RCM POC sandbox — Mock Epic/Oracle EHR + Mock Availity eligibility. NOT
        live Epic, Oracle Health, or Availity data.
      </div>
      <div className="mx-auto flex min-h-[calc(100vh-36px)] max-w-7xl">
        <aside className="hidden w-56 shrink-0 overflow-y-auto border-r border-slate-200 bg-white p-4 md:block">
          <div className="mb-6">
            <p className="text-xs font-semibold uppercase tracking-wide text-teal-700">
              Smart RCM
            </p>
            <h1 className="text-lg font-semibold text-slate-900">
              Learning lab
            </h1>
            <p className="mt-1 text-xs text-slate-500">
              Follow “Start here” top to bottom
            </p>
            <Link
              href="/walkthrough"
              className="mt-3 inline-block text-xs font-medium text-teal-700 hover:underline"
            >
              Full walkthrough →
            </Link>
          </div>
          <nav className="flex flex-col gap-1">
            {NAV.map((item) => {
              const active = activeHref === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`rounded-md px-3 py-2 text-sm ${
                    active
                      ? "bg-teal-50 font-medium text-teal-800"
                      : "text-slate-600 hover:bg-slate-100"
                  }`}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </aside>
        <main className="flex-1 p-4 md:p-8">{children}</main>
      </div>
    </div>
  );
}
