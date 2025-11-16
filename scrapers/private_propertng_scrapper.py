import requests
from bs4 import BeautifulSoup
import random
import time
import csv

BASE_URL = "https://privateproperty.ng"
LISTING_URL = f"{BASE_URL}/property-for-sale"

HEADERS_POOL = [
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    },
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 "
                      "(KHTML, like Gecko) Version/17.6 Safari/605.1.15",
        "Accept-Language": "en-US,en;q=0.8",
    },
    {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.7",
    },
]

def get_page(url):
    for _ in range(5):
        try:
            headers = random.choice(HEADERS_POOL)
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                return r.text
            else:
                time.sleep(random.uniform(2, 5))
        except requests.RequestException:
            time.sleep(random.uniform(2, 5))
    return None

def parse_listing_page(url):
    html = get_page(url)
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    listings = soup.find_all("div", class_="similar-listings-item")
    urls = []
    for listing in listings:
        a_tag = listing.find("a", href=True)
        if a_tag:
            urls.append(a_tag["href"])
    return urls

def parse_details_page(url):
    html = get_page(BASE_URL + url)
    if not html:
        return None
    soup = BeautifulSoup(html, "html.parser")

    # Title
    title_tag = soup.select_one(".property-info h1")
    title = title_tag.get_text(strip=True) if title_tag else None

    # Location
    location_tag = soup.select_one(".property-info p")
    location = location_tag.get_text(strip=True) if location_tag else None

    # Price
    price_tag = soup.select_one(".property-info p.price")
    price = price_tag.get_text(strip=True) if price_tag else None

    # Proper Type
    proper_type_tag = soup.select_one(".property-details ul li span:contains('Property Type')")  # fallback
    if not proper_type_tag:
        # Using parent ul li a text
        proper_type_li = soup.select_one(".property-details ul li")
        proper_type = proper_type_li.find("a").get_text(strip=True) if proper_type_li else None
    else:
        proper_type = proper_type_tag.find_next_sibling("a").get_text(strip=True)

    # Bedrooms, Bathrooms, Toilets
    benefit_tags = soup.select(".property-benefit li")
    bedrooms = benefit_tags[0].get_text(strip=True) if len(benefit_tags) > 0 else None
    bathrooms = benefit_tags[1].get_text(strip=True) if len(benefit_tags) > 1 else None
    toilets = benefit_tags[2].get_text(strip=True) if len(benefit_tags) > 2 else None

    # Added and Updated Dates
    added_date_tag = soup.select_one(".property-details li span:contains('Added')")
    added_date = added_date_tag.next_sibling.strip() if added_date_tag else None
    updated_date_tag = soup.select_one(".property-details li span:contains('Updated')")
    updated_date = updated_date_tag.next_sibling.strip() if updated_date_tag else None

    return {
        "title": title,
        "proper_type": proper_type,
        "location": location,
        "price": price,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "toilets": toilets,
        "added_date": added_date,
        "updated_dates": updated_date
    }

def scrape_all(max_pages=3):
    all_properties = []
    for page in range(1, max_pages + 1):
        print(f"Scraping listing page {page}...")
        page_url = f"{LISTING_URL}?page={page}"
        property_urls = parse_listing_page(page_url)
        if not property_urls:
            print("No more properties found, stopping.")
            break
        for url in property_urls:
            print(f"Scraping property {url}")
            details = parse_details_page(url)
            if details:
                all_properties.append(details)
            time.sleep(random.uniform(1, 3))
        time.sleep(random.uniform(2, 5))
    return all_properties

"""if __name__ == "__main__":
    properties = scrape_all(max_pages=3)
    keys = ["title", "proper_type", "location", "price", "bedrooms", "bathrooms", "toilets", "added_date", "updated_dates"]

    with open("../dataset/privateproperty_listings.csv", "w", newline="", encoding="utf-8") as f:
        dict_writer = csv.DictWriter(f, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(properties)

    print(f"Scraped {len(properties)} properties successfully!")"""
