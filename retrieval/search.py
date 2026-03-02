import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer


# Load model
model = SentenceTransformer("all-mpnet-base-v2")

# Load index
index = faiss.read_index("data/faiss_index.bin")

# Load documents
with open("data/documents.json", "r", encoding="utf-8") as f:
    documents = json.load(f)


def search(query, top_k=10):
    print(f"\nSearching for: {query}")

    query_embedding = model.encode([query]).astype("float32")
    faiss.normalize_L2(query_embedding)

    scores, indices = index.search(query_embedding, top_k)

    results = []

    for idx in indices[0]:
        results.append({
            "name": documents[idx]["name"],
            "url": documents[idx]["url"]
        })

    return results


if __name__ == "__main__":
    query = input("Enter query: ")
    results = search(query)

    print("\nTop Recommendations:\n")
    for r in results:
        print(r["name"])
        print(r["url"])
        print("-" * 50)