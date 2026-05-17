import requests
from bs4 import BeautifulSoup
import json
import time

BASE_URL = "https://www.shl.com"
CATALOG_URL = f"{BASE_URL}/solutions/products/product-catalog/"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def get_catalog_links():
    response = requests.get(CATALOG_URL, headers=headers)

    soup = BeautifulSoup(response.text, "html.parser")

    assessments = []

    links = soup.find_all("a")

    for link in links:
        text = link.get_text(strip=True)
        href = link.get("href")

        if (
            text
            and href
            and "/products/" in href
            and len(text) > 5
            and not text.isdigit()
        ):

            full_url = (
                href if href.startswith("http")
                else BASE_URL + href
            )

            assessments.append({
                "name": text,
                "url": full_url
            })

    unique = []
    seen = set()

    for item in assessments:
        if item["url"] not in seen:
            seen.add(item["url"])
            unique.append(item)

    return unique


def scrape_assessment_details(assessment):

    try:
        response = requests.get(
            assessment["url"],
            headers=headers,
            timeout=10
        )

        soup = BeautifulSoup(response.text, "html.parser")

        paragraphs = soup.find_all("p")

        description = " ".join(
            p.get_text(" ", strip=True)
            for p in paragraphs[:5]
        )

        assessment["description"] = description

        return assessment

    except Exception as e:
        print("Error:", assessment["url"])
        print(e)

        return assessment


def main():

    catalog = get_catalog_links()

    detailed_data = []

    for item in catalog:

        print("Scraping:", item["name"])

        detailed_item = scrape_assessment_details(item)

        detailed_data.append(detailed_item)

        time.sleep(1)

    with open(
        "../data/shl_catalog.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(detailed_data, f, indent=4)

    print(f"\nSaved {len(detailed_data)} assessments")


if __name__ == "__main__":
    main()