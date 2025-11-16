import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

BASE_URL = "https://nigeriapropertycentre.com"
LISTING_URL = f"{BASE_URL}/for-sale"

HEADERS_POOL = [
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0 Safari/537.36"},
    {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/17.3 Safari/605.1.15"},
    {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0"},
]

def get_soup(url):
    """Fetch and parse HTML with rotating headers."""
    headers = random.choice(HEADERS_POOL)
    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")

def get_property_links(page_number):
    """Extract property detail links from one listing page."""
    url = f"{LISTING_URL}?page={page_number}"
    print(f"📄 Scraping listings page {page_number} ...")

    soup = get_soup(url)
    cards = soup.select("div.wp-block.property.list div.wp-block-title a[itemprop='url']")
    links = [BASE_URL + card["href"].strip() for card in cards if card.has_attr("href")]
    print(f"→ Found {len(links)} property links on page {page_number}")
    return links

def parse_details_page(url):
    """Extract all required data from the property details page."""
    try:
        soup = get_soup(url)
        # Title
        title = soup.select_one("h4.content-title")
        title = title.get_text(strip=True) if title else None

        # Location
        location = soup.select_one("address")
        location = location.get_text(strip=True) if location else None

        # Price
        price = soup.select_one("span[itemprop='price']")
        price = price.get_text(strip=True) if price else None

        # Bedrooms, Bathrooms, Toilets (from Property Details table)
        table = soup.select_one("table.table-bordered")
        rows = table.select("tr td") if table else []
        details_map = {}
        for cell in rows:
            text = cell.get_text(strip=True)
            if ":" in text:
                key, val = text.split(":", 1)
                details_map[key.strip()] = val.strip()

        bedrooms = details_map.get("Bedrooms")
        bathrooms = details_map.get("Bathrooms")
        toilets = details_map.get("Toilets")
        property_type = details_map.get("Type")
        market_status = details_map.get("Market Status")
        added_date = details_map.get("Added On")
        updated_date = details_map.get("Last Updated")

        data = {
            "title": title,
            "location": location,
            "price": price,
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "toilets": toilets,
            "property_type": property_type,
            "market_status": market_status,
            "date_added": added_date,
            "date_updated": updated_date

        }

        print(f"✅ Scraped: {title}")
        return data

    except Exception as e:
        print(f"⚠️ Error on {url}: {e}")
        return {"url": url, "error": str(e)}

def scrape_all(max_pages=1):
    """Main controller for scraping multiple pages."""
    all_properties = []
    for page in range(1, max_pages + 1):
        links = get_property_links(page)
        for link in links:
            time.sleep(random.uniform(2, 5))  # polite delay
            property_data = parse_details_page(link)
            all_properties.append(property_data)
        time.sleep(random.uniform(4, 8))
    return all_properties

"""if __name__ == "__main__":
    properties = scrape_all(max_pages=1)
    df = pd.DataFrame(properties)
    #df.to_csv("nigeriapropertycentre_listings.csv", index=False)
    #print(f"\n✅ Done! Saved {len(df)} listings to CSV.")
"""