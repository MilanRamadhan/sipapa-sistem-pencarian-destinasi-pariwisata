import requests
import json

query = "jakarta"
top_k = 10

# Get TF-IDF results
tfidf_results = requests.get(f"http://localhost:5000/search?query={query}&algo=tfidf&top_k={top_k}").json()
print(f"TF-IDF doc_ids: {[r['doc_id'] for r in tfidf_results]}")

# Get BM25 results
bm25_results = requests.get(f"http://localhost:5000/search?query={query}&algo=bm25&top_k={top_k}").json()
print(f"BM25 doc_ids: {[r['doc_id'] for r in bm25_results]}")

# Check if they're different
tfidf_ids = set(r['doc_id'] for r in tfidf_results)
bm25_ids = set(r['doc_id'] for r in bm25_results)

print(f"\nSame docs: {len(tfidf_ids & bm25_ids)}/{top_k}")
print(f"Different docs: {len(tfidf_ids ^ bm25_ids)}/{top_k}")

# Get evaluation
eval_results = requests.get(f"http://localhost:5000/evaluate?query={query}&top_k={top_k}").json()
print(f"\n{json.dumps(eval_results, indent=2)}")
