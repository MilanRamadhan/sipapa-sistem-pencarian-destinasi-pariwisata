from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import csv
import math
from collections import defaultdict

# ====================================================
# LOAD INVERTED INDEX
# ====================================================
with open("data/inverted_index.json", "r", encoding="utf-8") as f:
    INVERTED_INDEX = json.load(f)

# ====================================================
# LOAD DOCUMENT METADATA
# Format CSV harus:
# id,title,url
# ====================================================
DOC_META = {}
with open("data/doc_meta.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        DOC_META[row["id"]] = {
            "title": row.get("title", "Untitled"),
            "url": row.get("url", "#"),
        }

TOTAL_DOCS = len(DOC_META)


# ====================================================
# SIMPLE BM25-LIKE SCORING (PURE PYTHON)
# ====================================================
def bm25_score(query_terms):
    scores = defaultdict(float)

    # Hyperparameter BM25 versi ringan
    k1 = 1.5
    b = 0.75

    # Hitung doc length
    doc_lengths = {}
    total_length = 0
    for term, postings in INVERTED_INDEX.items():
        for doc_id, freq in postings:
            doc_lengths[doc_id] = doc_lengths.get(doc_id, 0) + freq
            total_length += freq

    avg_dl = total_length / TOTAL_DOCS if TOTAL_DOCS else 1

    # Loop tiap term di query
    for term in query_terms:
        if term not in INVERTED_INDEX:
            continue

        postings = INVERTED_INDEX[term]
        df = len(postings)

        # idf sederhana
        idf = math.log((TOTAL_DOCS - df + 0.5) / (df + 0.5) + 1)

        # Loop tiap dokumen yang mengandung term
        for doc_id, freq in postings:
            dl = doc_lengths.get(doc_id, 1)
            tf = freq

            # BM25 formula simplified
            score = idf * ((tf * (k1 + 1)) /
                           (tf + k1 * (1 - b + b * (dl / avg_dl))))
            scores[doc_id] += score

    # Sort by score
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    results = []
    for doc_id, score in ranked[:20]:  # top 20 results
        meta = DOC_META.get(doc_id, {})
        results.append({
            "id": doc_id,
            "title": meta.get("title", "Untitled"),
            "url": meta.get("url", "#"),
            "score": score
        })

    return results


# ====================================================
# HTTP HANDLER (VERCEL SERVERLESS)
# ====================================================
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        q = params.get("q", [""])[0].strip()

        if not q:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error":"Query parameter q is required"}')
            return

        query_terms = q.lower().split()
        results = bm25_score(query_terms)

        body = json.dumps(results, ensure_ascii=False).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(body)
