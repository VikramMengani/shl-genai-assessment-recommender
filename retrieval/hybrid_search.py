import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi


def clean_query(query):
    lines = query.split("\n")
    cleaned_lines = []

    for line in lines:
        line = line.strip()

        if "about us" in line.lower():
            continue
        if "equal opportunity employer" in line.lower():
            continue
        if len(line) < 5:
            continue

        cleaned_lines.append(line)

    return " ".join(cleaned_lines)


model = SentenceTransformer("all-mpnet-base-v2")
index = faiss.read_index("data/faiss_index.bin")

with open("data/documents.json", "r", encoding="utf-8") as f:
    documents = json.load(f)

corpus = [
    (doc["name"] + " " + doc["description"]).lower().split()
    for doc in documents
]

bm25 = BM25Okapi(corpus)


def prefilter_documents(query):
    q = query.lower()
    filtered = []

    for i, doc in enumerate(documents):
        text = (doc["name"] + " " + doc["description"]).lower()

        if any(w in q for w in ["java", "python", "sql"]):
            if any(w in text for w in ["java", "python", "sql"]):
                filtered.append(i)

        elif any(w in q for w in ["personality", "leadership", "opq"]):
            if any(w in text for w in ["personality", "leadership", "opq"]):
                filtered.append(i)

        else:
            filtered.append(i)

    return filtered if filtered else list(range(len(documents)))


def hybrid_search(query, top_k=10):

    query = clean_query(query)

    query_embedding = model.encode([query]).astype("float32")
    faiss.normalize_L2(query_embedding)

    faiss_scores, faiss_indices = index.search(query_embedding, 200)

    tokenized_query = query.lower().split()
    bm25_scores = bm25.get_scores(tokenized_query)

    combined_scores = []
    faiss_index_list = list(faiss_indices[0])

    candidate_indices = prefilter_documents(query)

    for i in candidate_indices:

        semantic_score = 0
        keyword_score = bm25_scores[i]

        if i in faiss_index_list:
            idx_position = faiss_index_list.index(i)
            semantic_score = faiss_scores[0][idx_position]

        final_score = (0.85 * semantic_score) + (0.15 * keyword_score)
        combined_scores.append((i, final_score))

    combined_scores.sort(key=lambda x: x[1], reverse=True)

    results = []
    for idx, score in combined_scores[:top_k]:
        results.append({
            "name": documents[idx]["name"],
            "url": documents[idx]["url"],
            "description": documents[idx]["description"]
        })

    return results