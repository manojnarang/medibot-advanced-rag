export interface DemoAccount {
  username: string;
  password: string;
  label: string;
  role: string;
}

// Mirrors backend/app/auth/users.py - for quick-fill convenience on the login screen only.
export const DEMO_ACCOUNTS: DemoAccount[] = [
  { username: "dr.mehta", password: "Doctor@123", label: "Dr. Mehta", role: "Doctor" },
  { username: "nurse.priya", password: "Nurse@123", label: "Nurse Priya", role: "Nurse" },
  { username: "billing.ravi", password: "Billing@123", label: "Ravi Kumar", role: "Billing Executive" },
  { username: "tech.anand", password: "Tech@123", label: "Anand Singh", role: "Technician" },
  { username: "admin.sys", password: "Admin@123", label: "System Admin", role: "Admin" },
];
