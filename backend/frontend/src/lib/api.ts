// frontend/src/lib/api.ts

export type Algo = "tfidf" | "bm25";

export type SearchResult = {
  doc_id: number;
  title: string;
  url: string;
  snippet: string;
  score: number;
  doc_len?: number;
  image_url?: string;
};

const BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:5000";

export async function searchArticles(query: string, algo: Algo = "tfidf", topK: number = 20): Promise<SearchResult[]> {
  if (!query.trim()) return [];

  const params = new URLSearchParams({
    query,
    algo,
    top_k: String(topK),
  });

  const res = await fetch(`${BASE_URL}/search?${params.toString()}`, {
    cache: "no-store",
  });

  if (!res.ok) {
    throw new Error("Failed to fetch search results");
  }

  return res.json();
}

export async function getDocument(id?: string | number | null) {
  if (!id || id === "undefined") {
    return null;
  }

  const res = await fetch(`${BASE_URL}/document/${id}`, {
    cache: "no-store",
  });

  if (!res.ok) {
    console.warn("Failed to fetch document", id, res.status, res.statusText);
    return null;
  }

  return res.json();
}
