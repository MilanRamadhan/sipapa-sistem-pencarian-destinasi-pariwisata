from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Dict, List, Any

import os
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# --- meta dokumen ---
DOC_META_DF = pd.read_csv(os.path.join(DATA_DIR, "doc_meta.csv"))
DOC_META = {
    int(row["doc_id"]): {
        "doc_id": int(row["doc_id"]),
        "title": row["title"],
        "url": row["url"],
        "doc_len": int(row["doc_len"]),
    }
    for _, row in DOC_META_DF.iterrows()
}

# --- isi artikel (hasil scraping) ---
CORPUS_DF = pd.read_csv(os.path.join(DATA_DIR, "corpus_clean.csv"))
CORPUS_BY_URL = {
    row["url"]: {
        "content_raw": row.get("content_raw", ""),
        "content_clean": row.get("content_clean", ""),
        "image_url": "" if pd.isna(row.get("image_url")) else str(row.get("image_url", "")),
    }
    for _, row in CORPUS_DF.iterrows()
}


# ========= PATH & GLOBAL DATA =========

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

# Stopwords
STOPWORDS_PATH = BASE_DIR / "stopwords_id.txt"
if STOPWORDS_PATH.exists():
    with STOPWORDS_PATH.open("r", encoding="utf-8") as f:
        STOPWORDS = {line.strip().lower() for line in f if line.strip()}
else:
    STOPWORDS = set()

# Optional stemmer (Sastrawi). Kalau tidak ter-install, stemming akan dilewati.
try:
    from Sastrawi.Stemmer.StemmerFactory import StemmerFactory  # type: ignore

    _stemmer = StemmerFactory().create_stemmer()
except Exception:  # fallback kalau tidak ada Sastrawi
    _stemmer = None


def _stem(token: str) -> str:
    if _stemmer is None:
        return token
    try:
        return _stemmer.stem(token)
    except Exception:
        return token


# Load inverted index (struktur fleksibel)
with (DATA_DIR / "inverted_index.json").open("r", encoding="utf-8") as f:
    _raw_index = json.load(f)

INVERTED_INDEX: Dict[str, Dict[int, int]] = {}

for term, postings in _raw_index.items():
    doc_tf: Dict[int, int] = {}

    # Case 1: sudah dict {doc_id: tf}
    if isinstance(postings, dict):
        for doc_id, tf in postings.items():
            doc_tf[int(doc_id)] = int(tf)

    # Case 2: list (bisa list of list / tuple / dict / int)
    elif isinstance(postings, list):
        for item in postings:
            doc_id = None
            tf = 1

            # contoh: [doc_id, tf] atau (doc_id, tf)
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                doc_id, tf = item[0], item[1]

            # contoh: {"doc_id": 5, "tf": 3} atau {"id": 5, "freq": 3}
            elif isinstance(item, dict):
                doc_id = (
                    item.get("doc_id")
                    or item.get("doc")
                    or item.get("id")
                )
                tf = (
                    item.get("tf")
                    or item.get("freq")
                    or item.get("count")
                    or 1
                )

            # contoh: cuma angka doc_id (tf = 1)
            else:
                doc_id = item
                tf = 1

            if doc_id is None:
                continue

            doc_id_int = int(doc_id)
            doc_tf[doc_id_int] = doc_tf.get(doc_id_int, 0) + int(tf)

    INVERTED_INDEX[term] = doc_tf


# Load document metadata
DOC_META_DF = pd.read_csv(DATA_DIR / "doc_meta.csv")
DOC_META_DF = DOC_META_DF.astype({"doc_id": int, "doc_len": int})
DOC_META_MAP: Dict[int, Dict[str, Any]] = {
    int(row.doc_id): {
        "doc_id": int(row.doc_id),
        "url": row.url,
        "title": row.title,
        "doc_len": int(row.doc_len),
    }
    for _, row in DOC_META_DF.iterrows()
}

N: int = len(DOC_META_MAP)
AVGDL: float = float(DOC_META_DF["doc_len"].mean())

# (Opsional) load konten artikel untuk snippet
SCRAPED_PATH = DATA_DIR / "scraped.csv"
CONTENT_BY_URL: Dict[str, str] = {}
if SCRAPED_PATH.exists():
    scraped_df = pd.read_csv(SCRAPED_PATH)
    for _, row in scraped_df.iterrows():
        CONTENT_BY_URL[str(row["url"])] = str(row.get("content", ""))

# Pre-compute DF dan IDF
DF_MAP: Dict[str, int] = {term: len(postings) for term, postings in INVERTED_INDEX.items()}

IDF_TFIDF: Dict[str, float] = {}
IDF_BM25: Dict[str, float] = {}

for term, df in DF_MAP.items():
    df = max(df, 1)  # hindari division by zero
    # TF-IDF classic idf
    IDF_TFIDF[term] = math.log(N / df)
    # BM25 idf
    IDF_BM25[term] = math.log((N - df + 0.5) / (df + 0.5) + 1.0)


# ========= PREPROCESSING =========


def preprocess_query(text: str) -> List[str]:
    text = text.lower()
    # buang URL
    text = re.sub(r"http\S+|www\.\S+", " ", text)
    # hanya huruf/angka dan spasi
    text = re.sub(r"[^0-9a-zA-Z\s]", " ", text)
    # tokenisasi kata
    tokens = re.findall(r"\w+", text)

    # # stopword removal
    # tokens = [t for t in tokens if t not in STOPWORDS]

    # # stemming
    # tokens = [_stem(t) for t in tokens]

    return [t for t in tokens if t]


# ========= CORE SEARCH FUNCTIONS =========


def _rank_to_results(scores: Counter, top_k: int = 20) -> List[Dict[str, Any]]:
    ranked = scores.most_common(top_k)
    results: List[Dict[str, Any]] = []

    for doc_id, score in ranked:
        meta = DOC_META_MAP.get(int(doc_id))
        if not meta:
            continue

        url = meta["url"]
        content = CONTENT_BY_URL.get(url, "")
        snippet = content[:1200] if content else meta["title"]
        
        # Ambil image_url dari CORPUS_BY_URL
        corpus_data = CORPUS_BY_URL.get(url, {})
        image_url = corpus_data.get("image_url", "")

        results.append(
            {
                "doc_id": int(doc_id),
                "title": meta["title"],
                "url": url,
                "doc_len": meta["doc_len"],
                "score": float(score),
                "snippet": snippet,
                "image_url": image_url,
            }
        )

    return results


def tfidf_search(query: str, top_k: int = 20) -> List[Dict[str, Any]]:
    """
    Pencarian menggunakan skor TF-IDF:
        score(q, d) = Σ tf(t, d) × idf(t)
    """
    query_tokens = preprocess_query(query)
    scores: Counter = Counter()

    for term in query_tokens:
        postings = INVERTED_INDEX.get(term)
        if not postings:
            continue

        idf = IDF_TFIDF.get(term, 0.0)
        if idf == 0.0:
            continue

        for doc_id, tf in postings.items():
            scores[doc_id] += tf * idf

    return _rank_to_results(scores, top_k=top_k)


def bm25_search(
    query: str,
    top_k: int = 20,
    k1: float = 1.5,
    b: float = 0.75,
) -> List[Dict[str, Any]]:
    """
    Pencarian menggunakan BM25:
        score(q, d) = Σ idf(t) × [tf(t,d) × (k₁ + 1)] / [tf(t,d) + k₁ × (1 - b + b × |d|/avgdl)]
    """
    query_tokens = preprocess_query(query)
    scores: Counter = Counter()

    for term in query_tokens:
        postings = INVERTED_INDEX.get(term)
        if not postings:
            continue

        idf = IDF_BM25.get(term, 0.0)
        if idf == 0.0:
            continue

        for doc_id, tf in postings.items():
            dl = DOC_META_MAP.get(int(doc_id), {}).get("doc_len", AVGDL)
            denom = tf + k1 * (1.0 - b + b * (dl / AVGDL))
            if denom <= 0:
                continue
            score = idf * (tf * (k1 + 1.0)) / denom
            scores[doc_id] += score

    return _rank_to_results(scores, top_k=top_k)


# ========= METRICS / UTILITIES =========


def get_metrics() -> Dict[str, Any]:
    """
    Baca file evaluation_report.json dan balikin sebagai dict.
    Dipakai buat tampilan perbandingan performa di UI.
    """
    path = DATA_DIR / "evaluation_report.json"
    if not path.exists():
        return {}

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def get_document(doc_id: int):
    """Ambil detail satu dokumen berdasarkan doc_id."""
    doc_id = int(doc_id)
    meta = DOC_META.get(doc_id)
    if not meta:
        return None

    corpus = CORPUS_BY_URL.get(meta["url"], {})
    content = corpus.get("content_raw") or corpus.get("content_clean") or ""
    image_url = corpus.get("image_url", "")

    return {
        "doc_id": doc_id,
        "title": meta["title"],
        "url": meta["url"],
        "doc_len": meta["doc_len"],
        "content": content,
        "image_url": image_url,
    }

