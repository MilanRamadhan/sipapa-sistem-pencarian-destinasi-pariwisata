# backend/api/search.py
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import math
from collections import defaultdict

with open("data/inverted_index.json", "r", encoding="utf-8") as f:
    INVERTED_INDEX = json.load(f)

with open("data/doc_meta.csv", "r", encoding="utf-8") as f:
    # parse csv manual, isi DOC_META = {doc_id: {title, url, ...}}
    DOC_META = {}  # isi sendiri

N_DOCS = len(DOC_META)

def bm25_score(query_terms):
    scores = defaultdict(float)
    # TODO: sesuaikan dengan struktur inverted_index.json kamu
    for term in query_terms:
        postings = INVERTED_INDEX.get(term, [])
        # hitung idf, tf, dll
        # scores[doc_id] += ...
    # convert & sort
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    results = []
    for doc_id, score in ranked[:20]:
        meta = DOC_META.get(doc_id, {})
        results.append({
            "id": doc_id,
            "title": meta.get("title", doc_id),
            "url": meta.get("url", "#"),
            "score": score,
        })
    return results

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        q = params.get("q", [""])[0].strip()
        if not q:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'{"error":"q is required"}')
            return

        query_terms = q.lower().split()
        results = bm25_score(query_terms)

        body = json.dumps(results, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(body)
