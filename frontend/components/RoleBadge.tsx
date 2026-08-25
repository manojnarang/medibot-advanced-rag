const ROLE_STYLES: Record<string, string> = {
  doctor: "bg-sky-100 text-sky-800 ring-sky-300",
  nurse: "bg-emerald-100 text-emerald-800 ring-emerald-300",
  billing_executive: "bg-amber-100 text-amber-800 ring-amber-300",
  technician: "bg-violet-100 text-violet-800 ring-violet-300",
  admin: "bg-rose-100 text-rose-800 ring-rose-300",
};

const ROLE_LABELS: Record<string, string> = {
  doctor: "Doctor",
  nurse: "Nurse",
  billing_executive: "Billing Executive",
  technician: "Technician",
  admin: "Admin",
};

export default function RoleBadge({ role }: { role: string }) {
  const style = ROLE_STYLES[role] ?? "bg-slate-100 text-slate-700 ring-slate-300";
  const label = ROLE_LABELS[role] ?? role;
  return (
    <span className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ring-1 ring-inset ${style}`}>
      {label}
    </span>
  );
}
