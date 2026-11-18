"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { ModuleGuide } from "@/components/learn/ModuleGuide";
import { GUIDES } from "@/components/learn/guideContent";
import { API_BASE } from "@/services/api";

type Roadmap = {
  eli5: string;
  modules: Array<{ id: string; name: string; status: string }>;
  disclaimer: string;
};

const PROMPTS = [
  "Why was Ava's MRI claim denied and what policy supports an appeal?",
  "Summarize eligibility and documents for Liam",
  "What modules are connected in this Smart RCM assistant?",
];

export default function AssistantPage() {
  const [roadmap, setRoadmap] = useState<Roadmap | null>(null);
  const [question, setQuestion] = useState(PROMPTS[0]);
  const [answer, setAnswer] = useState("");
  const [modules, setModules] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    void fetch(`${API_BASE}/assistant/roadmap`)
      .then((r) => r.json())
      .then(setRoadmap);
  }, []);

  async function ask(q = question) {
    setBusy(true);
    try {
      const res = await fetch(`${API_BASE}/assistant/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q }),
      });
      const data = await res.json();
      setAnswer(data.answer ?? "");
      setModules(data.modules_used ?? []);
    } finally {
      setBusy(false);
    }
  }

  return (
    <AppShell activeHref="/assistant">
      <div className="space-y-6">
        <header>
          <h2 className="text-2xl font-semibold">
            Capstone · End-to-End Smart RCM Assistant
          </h2>
          <p className="mt-1 text-sm text-slate-600">
            One place to ask about the whole Ava Chen demo story.
          </p>
        </header>
        <ModuleGuide {...GUIDES.assistant} />

        {roadmap ? (
          <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
            {roadmap.modules.map((m) => (
              <div
                key={m.id}
                className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm"
              >
                <div className="font-medium">{m.name}</div>
                <div className="text-xs uppercase text-teal-700">{m.status}</div>
              </div>
            ))}
          </div>
        ) : null}

        <div className="flex flex-wrap gap-2">
          {PROMPTS.map((p) => (
            <button
              key={p}
              onClick={() => {
                setQuestion(p);
                void ask(p);
              }}
              className="rounded-full border border-slate-300 bg-white px-3 py-1 text-xs hover:bg-slate-50"
            >
              {p}
            </button>
          ))}
        </div>

        <div className="flex gap-2">
          <input
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
          />
          <button
            onClick={() => void ask()}
            disabled={busy}
            className="rounded-md bg-teal-700 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
          >
            {busy ? "Thinking…" : "Ask capstone"}
          </button>
        </div>

        {modules.length ? (
          <p className="text-xs text-slate-500">
            Modules used: {modules.join(" · ")}
          </p>
        ) : null}

        {answer ? (
          <section className="rounded-xl border border-teal-200 bg-teal-50/40 p-5">
            <pre className="whitespace-pre-wrap font-sans text-sm text-slate-800">
              {answer}
            </pre>
          </section>
        ) : null}

        <p className="text-xs text-amber-800">
          {roadmap?.disclaimer ??
            "All modules use MOCK / synthetic data for learning."}
        </p>
      </div>
    </AppShell>
  );
}
