"use client";

import { useEffect, useState } from "react";
import { getCollections } from "@/lib/api";
import { CollectionInfo, Session } from "@/lib/types";
import RoleBadge from "./RoleBadge";

export default function Sidebar({ session }: { session: Session }) {
  const [collections, setCollections] = useState<CollectionInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(false);

  useEffect(() => {
    let cancelled = false;
    getCollections(session.role, session.token)
      .then((res) => {
        if (!cancelled) setCollections(res.accessible_collections);
      })
      .catch(() => {
        if (!cancelled) setLoadError(true);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [session.role, session.token]);

  return (
    <aside className="flex h-full w-72 flex-col border-r border-slate-200 bg-white">
      <div className="border-b border-slate-200 p-5">
        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-brand-600 text-sm font-bold text-white">
          M
        </div>
        <h2 className="mt-3 text-sm font-semibold text-slate-900">{session.displayName}</h2>
        <p className="text-xs text-slate-400">{session.department}</p>
        <div className="mt-2">
          <RoleBadge role={session.role} />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-5">
        <h3 className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-400">
          Your accessible collections
        </h3>
        {loading && <p className="text-xs text-slate-400">Loading…</p>}
        {!loading && loadError && (
          <p className="text-xs text-red-500">Couldn&apos;t load your collections. Try refreshing.</p>
        )}
        {!loading && !loadError && collections.length === 0 && (
          <p className="text-xs text-slate-400">No collections available.</p>
        )}
        <ul className="space-y-3">
          {collections.map((c) => (
            <li key={c.name} className="rounded-lg bg-slate-50 p-3 ring-1 ring-slate-200">
              <p className="text-sm font-medium text-slate-800">{c.label}</p>
              <p className="mt-0.5 text-xs text-slate-500">{c.description}</p>
              {c.documents.length > 0 && (
                <p className="mt-1.5 text-[11px] text-slate-400">
                  {c.documents.length} document{c.documents.length === 1 ? "" : "s"}
                </p>
              )}
            </li>
          ))}
        </ul>
      </div>
    </aside>
  );
}
