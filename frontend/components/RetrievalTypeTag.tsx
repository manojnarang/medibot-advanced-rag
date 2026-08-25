import { RetrievalType } from "@/lib/types";

const CONFIG: Record<RetrievalType, { label: string; className: string }> = {
  hybrid_rag: { label: "Hybrid RAG", className: "bg-brand-50 text-brand-700 ring-brand-200" },
  sql_rag: { label: "SQL RAG", className: "bg-indigo-50 text-indigo-700 ring-indigo-200" },
  rbac_blocked: { label: "Access Restricted", className: "bg-red-50 text-red-700 ring-red-200" },
};

export default function RetrievalTypeTag({ type }: { type: RetrievalType }) {
  const cfg = CONFIG[type];
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-[11px] font-medium ring-1 ring-inset ${cfg.className}`}>
      {cfg.label}
    </span>
  );
}
