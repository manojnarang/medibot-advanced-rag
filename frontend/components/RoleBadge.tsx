import { ROLE_META } from "@/lib/roles";
import { Role } from "@/lib/types";

export default function RoleBadge({ role }: { role: Role }) {
  const { label, badgeClassName } = ROLE_META[role];
  return (
    <span
      className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ring-1 ring-inset ${badgeClassName}`}
    >
      {label}
    </span>
  );
}
