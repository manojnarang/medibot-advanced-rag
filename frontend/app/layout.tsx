import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MediBot | MediAssist Health Network",
  description: "Role-aware clinical & operational assistant for MediAssist Health Network.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen text-slate-800 antialiased">{children}</body>
    </html>
  );
}
