import requests

queries = ["jakarta", "hotel", "pantai", "kuliner", "museum"]

for query in queries:
    eval_results = requests.get(f"http://localhost:5000/evaluate?query={query}&top_k=20").json()
    
    tfidf = eval_results['tfidf']
    bm25 = eval_results['bm25']
    
    print(f"\nQuery: '{query}'")
    print(f"  Ground Truth: {tfidf['relevant_count']} relevant docs")
    print(f"  TF-IDF:  Precision={tfidf['precision']:.3f}, Recall={tfidf['recall']:.3f}, F1={tfidf['f1']:.3f}")
    print(f"  BM25:    Precision={bm25['precision']:.3f}, Recall={bm25['recall']:.3f}, F1={bm25['f1']:.3f}")
    
    winner = "TF-IDF" if tfidf['f1'] > bm25['f1'] else "BM25" if bm25['f1'] > tfidf['f1'] else "TIE"
    print(f"  Winner: {winner}")
