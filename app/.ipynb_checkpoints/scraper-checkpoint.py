import requests
from bs4 import BeautifulSoup
import json

URL = "https://www.shl.com/solutions/products/product-catalog/"


def scrape_shl_catalog():
    response = requests.get(URL)

    if response.status_code != 200:
        print("Failed to fetch page")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    assessments = []

    links = soup.find_all("a")

    for link in links:
        text = link.get_text(strip=True)
        href = link.get("href")

        if text and href:
            if "/products/" in href:
                assessments.append({
                    "name": text,
                    "url": href if href.startswith("http") else f"https://www.shl.com{href}"
                })

    unique_assessments = []
    seen = set()

    for item in assessments:
        if item["url"] not in seen:
            seen.add(item["url"])
            unique_assessments.append(item)

    with open("../data/shl_catalog.json", "w", encoding="utf-8") as f:
        json.dump(unique_assessments, f, indent=4)

    print(f"Saved {len(unique_assessments)} assessments")


if __name__ == "__main__":
    scrape_shl_catalog()