"use client";

import { useRouter } from "next/navigation";

function BackButton() {
  const router = useRouter();

  return (
    <button onClick={() => router.back()} className="text-xs uppercase tracking-[0.16em] text-neutral-600 hover:text-neutral-900 transition-colors">
      ← Kembali
    </button>
  );
}

export default BackButton;
