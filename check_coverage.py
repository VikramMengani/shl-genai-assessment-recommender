import json
import pandas as pd

# Load scraped catalog
with open("data/final_catalog.json", "r", encoding="utf-8") as f:
    catalog = json.load(f)

catalog_urls = set(item["url"].lower().strip().rstrip("/") for item in catalog)

# Load labeled data
df = pd.read_excel("Gen_AI Dataset.xlsx")
df = df[["Query", "Assessment_url"]]

missing = 0
total = len(df)

for url in df["Assessment_url"]:
    normalized = url.lower().strip().rstrip("/")
    normalized = normalized.replace("/solutions", "")

    if normalized not in catalog_urls:
        missing += 1

print("Total labeled URLs:", total)
print("Missing from catalog:", missing)
print("Coverage %:", round((total - missing) / total * 100, 2))