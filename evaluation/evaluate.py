import json
import pandas as pd
from urllib.parse import urlparse
from retrieval.hybrid_search import hybrid_search


def extract_slug(url):
    """
    Extract last part of URL (assessment slug).
    """
    if not isinstance(url, str):
        return ""

    url = url.strip().lower()

    if url.endswith("/"):
        url = url[:-1]

    return url.split("/")[-1]


def recall_at_k(true_urls, predicted_urls, k=10):
    true_slugs = [extract_slug(u) for u in true_urls]
    predicted_slugs = [extract_slug(u) for u in predicted_urls]

    return len(set(true_slugs) & set(predicted_slugs[:k])) / len(true_slugs)


# Load dataset
df = pd.read_excel("Gen_AI Dataset.xlsx")
queries = df["Query"].unique()

# Load catalog
with open("data/documents.json", "r", encoding="utf-8") as f:
    documents = json.load(f)

catalog_slugs = set(extract_slug(d["url"]) for d in documents)

# Coverage check
missing = 0
for url in df["Assessment_url"]:
    if extract_slug(url) not in catalog_slugs:
        missing += 1

print("Total labeled URLs:", len(df))
print("Missing from catalog:", missing)
print("Coverage %:", round((1 - missing / len(df)) * 100, 2))
print("-" * 50)


# Evaluation
mean_recall = 0

for query in queries:

    true_urls = df[df["Query"] == query]["Assessment_url"].tolist()

    results = hybrid_search(query, top_k=10)
    predicted_urls = [r["url"] for r in results]

    score = recall_at_k(true_urls, predicted_urls, 10)

    print("Query:", query[:80], "...")
    print("Recall@10:", round(score, 3))
    print("-" * 60)

    mean_recall += score


mean_recall /= len(queries)

print("\n=====================================")
print("Mean Recall@10:", round(mean_recall, 4))
print("=====================================")