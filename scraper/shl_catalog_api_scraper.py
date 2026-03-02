import requests
import json
import time

BASE_URL = "https://www.shl.com"

SEARCH_API = "https://www.shl.com/api/productcatalog/search"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/json",
    "Accept": "application/json"
}


def fetch_products(page):
    payload = {
        "page": page,
        "pageSize": 50,
        "filters": {
            "solutionType": "individual"
        }
    }

    response = requests.post(SEARCH_API, headers=HEADERS, json=payload)

    if response.status_code != 200:
        print("Error:", response.status_code)
        return None

    return response.json()


def crawl():
    all_products = []
    page = 1

    while True:
        print(f"Fetching page {page}")
        data = fetch_products(page)

        if not data or "results" not in data:
            break

        results = data["results"]

        if not results:
            break

        for item in results:
            all_products.append({
                "name": item.get("title"),
                "url": BASE_URL + item.get("url", ""),
                "description": item.get("description")
            })

        page += 1
        time.sleep(1)

    print("Total products:", len(all_products))

    with open("data/raw_catalog.json", "w", encoding="utf-8") as f:
        json.dump(all_products, f, indent=2)

    print("Saved to data/raw_catalog.json")


if __name__ == "__main__":
    crawl()