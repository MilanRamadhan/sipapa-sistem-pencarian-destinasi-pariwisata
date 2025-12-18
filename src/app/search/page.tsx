import { Suspense } from "react";
import SearchPageClient from "./SearchPageClient";

export default function SearchPage() {
  return (
    <Suspense
      fallback={
        <main className="min-h-screen bg-neutral-50 text-neutral-900">
          <div className="max-w-4xl mx-auto px-4 py-8">
            <p className="text-sm text-neutral-600">
              Memuat hasil pencarian...
            </p>
          </div>
        </main>
      }
    >
      <SearchPageClient />
    </Suspense>
  );
}
