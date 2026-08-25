"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import ChatShell from "@/components/ChatShell";
import Sidebar from "@/components/Sidebar";
import { getSession } from "@/lib/auth";
import { Session } from "@/lib/types";

export default function ChatPage() {
  const router = useRouter();
  const [session, setSession] = useState<Session | null>(null);
  const [checked, setChecked] = useState(false);

  useEffect(() => {
    const s = getSession();
    if (!s) {
      router.replace("/login");
      return;
    }
    setSession(s);
    setChecked(true);
  }, [router]);

  if (!checked || !session) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-brand-300 border-t-brand-600" />
      </div>
    );
  }

  return (
    <div className="flex h-screen">
      <Sidebar session={session} />
      <ChatShell session={session} />
    </div>
  );
}
