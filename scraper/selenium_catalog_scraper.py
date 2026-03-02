import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup


BASE_URL = "https://www.shl.com/products/product-catalog/?start={}&type=1"


def setup_driver():
    options = Options()
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    return driver


def extract_links_from_page(driver):
    links = []
    elements = driver.find_elements(By.TAG_NAME, "a")

    for el in elements:
        href = el.get_attribute("href")
        if href and "/products/product-catalog/view/" in href:
            links.append(href)

    return list(set(links))


def scrape_product(driver, url):
    try:
        driver.get(url)
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        name_tag = soup.find("h1")
        name = name_tag.get_text(strip=True) if name_tag else ""

        meta_desc = soup.find("meta", attrs={"name": "description"})
        description = meta_desc["content"].strip() if meta_desc else ""

        return {
            "name": name,
            "url": url,
            "description": description
        }

    except Exception as e:
        print("Error scraping:", url)
        return None


def crawl():
    driver = setup_driver()
    all_links = []
    start = 0

    try:
        while True:
            url = BASE_URL.format(start)
            print(f"Opening page with start={start}")
            driver.get(url)
            time.sleep(4)

            page_links = extract_links_from_page(driver)

            if not page_links:
                break

            new_links = [l for l in page_links if l not in all_links]
            if not new_links:
                break

            all_links.extend(new_links)
            start += 12

        print("Total links:", len(all_links))

        data = []
        for i, link in enumerate(all_links):
            print(f"Scraping {i+1}/{len(all_links)}")
            result = scrape_product(driver, link)
            if result:
                data.append(result)

        with open("data/final_catalog.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print("Saved to data/final_catalog.json")

    finally:
        driver.quit()


if __name__ == "__main__":
    crawl()