import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import random
import time

# --- Header Pool (Rotating User-Agents) ---
HEADERS_LIST = [
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"},
    {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15"},
    {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0"},
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Edge/126.0.2592.68"},
]

def get_soup(url, retries=3, backoff=5):
    """Fetch a page with retries and return a BeautifulSoup object."""
    for attempt in range(1, retries + 1):
        try:
            headers = random.choice(HEADERS_LIST)
            print(f"🌐 Fetching ({attempt}/{retries}): {url}")
            response = requests.get(url, headers=headers, timeout=35)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Attempt {attempt} failed: {e}")
            if attempt < retries:
                wait = backoff * attempt
                print(f"🔁 Retrying in {wait}s...")
                time.sleep(wait)
            else:
                print(f"❌ All {retries} attempts failed for {url}")
                return None


def extract_listing_data(listing):
    """Extract data from a single listing card."""
    title = listing.select_one(".pl-title h3 a")
    location = listing.select_one(".pl-title p")
    property_type = listing.select_one(".pl-title h6")
    price = listing.select_one(".pl-price h3")
    details = listing.select_one(".pl-price h6")
    date_info = listing.select_one(".date-added")

    # Clean text
    title = title.get_text(strip=True) if title else None
    location = location.get_text(strip=True) if location else None
    property_type = property_type.get_text(strip=True) if property_type else None
    price = price.get_text(strip=True).replace("₦", "").replace(",", "").strip() if price else None
    details_text = details.get_text(strip=True) if details else ""
    date_info = date_info.get_text(strip=True) if date_info else ""

    # Extract numeric features
    bedrooms = re.search(r"(\d+)\s*Bed", details_text)
    bathrooms = re.search(r"(\d+)\s*Bath", details_text)
    toilets = re.search(r"(\d+)\s*Toilet", details_text)
    parking = re.search(r"(\d+)\s*Parking", details_text)

    bedrooms = int(bedrooms.group(1)) if bedrooms else None
    bathrooms = int(bathrooms.group(1)) if bathrooms else None
    toilets = int(toilets.group(1)) if toilets else None
    parking = int(parking.group(1)) if parking else None

    # Extract updated and added dates
    updated_date, added_date = None, None
    if date_info:
        match = re.search(r"Updated\s+([\dA-Za-z ]+)", date_info)
        if match:
            updated_date = match.group(1).strip()
        match = re.search(r"Added\s+([\dA-Za-z ]+)", date_info)
        if match:
            added_date = match.group(1).strip()

    return {
        "title": title,
        "property_type": property_type,
        "location": location,
        "price": price,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "toilets": toilets,
        "parking_spaces": parking,
        "updated_date": updated_date,
        "added_date": added_date,
    }

def scrape_propertypro(max_pages=2):
    """Scrape multiple pages from PropertyPro."""
    base_url = "https://www.propertypro.ng/property-for-sale?page="
    all_data = []

    for page in range(1, max_pages + 1):
        url = f"{base_url}{page}"
        print(f"\n📄 Scraping page {page}...")
        soup = get_soup(url)
        if not soup:
            continue

        listings = soup.find_all("div", class_="property-listing")
        print(f"→ Found {len(listings)} listings")

        for listing in listings:
            data = extract_listing_data(listing)
            all_data.append(data)

        # Random delay (anti-block)
        delay = random.uniform(3, 6)
        print(f"⏳ Waiting {delay:.1f}s before next page...")
        time.sleep(delay)

    # Save results
    #df = pd.DataFrame(all_data)
    #df.to_csv("propertypro_listings.csv", index=False)
    #print("\n✅ Scraping complete. Data saved to 'propertypro_listings.csv'")
    return all_data

# --- Run Script ---
"""if __name__ == "__main__":
    df = scrape_propertypro(max_pages=1)  # change number of pages here
    print(df.head())
"""