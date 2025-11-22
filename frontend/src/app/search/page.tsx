"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import SearchBar from "@/components/SearchBar";
import SafeImage from "@/components/SafeImage";
import EvaluationPanel from "@/components/EvaluationPanel";
import { Algo, SearchResult, searchArticles } from "@/lib/api";

export default function SearchPage() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const q = searchParams.get("q") || "";
  const algoParam = (searchParams.get("algo") as Algo) || "tfidf";

  const [algo, setAlgo] = useState<Algo>(algoParam);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [showEval, setShowEval] = useState<boolean>(false);
  const [evalMetrics, setEvalMetrics] = useState<any>(null);

  useEffect(() => {
    let cancelled = false;
    async function run() {
      setLoading(true);
      try {
        const data = await searchArticles(q, algo);
        if (!cancelled) setResults(data);
      } catch (e) {
        console.error(e);
        if (!cancelled) setResults([]);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    if (q) run();
    else {
      setResults([]);
      setLoading(false);
    }
    return () => {
      cancelled = true;
    };
  }, [q, algo]);

  const handleAlgoChange = (next: Algo) => {
    setAlgo(next);
    const params = new URLSearchParams(searchParams.toString());
    params.set("algo", next);
    router.replace(`/search?${params.toString()}`);
  };

  const handleShowEvaluation = async () => {
    if (!q) return;

    setShowEval(true);
    setEvalMetrics(null); // Reset saat loading

    try {
      const response = await fetch(`http://localhost:5000/evaluate?query=${encodeURIComponent(q)}&top_k=20`);
      const data = await response.json();

      if (data.tfidf && data.bm25) {
        setEvalMetrics({
          tfidf: {
            runtime: data.tfidf.runtime || 0,
            precision: data.tfidf.precision || 0,
            recall: data.tfidf.recall || 0,
            f1: data.tfidf.f1 || 0,
            map: data.tfidf.ap || 0, // AP untuk single query
          },
          bm25: {
            runtime: data.bm25.runtime || 0,
            precision: data.bm25.precision || 0,
            recall: data.bm25.recall || 0,
            f1: data.bm25.f1 || 0,
            map: data.bm25.ap || 0, // AP untuk single query
          },
        });
      } else {
        // Fallback jika tidak ada ground truth
        setEvalMetrics({
          tfidf: {
            runtime: 0,
            precision: 0,
            recall: 0,
            f1: 0,
            map: 0,
          },
          bm25: {
            runtime: 0,
            precision: 0,
            recall: 0,
            f1: 0,
            map: 0,
          },
        });
      }
    } catch (error) {
      console.error("Error fetching evaluation:", error);
      // Gunakan dummy data jika API gagal
      setEvalMetrics({
        tfidf: {
          runtime: 0,
          precision: 0,
          recall: 0,
          f1: 0,
          map: 0,
        },
        bm25: {
          runtime: 0,
          precision: 0,
          recall: 0,
          f1: 0,
          map: 0,
        },
      });
    }
  };

  return (
    <main className="min-h-screen bg-neutral-50 text-neutral-900">
      <div className="max-w-5xl mx-auto px-4 py-6">
        {/* Header bar */}
        <header className="border-b border-neutral-300 pb-4 mb-6">
          <div className="flex items-center justify-between gap-4 mb-3">
            <a href="/" className="heading-serif text-3xl font-black tracking-tight hover:opacity-80 transition-opacity" style={{ fontFamily: "var(--font-playfair)" }}>
              Sipapa Travel Times
            </a>
            <div className="hidden md:block w-72">
              <SearchBar />
            </div>
          </div>

          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-4">
              <button onClick={() => router.push("/")} className="text-[11px] uppercase tracking-[0.16em] text-neutral-600 hover:text-neutral-900 flex items-center gap-1 transition-colors">
                ← Dashboard
              </button>
              <div className="text-xs uppercase tracking-[0.18em] text-neutral-600">
                Hasil untuk:
                <span className="ml-2 text-neutral-900">{q || "—"}</span>
              </div>
            </div>

            {/* Toggle algoritma & Tombol Evaluasi */}
            <div className="flex gap-2 text-[11px] uppercase tracking-[0.16em]">
              <button
                onClick={() => handleAlgoChange("tfidf")}
                className={`px-3 py-1 border rounded-full transition-all ${algo === "tfidf" ? "border-neutral-900 bg-neutral-900 text-neutral-50" : "border-neutral-300 text-neutral-700 hover:border-neutral-500"}`}
              >
                TF-IDF
              </button>
              <button
                onClick={() => handleAlgoChange("bm25")}
                className={`px-3 py-1 border rounded-full transition-all ${algo === "bm25" ? "border-neutral-900 bg-neutral-900 text-neutral-50" : "border-neutral-300 text-neutral-700 hover:border-neutral-500"}`}
              >
                BM25
              </button>
              <button
                onClick={handleShowEvaluation}
                className="px-4 py-1.5 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-full hover:from-indigo-700 hover:to-purple-700 transition-all shadow-md hover:shadow-lg transform hover:scale-105 flex items-center gap-1"
              >
                <span>📊</span>
                <span>Evaluasi</span>
              </button>
            </div>
          </div>
        </header>

        {/* Content */}
        {!q && <p className="text-sm text-neutral-600">Masukkan kata kunci pada kotak pencarian di atas untuk mulai mencari artikel destinasi wisata.</p>}

        {q && loading && <p className="text-sm text-neutral-600">Memuat hasil pencarian…</p>}

        {q && !loading && results.length === 0 && <p className="text-sm text-neutral-600">Tidak ada hasil ditemukan untuk kata kunci tersebut.</p>}

        {q && !loading && results.length > 0 && (
          <section className="space-y-6">
            {results.map((item) => (
              <article key={item.doc_id} className="border-b border-neutral-200 pb-4">
                <div className="flex gap-4">
                  {item.image_url && (
                    <div className="flex-shrink-0 w-32 h-24 overflow-hidden rounded-sm">
                      <SafeImage src={item.image_url} alt={item.title} className="w-full h-full object-cover" />
                    </div>
                  )}
                  <div className="flex-1 min-w-0">
                    <p className="text-[10px] uppercase tracking-[0.18em] text-neutral-500 mb-1">Travel · {algo.toUpperCase()}</p>
                    <a href={`/detail/${item.doc_id}`} className="heading-serif text-xl font-semibold leading-snug hover:underline cursor-pointer block">
                      {item.title}
                    </a>

                    <p className="text-xs text-neutral-600 mt-2 line-clamp-3">
                      {item.snippet.slice(0, 260)}
                      {item.snippet.length > 260 && "…"}
                    </p>
                    <div className="mt-2 flex items-center justify-between text-[11px] text-neutral-500">
                      <span className="truncate max-w-xs">{item.url.replace(/^https?:\/\//, "")}</span>
                      <a href={`/detail/${item.doc_id}`} className="text-blue-700 uppercase tracking-[0.16em] hover:text-blue-900 hover:underline">
                        Selengkapnya →
                      </a>
                    </div>
                  </div>
                </div>
              </article>
            ))}
          </section>
        )}
      </div>

      {/* Evaluation Panel */}
      <EvaluationPanel metrics={evalMetrics} isOpen={showEval} onClose={() => setShowEval(false)} />
    </main>
  );
}
