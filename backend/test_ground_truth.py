import pandas as pd
import re

corpus = pd.read_csv("data/corpus_clean.csv")
query = "jakarta"

# Tokenize query
query_lower = query.lower()
keywords = re.findall(r'\w+', query_lower)
keywords = [k for k in keywords if len(k) > 2]

print(f"Query: {query}")
print(f"Keywords: {keywords}")

relevant_docs = []

for idx, row in corpus.iterrows():
    if idx > 20:  # Test first 20 docs only
        break
        
    content = str(row.get("content_clean", "")).lower()
    title = str(row.get("title", "")).lower()
    
    title_match = sum(1 for kw in keywords if kw in title)
    content_match = sum(1 for kw in keywords if kw in content)
    
    if title_match >= 1 or content_match >= 1:
        relevant_docs.append(idx)
        print(f"Doc {idx}: title_match={title_match}, content_match={content_match}")
        print(f"  Title: {title[:80]}")

print(f"\nTotal relevant in first 20: {len(relevant_docs)}")
