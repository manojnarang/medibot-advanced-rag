"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useRef, useState } from "react";
import { sendChatMessage, ApiError } from "@/lib/api";
import { clearSession } from "@/lib/auth";
import { ChatMessage, Session } from "@/lib/types";
import MessageBubble from "./MessageBubble";
import RoleBadge from "./RoleBadge";

const WELCOME: Record<string, string> = {
  doctor: "Ask about treatment protocols, the drug formulary, or diagnostic guidelines.",
  nurse: "Ask about nursing procedures, infection control, or general policy questions.",
  billing_executive: "Ask about billing codes, claim procedures, or claims analytics.",
  technician: "Ask about equipment manuals, calibration, or maintenance schedules.",
  admin: "You have access to every collection and analytics across MediAssist.",
};

export default function ChatShell({ session }: { session: Session }) {
  const router = useRouter();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  function logout() {
    clearSession();
    router.push("/login");
  }

  async function submit(e: FormEvent) {
    e.preventDefault();
    const question = input.trim();
    if (!question || sending) return;

    const userMsg: ChatMessage = { id: crypto.randomUUID(), role: "user", text: question };
    const pendingMsg: ChatMessage = { id: crypto.randomUUID(), role: "bot", text: "", pending: true };
    setMessages((prev) => [...prev, userMsg, pendingMsg]);
    setInput("");
    setSending(true);

    try {
      const result = await sendChatMessage(question, session.token);
      setMessages((prev) =>
        prev.map((m) =>
          m.id === pendingMsg.id
            ? {
                ...m,
                pending: false,
                text: result.answer,
                sources: result.sources,
                retrievalType: result.retrieval_type,
              }
            : m
        )
      );
    } catch (err) {
      const message =
        err instanceof ApiError && err.status === 401
          ? "Your session has expired. Please sign in again."
          : "Something went wrong reaching MediBot. Please try again.";
      setMessages((prev) =>
        prev.map((m) => (m.id === pendingMsg.id ? { ...m, pending: false, text: message } : m))
      );
      if (err instanceof ApiError && err.status === 401) {
        clearSession();
      }
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="flex h-full flex-1 flex-col">
      <header className="flex items-center justify-between border-b border-slate-200 bg-white px-6 py-4">
        <div>
          <h1 className="text-lg font-semibold text-slate-900">MediBot</h1>
          <p className="text-xs text-slate-400">MediAssist Health Network assistant</p>
        </div>
        <div className="flex items-center gap-3">
          <RoleBadge role={session.role} />
          <button
            onClick={logout}
            className="rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-medium text-slate-600 transition hover:bg-slate-50"
          >
            Log out
          </button>
        </div>
      </header>

      <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto px-6 py-6">
        {messages.length === 0 && (
          <div className="mx-auto max-w-md rounded-2xl bg-white p-6 text-center shadow-sm ring-1 ring-slate-200">
            <p className="text-sm font-medium text-slate-700">
              Hi {session.displayName.split(" ")[0]}, how can I help?
            </p>
            <p className="mt-1 text-xs text-slate-400">{WELCOME[session.role]}</p>
          </div>
        )}
        {messages.map((m) => (
          <MessageBubble key={m.id} message={m} />
        ))}
      </div>

      <form onSubmit={submit} className="border-t border-slate-200 bg-white px-6 py-4">
        <div className="flex items-center gap-3">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask MediBot a question…"
            className="flex-1 rounded-xl border border-slate-300 px-4 py-2.5 text-sm outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-100"
          />
          <button
            type="submit"
            disabled={sending || !input.trim()}
            className="rounded-xl bg-brand-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
}
