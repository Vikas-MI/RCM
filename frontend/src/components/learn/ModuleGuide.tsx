import Link from "next/link";

export type ModuleGuideProps = {
  title: string;
  plainEnglish: string;
  whyItMatters: string;
  howItWorks?: string;
  nextStep?: { href: string; label: string; reason: string };
  terms?: Array<{ term: string; meaning: string }>;
  mockNote?: string;
  demoTip?: string;
};

export function ModuleGuide({
  title,
  plainEnglish,
  whyItMatters,
  howItWorks,
  nextStep,
  terms,
  mockNote,
  demoTip,
}: ModuleGuideProps) {
  return (
    <section className="rounded-xl border border-sky-200 bg-sky-50/70 p-5 text-sm text-slate-800 shadow-sm">
      <p className="text-xs font-semibold uppercase tracking-wide text-sky-800">
        Plain-English guide · {title}
      </p>
      <p className="mt-2 leading-relaxed">{plainEnglish}</p>

      <div className="mt-4 grid gap-3 md:grid-cols-2">
        <div className="rounded-lg bg-white/80 p-3">
          <p className="text-xs font-semibold uppercase text-slate-500">
            Why it matters
          </p>
          <p className="mt-1 leading-relaxed">{whyItMatters}</p>
        </div>
        {howItWorks ? (
          <div className="rounded-lg bg-white/80 p-3">
            <p className="text-xs font-semibold uppercase text-slate-500">
              What you do here
            </p>
            <p className="mt-1 leading-relaxed">{howItWorks}</p>
          </div>
        ) : null}
      </div>

      {demoTip ? (
        <p className="mt-3 rounded-lg border border-teal-200 bg-teal-50 px-3 py-2 text-teal-900">
          <span className="font-semibold">Try with demo data: </span>
          {demoTip}
        </p>
      ) : null}

      {terms?.length ? (
        <dl className="mt-4 space-y-2">
          <p className="text-xs font-semibold uppercase text-slate-500">
            Words you might not know
          </p>
          {terms.map((t) => (
            <div key={t.term} className="rounded-md bg-white/80 px-3 py-2">
              <dt className="font-medium text-slate-900">{t.term}</dt>
              <dd className="mt-0.5 text-slate-600">{t.meaning}</dd>
            </div>
          ))}
        </dl>
      ) : null}

      {mockNote ? (
        <p className="mt-3 text-xs font-medium text-amber-900">
          Mock / practice data: {mockNote}
        </p>
      ) : null}

      {nextStep ? (
        <p className="mt-4 flex flex-wrap items-center gap-2 border-t border-sky-200 pt-3">
          <span className="text-slate-600">Next step:</span>
          <Link
            href={nextStep.href}
            className="rounded-md bg-teal-700 px-3 py-1.5 text-xs font-medium text-white hover:bg-teal-800"
          >
            {nextStep.label}
          </Link>
          <span className="text-slate-600">{nextStep.reason}</span>
        </p>
      ) : null}
    </section>
  );
}
