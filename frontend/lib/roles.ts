import { Role } from "./types";

/**
 * Single source of truth for role display metadata (label, badge color,
 * chat welcome text). Keyed by the Role union itself, not a loose string,
 * so a missing or misspelled role is a compile error here rather than a
 * silent runtime fallback in whichever component happens to use it.
 */
export interface RoleMeta {
  label: string;
  badgeClassName: string;
  welcome: string;
}

export const ROLE_META: Record<Role, RoleMeta> = {
  doctor: {
    label: "Doctor",
    badgeClassName: "bg-sky-100 text-sky-800 ring-sky-300",
    welcome: "Ask about treatment protocols, the drug formulary, or diagnostic guidelines.",
  },
  nurse: {
    label: "Nurse",
    badgeClassName: "bg-emerald-100 text-emerald-800 ring-emerald-300",
    welcome: "Ask about nursing procedures, infection control, or general policy questions.",
  },
  billing_executive: {
    label: "Billing Executive",
    badgeClassName: "bg-amber-100 text-amber-800 ring-amber-300",
    welcome: "Ask about billing codes, claim procedures, or claims analytics.",
  },
  technician: {
    label: "Technician",
    badgeClassName: "bg-violet-100 text-violet-800 ring-violet-300",
    welcome: "Ask about equipment manuals, calibration, or maintenance schedules.",
  },
  admin: {
    label: "Admin",
    badgeClassName: "bg-rose-100 text-rose-800 ring-rose-300",
    welcome: "You have access to every collection and analytics across MediAssist.",
  },
};

export interface DemoAccount {
  username: string;
  password: string;
  displayName: string;
  role: Role;
}

// Mirrors backend/app/auth/users.py - for quick-fill convenience on the login screen only.
export const DEMO_ACCOUNTS: DemoAccount[] = [
  { username: "dr.mehta", password: "Doctor@123", displayName: "Dr. Mehta", role: "doctor" },
  { username: "nurse.priya", password: "Nurse@123", displayName: "Nurse Priya", role: "nurse" },
  {
    username: "billing.ravi",
    password: "Billing@123",
    displayName: "Ravi Kumar",
    role: "billing_executive",
  },
  { username: "tech.anand", password: "Tech@123", displayName: "Anand Singh", role: "technician" },
  { username: "admin.sys", password: "Admin@123", displayName: "System Admin", role: "admin" },
];
