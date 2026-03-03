import pandas as pd
from retrieval.hybrid_search import hybrid_search

# Load ONLY Test-Set sheet
test_df = pd.read_excel("Gen_AI Dataset.xlsx", sheet_name="Test-Set")

rows = []

for query in test_df["Query"]:
    print("Processing:", query[:60])

    results = hybrid_search(query, top_k=10)

    for r in results:
        rows.append({
            "Query": query,
            "Assessment_url": r["url"]
        })

submission_df = pd.DataFrame(rows)

submission_df.to_csv("submission.csv", index=False)

print("\nsubmission.csv generated successfully!")