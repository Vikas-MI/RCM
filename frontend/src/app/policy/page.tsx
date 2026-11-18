"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { ModuleGuide } from "@/components/learn/ModuleGuide";
import { GUIDES } from "@/components/learn/guideContent";
import { API_BASE } from "@/services/api";

type Chunk = {
  id: string;
  title: string;
  policy_id: string;
  category: string;
};
type Citation = {
  title: string;
  policy_id: string;
  score: number;
  snippet: string;
};

const SUGGESTIONS = [
  "When is MRI for low back pain covered?",
  "What does denial CO-50 medical necessity mean?",
  "How do I write a strong appeal letter?",
  "Is outpatient physical therapy covered?",
];

export default function PolicyPage() {
  const [chunks, setChunks] = useState<Chunk[]>([]);
  const [question, setQuestion] = useState(SUGGESTIONS[0]);
  const [answer, setAnswer] = useState("");
  const [citations, setCitations] = useState<Citation[]>([]);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    void fetch(`${API_BASE}/policy/corpus`)
      .then((r) => r.json())
      .then((d) => setChunks(d.chunks ?? []));
  }, []);

  async function ask(q = question) {
    setBusy(true);
    try {
      const res = await fetch(`${API_BASE}/policy/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q, top_k: 3 }),
      });
      const data = await res.json();
      setAnswer(data.answer ?? "");
      setCitations(data.citations ?? []);
    } finally {
      setBusy(false);
    }
  }

  return (
    <AppShell activeHref="/policy">
      <div className="space-y-6">
        <header>
          <h2 className="text-2xl font-semibold">CMS Policy Copilot (RAG)</h2>
          <p className="mt-1 text-sm text-slate-600">
            Ask coverage-rule questions and get answers with citations.
          </p>
        </header>
        <ModuleGuide {...GUIDES.policy} />

        <div className="flex flex-wrap gap-2">
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              onClick={() => {
                setQuestion(s);
                void ask(s);
              }}
              className="rounded-full border border-slate-300 bg-white px-3 py-1 text-xs hover:bg-slate-50"
            >
              {s}
            </button>
          ))}
        </div>

        <div className="flex gap-2">
          <input
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask about coverage rules…"
          />
          <button
            onClick={() => void ask()}
            disabled={busy}
            className="rounded-md bg-teal-700 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
          >
            {busy ? "Searching…" : "Ask"}
          </button>
        </div>

        {answer ? (
          <section className="rounded-xl border border-teal-200 bg-teal-50/40 p-5">
            <h3 className="text-sm font-semibold">Answer</h3>
            <pre className="mt-2 whitespace-pre-wrap font-sans text-sm text-slate-800">
              {answer}
            </pre>
            <div className="mt-4 space-y-2">
              {citations.map((c) => (
                <div
                  key={c.policy_id + c.score}
                  className="rounded-md bg-white p-3 text-xs"
                >
                  <div className="font-medium">
                    {c.policy_id} · score {c.score}
                  </div>
                  <div className="text-slate-500">{c.title}</div>
                  <p className="mt-1 text-slate-700">{c.snippet}</p>
                </div>
              ))}
            </div>
          </section>
        ) : null}

        <section>
          <h3 className="mb-2 text-sm font-semibold">
            Policy corpus (vector store contents)
          </h3>
          <ul className="grid gap-2 sm:grid-cols-2">
            {chunks.map((c) => (
              <li
                key={c.id}
                className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm"
              >
                <div className="font-medium">{c.title}</div>
                <div className="text-xs text-slate-500">
                  {c.policy_id} · {c.category}
                </div>
              </li>
            ))}
          </ul>
        </section>
      </div>
    </AppShell>
  );
}
