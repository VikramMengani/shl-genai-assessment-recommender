import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def setup_driver():
    options = Options()
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    return driver


def extract_details(driver, url):
    driver.get(url)
    time.sleep(3)

    try:
        name = driver.find_element(By.TAG_NAME, "h1").text
    except:
        name = "N/A"

    try:
        description = driver.find_element(By.TAG_NAME, "p").text
    except:
        description = ""

    return {
        "name": name,
        "url": url,
        "description": description
    }


def crawl():
    with open("data/raw_catalog_links.json", "r", encoding="utf-8") as f:
        links = json.load(f)

    driver = setup_driver()

    all_data = []

    for i, link in enumerate(links):
        print(f"Processing {i+1}/{len(links)}")
        details = extract_details(driver, link)
        all_data.append(details)
        time.sleep(2)

    driver.quit()

    with open("data/final_catalog.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2)

    print("Saved to data/final_catalog.json")


if __name__ == "__main__":
    crawl()