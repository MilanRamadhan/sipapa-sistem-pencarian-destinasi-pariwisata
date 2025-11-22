"use client";

interface EvaluationMetrics {
  tfidf: {
    runtime: number;
    precision: number;
    recall: number;
    f1: number;
    map: number;
  };
  bm25: {
    runtime: number;
    precision: number;
    recall: number;
    f1: number;
    map: number;
  };
}

interface EvaluationPanelProps {
  metrics: EvaluationMetrics | null;
  isOpen: boolean;
  onClose: () => void;
}

export default function EvaluationPanel({ metrics, isOpen, onClose }: EvaluationPanelProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-60 z-50 flex items-center justify-center p-4">
      <div className="bg-white text-neutral-900 rounded shadow-2xl w-full max-w-3xl overflow-hidden border-4 border-neutral-900">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b-2 border-neutral-900 bg-neutral-50">
          <h2 className="heading-serif text-2xl font-bold uppercase tracking-wider">Hasil Evaluasi Algoritma</h2>
          <button onClick={onClose} className="text-neutral-600 hover:text-neutral-900 transition-colors">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {!metrics ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-4 border-neutral-900"></div>
              <p className="mt-4 text-sm uppercase tracking-wider text-neutral-600">Menghitung metrik evaluasi...</p>
            </div>
          ) : (
            <div className="grid md:grid-cols-2 gap-6">
              {/* TF-IDF */}
              <div className="border-2 border-neutral-300 p-5 bg-neutral-50">
                <h3 className="text-lg font-bold uppercase tracking-wider mb-4 pb-2 border-b-2 border-neutral-900">TF-IDF</h3>
                <div className="space-y-2.5 text-sm">
                  <div className="flex justify-between items-center">
                    <span className="text-neutral-600 uppercase tracking-wide text-xs">Runtime</span>
                    <span className="font-mono font-semibold">{metrics.tfidf.runtime.toFixed(4)} ms</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-neutral-600 uppercase tracking-wide text-xs">Precision</span>
                    <span className="font-mono font-semibold">{metrics.tfidf.precision.toFixed(4)}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-neutral-600 uppercase tracking-wide text-xs">Recall</span>
                    <span className="font-mono font-semibold">{metrics.tfidf.recall.toFixed(4)}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-neutral-600 uppercase tracking-wide text-xs">F1-Score</span>
                    <span className="font-mono font-semibold">{metrics.tfidf.f1.toFixed(4)}</span>
                  </div>
                  <div className="flex justify-between items-center pt-2 border-t border-neutral-300">
                    <span className="text-neutral-600 uppercase tracking-wide text-xs font-bold">Avg Precision</span>
                    <span className="font-mono font-bold text-base">{metrics.tfidf.map.toFixed(4)}</span>
                  </div>
                </div>
              </div>

              {/* BM25 */}
              <div className="border-2 border-neutral-300 p-5 bg-neutral-50">
                <h3 className="text-lg font-bold uppercase tracking-wider mb-4 pb-2 border-b-2 border-neutral-900">BM25</h3>
                <div className="space-y-2.5 text-sm">
                  <div className="flex justify-between items-center">
                    <span className="text-neutral-600 uppercase tracking-wide text-xs">Runtime</span>
                    <span className="font-mono font-semibold">{metrics.bm25.runtime.toFixed(4)} ms</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-neutral-600 uppercase tracking-wide text-xs">Precision</span>
                    <span className="font-mono font-semibold">{metrics.bm25.precision.toFixed(4)}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-neutral-600 uppercase tracking-wide text-xs">Recall</span>
                    <span className="font-mono font-semibold">{metrics.bm25.recall.toFixed(4)}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-neutral-600 uppercase tracking-wide text-xs">F1-Score</span>
                    <span className="font-mono font-semibold">{metrics.bm25.f1.toFixed(4)}</span>
                  </div>
                  <div className="flex justify-between items-center pt-2 border-t border-neutral-300">
                    <span className="text-neutral-600 uppercase tracking-wide text-xs font-bold">Avg Precision</span>
                    <span className="font-mono font-bold text-base">{metrics.bm25.map.toFixed(4)}</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Note jika tidak ada ground truth */}
          {metrics && metrics.tfidf.precision === 0 && metrics.bm25.precision === 0 && (
            <div className="mt-4 bg-amber-50 border-l-4 border-amber-500 p-4">
              <div className="flex items-start">
                <span className="text-amber-600 text-xl mr-3">⚠</span>
                <div className="text-sm text-amber-800">
                  <p className="font-semibold mb-1">Tidak ada ground truth untuk query ini</p>
                  <p className="text-xs">Metrik evaluasi (precision, recall, F1, AP) tidak dapat dihitung tanpa data ground truth. Runtime tetap diukur.</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
