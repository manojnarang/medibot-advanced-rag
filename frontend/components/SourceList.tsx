import { Source } from "@/lib/types";

export default function SourceList({ sources }: { sources: Source[] }) {
  if (sources.length === 0) return null;

  return (
    <details className="mt-2 text-xs">
      <summary className="cursor-pointer select-none font-medium text-brand-700 hover:text-brand-800">
        {sources.length} source{sources.length === 1 ? "" : "s"}
      </summary>
      <ul className="mt-2 space-y-1.5">
        {sources.map((s, idx) => (
          <li key={idx} className="rounded-md bg-slate-50 px-2.5 py-1.5 ring-1 ring-slate-200">
            <span className="font-medium text-slate-700">{s.source_document}</span>
            {s.section_title && <span className="text-slate-500"> — {s.section_title}</span>}
            <span className="ml-1.5 rounded bg-slate-200 px-1.5 py-0.5 text-[10px] uppercase text-slate-600">
              {s.collection}
            </span>
          </li>
        ))}
      </ul>
    </details>
  );
}
