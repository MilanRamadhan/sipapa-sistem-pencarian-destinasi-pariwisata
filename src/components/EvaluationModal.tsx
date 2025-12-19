"use client";

import { useState, useEffect } from "react";
import { getAggregateEvaluation, AggregateEvaluationResult } from "@/lib/api";

type Props = {
  isOpen: boolean;
  onClose: () => void;
};

export default function EvaluationModal({ isOpen, onClose }: Props) {
  const [data, setData] = useState<AggregateEvaluationResult | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetchEvaluation();
    }
  }, [isOpen]);

  const fetchEvaluation = async () => {
    setLoading(true);
    const result = await getAggregateEvaluation(20);
    setData(result);
    setLoading(false);
  };

  if (!isOpen) return null;

  const formatPercent = (val: number) => (val * 100).toFixed(4);
  const formatTime = (val: number) => val.toFixed(4);

  const winner = data && data.bm25.mean_ap > data.tfidf.mean_ap ? "BM25" : data && data.tfidf.mean_ap > data.bm25.mean_ap ? "TF-IDF" : "Setara";

  return (
    <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4" onClick={onClose}>
      <div className="bg-white rounded-lg shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="border-b border-neutral-300 p-6 sticky top-0 bg-white">
          <div className="flex items-center justify-between mb-2">
            <h2 className="heading-serif text-3xl font-black uppercase tracking-wider text-blue-600" style={{ fontFamily: "var(--font-playfair)" }}>
              EVALUATION
            </h2>
            <button onClick={onClose} className="text-neutral-500 hover:text-black text-3xl font-light leading-none">
              ×
            </button>
          </div>
          <p className="text-sm text-neutral-600">
            Perbandingan kinerja TF-IDF vs BM25 - Evaluasi agregat dari <strong>{data?.total_queries || "25"} queries</strong>
          </p>
        </div>

        {/* Content */}
        <div className="p-8">
          {loading ? (
            <div className="text-center py-16">
              <div className="inline-block animate-spin rounded-full h-10 w-10 border-4 border-neutral-300 border-t-blue-600"></div>
              <p className="mt-4 text-sm text-neutral-600 font-semibold">Menghitung evaluasi dari {data?.total_queries || "25"} queries...</p>
            </div>
          ) : data ? (
            <>
              {/* Main Table - Simplified like friend's example */}
              <div className="border-2 border-blue-600 rounded-lg overflow-hidden shadow-lg">
                <table className="w-full bg-white">
                  <thead>
                    <tr className="border-b-2 border-blue-600">
                      <th className="text-left px-6 py-4 text-sm font-bold text-neutral-800">Metrik Evaluasi</th>
                      <th className="text-center px-6 py-4 text-sm font-bold text-blue-700">TF-IDF</th>
                      <th className="text-center px-6 py-4 text-sm font-bold text-green-700">BM25</th>
                      <th className="text-center px-6 py-4 text-sm font-bold text-neutral-600">Selisih</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-neutral-200">
                    {/* Mean Precision */}
                    <tr className="hover:bg-blue-50/30 transition-colors">
                      <td className="px-6 py-4">
                        <p className="font-semibold text-base">Mean Precision</p>
                      </td>
                      <td className="px-6 py-4 text-center font-mono text-lg font-semibold text-blue-700">{formatPercent(data.tfidf.mean_precision)}</td>
                      <td className="px-6 py-4 text-center font-mono text-lg font-semibold text-green-700">{formatPercent(data.bm25.mean_precision)}</td>
                      <td className="px-6 py-4 text-center font-mono text-sm text-neutral-600">
                        {data.bm25.mean_precision > data.tfidf.mean_precision ? "+" : ""}
                        {formatPercent(data.bm25.mean_precision - data.tfidf.mean_precision)}
                      </td>
                    </tr>

                    {/* Mean Recall */}
                    <tr className="hover:bg-blue-50/30 transition-colors">
                      <td className="px-6 py-4">
                        <p className="font-semibold text-base">Mean Recall</p>
                      </td>
                      <td className="px-6 py-4 text-center font-mono text-lg font-semibold text-blue-700">{formatPercent(data.tfidf.mean_recall)}</td>
                      <td className="px-6 py-4 text-center font-mono text-lg font-semibold text-green-700">{formatPercent(data.bm25.mean_recall)}</td>
                      <td className="px-6 py-4 text-center font-mono text-sm text-neutral-600">
                        {data.bm25.mean_recall > data.tfidf.mean_recall ? "+" : ""}
                        {formatPercent(data.bm25.mean_recall - data.tfidf.mean_recall)}
                      </td>
                    </tr>

                    {/* Mean F1-Score */}
                    <tr className="hover:bg-blue-50/30 transition-colors">
                      <td className="px-6 py-4">
                        <p className="font-semibold text-base">Mean F1-Score</p>
                      </td>
                      <td className="px-6 py-4 text-center font-mono text-lg font-semibold text-blue-700">{formatPercent(data.tfidf.mean_f1)}</td>
                      <td className="px-6 py-4 text-center font-mono text-lg font-semibold text-green-700">{formatPercent(data.bm25.mean_f1)}</td>
                      <td className="px-6 py-4 text-center font-mono text-sm text-neutral-600">
                        {data.bm25.mean_f1 > data.tfidf.mean_f1 ? "+" : ""}
                        {formatPercent(data.bm25.mean_f1 - data.tfidf.mean_f1)}
                      </td>
                    </tr>

                    {/* MAP (Mean Average Precision) */}
                    <tr className="hover:bg-blue-50/30 transition-colors bg-blue-50/50">
                      <td className="px-6 py-4">
                        <p className="font-bold text-base">Mean Average Precision</p>
                      </td>
                      <td className="px-6 py-4 text-center font-mono text-xl font-black text-blue-700">{formatPercent(data.tfidf.mean_ap)}</td>
                      <td className="px-6 py-4 text-center font-mono text-xl font-black text-green-700">{formatPercent(data.bm25.mean_ap)}</td>
                      <td className="px-6 py-4 text-center font-mono text-sm font-bold text-neutral-700">
                        {data.bm25.mean_ap > data.tfidf.mean_ap ? "+" : ""}
                        {formatPercent(data.bm25.mean_ap - data.tfidf.mean_ap)}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              {/* Analysis Section */}
              <div className="mt-8 p-6 bg-gradient-to-r from-blue-50 to-green-50 rounded-lg border border-blue-200">
                <h3 className="text-sm font-bold uppercase tracking-wider text-neutral-700 mb-3">📊 Analisis Hasil Evaluasi</h3>
                <div className="text-sm text-neutral-700 space-y-2 leading-relaxed">
                  <p>
                    Secara keseluruhan, algoritma <strong className="text-blue-700">{winner}</strong> menunjukkan performa terbaik berdasarkan Mean Average Precision (MAP) dari evaluasi terhadap <strong>{data.total_queries} queries</strong>
                    .
                  </p>
                  <p>
                    <strong>Precision:</strong> Algoritma <strong>{data.bm25.mean_precision > data.tfidf.mean_precision ? "BM25" : "TF-IDF"}</strong> lebih akurat dalam mengidentifikasi dokumen relevan (
                    {formatPercent(Math.max(data.tfidf.mean_precision, data.bm25.mean_precision))}).
                  </p>
                  <p>
                    <strong>Recall:</strong> Algoritma <strong>{data.bm25.mean_recall > data.tfidf.mean_recall ? "BM25" : "TF-IDF"}</strong> lebih lengkap dalam mengembalikan dokumen relevan (
                    {formatPercent(Math.max(data.tfidf.mean_recall, data.bm25.mean_recall))}).
                  </p>
                  <p>
                    <strong>MAP:</strong> Dengan MAP sebesar <strong>{formatPercent(winner === "BM25" ? data.bm25.mean_ap : data.tfidf.mean_ap)}</strong>, algoritma {winner} memiliki kualitas ranking yang lebih baik, artinya dokumen relevan
                    lebih sering muncul di posisi atas hasil pencarian.
                  </p>
                </div>
              </div>
            </>
          ) : (
            <div className="text-center py-12">
              <p className="text-neutral-600">Gagal memuat data evaluasi.</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t-2 border-blue-600 p-5 bg-blue-600/5 text-center">
          <p className="text-xs text-neutral-600 font-medium">
            Evaluasi agregat dari <strong>{data?.total_queries || "25"} queries</strong> · Top-K: <strong>20</strong> · Ground truth dinamis dengan position-based scoring
          </p>
        </div>
      </div>
    </div>
  );
}
