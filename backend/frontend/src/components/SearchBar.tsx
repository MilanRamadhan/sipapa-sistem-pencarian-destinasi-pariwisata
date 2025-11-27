"use client";

import { FormEvent, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

export default function SearchBar() {
  const router = useRouter();
  const params = useSearchParams();
  const initial = params.get("q") || "";

  const [query, setQuery] = useState(initial);

  const onSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    router.push(`/search?q=${encodeURIComponent(query)}&algo=tfidf`);
  };

  return (
    <form onSubmit={onSubmit} className="w-full max-w-md">
      <input
        className="w-full border border-neutral-400 rounded-full px-4 py-2 text-sm outline-none focus:ring-2 focus:ring-neutral-800 focus:border-neutral-800 bg-white"
        placeholder="Cari destinasi wisata, kota, atau kata kunci…"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
    </form>
  );
}
