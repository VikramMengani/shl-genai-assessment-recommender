import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer


with open("data/final_catalog.json", "r", encoding="utf-8") as f:
    catalog = json.load(f)

documents = []
texts = []

for doc in catalog:
    documents.append(doc)
    text = doc.get("name", "") + " " + doc.get("description", "")
    texts.append(text.strip())

model = SentenceTransformer("all-mpnet-base-v2")

print("Generating embeddings...")
embeddings = model.encode(texts, convert_to_numpy=True)
embeddings = embeddings.astype("float32")
faiss.normalize_L2(embeddings)

dimension = embeddings.shape[1]
index = faiss.IndexFlatIP(dimension)
index.add(embeddings)

faiss.write_index(index, "data/faiss_index.bin")

with open("data/documents.json", "w", encoding="utf-8") as f:
    json.dump(documents, f, indent=2, ensure_ascii=False)

print("Index built and saved.")