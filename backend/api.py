from flask import Flask, request, jsonify
from flask_cors import CORS

from search_engine import (
    tfidf_search,
    bm25_search,
    get_metrics,
    get_document,
)
from evaluator import evaluate_query_both_algos

app = Flask(__name__)
CORS(app)  # Penting biar frontend (Next.js) bisa akses backend


# ===============================
# Root Test Endpoint
# ===============================
@app.get("/")
def index():
    return jsonify({
        "message": "Sipapa Search Engine API is running!",
        "endpoints": [
            "/search",
            "/metrics",
            "/document/<doc_id>",
            "/evaluate",
        ]
    })


# ===============================
# Search Endpoint
# ===============================
@app.get("/search")
def search():
    query = request.args.get("query", "").strip()
    algo = request.args.get("algo", "tfidf").lower()
    top_k = int(request.args.get("top_k", 20))

    if not query:
        return jsonify([])

    if algo == "bm25":
        results = bm25_search(query, top_k=top_k)
    else:
        results = tfidf_search(query, top_k=top_k)

    return jsonify(results)


# ===============================
# Metrics Endpoint
# ===============================
@app.get("/metrics")
def metrics():
    result = get_metrics()
    return jsonify(result)


# ===============================
# Document Detail Endpoint
# ===============================
@app.get("/document/<int:doc_id>")
def document_detail(doc_id):
    doc = get_document(doc_id)
    if not doc:
        return jsonify({"error": "Document not found"}), 404
    return jsonify(doc)


# ===============================
# Evaluation Endpoint
# ===============================
@app.get("/evaluate")
def evaluate():
    """
    Endpoint untuk evaluasi perbandingan TF-IDF vs BM25
    Params:
        - query: search query string
        - top_k: number of results (default 20)
    
    Returns:
        {
            "query": "...",
            "tfidf": {
                "runtime": ms,
                "precision": 0.0-1.0,
                "recall": 0.0-1.0,
                "f1": 0.0-1.0,
                "map": 0.0-1.0,
                ...
            },
            "bm25": {...}
        }
    """
    query = request.args.get("query", "").strip()
    top_k = int(request.args.get("top_k", 20))
    
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400
    
    # Import search engine module untuk evaluasi
    import search_engine as se
    
    # Buat object mock untuk evaluator
    class SearchEngineMock:
        def search(self, q, algo="tfidf", top_k=20):
            if algo == "bm25":
                return se.bm25_search(q, top_k=top_k)
            else:
                return se.tfidf_search(q, top_k=top_k)
    
    search_mock = SearchEngineMock()
    result = evaluate_query_both_algos(query, search_mock, top_k=top_k)
    
    return jsonify(result)


# ===============================
# Run Server
# ===============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
