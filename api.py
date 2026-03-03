from fastapi import FastAPI
from pydantic import BaseModel
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

app = FastAPI(title="SHL Assessment Recommendation API")

# -------------------------
# Load resources safely
# -------------------------

try:
    model = SentenceTransformer("all-mpnet-base-v2")
    index = faiss.read_index("data/faiss_index.bin")

    with open("data/documents.json", "r", encoding="utf-8") as f:
        documents = json.load(f)

    corpus = [
        (doc["name"] + " " + doc["description"]).lower().split()
        for doc in documents
    ]
    bm25 = BM25Okapi(corpus)

    print("✅ Model and index loaded successfully.")

except Exception as e:
    print("❌ Startup error:", e)
    raise e


class QueryRequest(BaseModel):
    query: str
    top_k: int = 10


@app.get("/")
def home():
    return {"message": "SHL Assessment Recommendation API Running"}


@app.post("/recommend")
def recommend(request: QueryRequest):
    query_embedding = model.encode([request.query]).astype("float32")
    faiss.normalize_L2(query_embedding)

    scores, indices = index.search(query_embedding, 50)

    results = []

    for idx in indices[0][:request.top_k]:
        results.append({
            "name": documents[idx]["name"],
            "url": documents[idx]["url"]
        })

    return {"recommendations": results}