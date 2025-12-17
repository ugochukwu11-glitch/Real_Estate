import pandas as pd
import re

# --- Load your data ---
df = pd.read_csv("dataset/combined_listings.csv")

print(f"Original shape: {df.shape}")

# --- Step 1: Normalize text ---
for col in ["title", "location", "property_type"]:
    df[col] = df[col].astype(str).str.lower().str.strip()

# --- Step 2: Remove duplicates ---
df_no_dup = df.drop_duplicates(subset=["title", "location", "property_type"], keep="first")
print(f"After removing duplicates: {df_no_dup.shape}")

# --- Step 3: Extract city from location ---
cities = [
    "lagos", "abuja", "port harcourt", "uyo", "enugu", "benin",
    "ilorin", "owerri", "calabar", "jos", "kaduna",
    "oyo", "delta", "ogun", "osun", "edo"
]

def extract_city(location):
    loc = str(location).lower()
    for city in cities:
        if re.search(rf"\b{city}\b", loc):
            return city.title()
    parts = re.split(r"[,\s]+", loc.strip())
    if parts:
        return parts[-1].title()
    return None

df_no_dup["city"] = df_no_dup["location"].apply(extract_city)

# --- Step 4: Clean city names ---
df_no_dup["city"] = (
    df_no_dup["city"]
    .astype(str)
    .str.replace(r"[^\w\s]", "", regex=True)
    .str.strip()
    .str.title()
)

# --- Step 5: Remove rentals / shortlets ---
exclude_keywords = ["for rent", "shortlet", "lease"]
pattern = "|".join(exclude_keywords)

df_no_dup = df_no_dup[~df_no_dup["property_type"].str.contains(pattern)]
df_no_dup = df_no_dup[~df_no_dup["title"].str.contains(pattern)]
df_no_dup = df_no_dup[~df_no_dup["price"].astype(str).str.contains("/day|/year", regex=True)]

# --- Step 6: Clean price column ---
EXCHANGE_RATE_USD_NGN = 1438

def clean_price(price):
    if pd.isna(price):
        return None

    price_str = str(price).lower().replace(",", "").strip()

    if "/sqm" in price_str:
        num = re.search(r"[\d\.]+", price_str)
        return float(num.group()) if num else None

    if price_str.startswith("$"):
        num = re.search(r"[\d\.]+", price_str)
        return float(num.group()) * EXCHANGE_RATE_USD_NGN if num else None

    price_str = re.sub(r"[^\d\.]", "", price_str)

    try:
        return float(price_str) if price_str else None
    except:
        return None

df_no_dup["price"] = df_no_dup["price"].apply(clean_price)

# --- Step 7: Derived columns for analytics ---

df_no_dup["price_per_bedroom"] = df_no_dup.apply(
    lambda x: x["price"] / x["bedrooms"] if pd.notnull(x["bedrooms"]) and x["bedrooms"] > 0 else None,
    axis=1
)

def categorize_price(p):
    if pd.isna(p):
        return None
    if p < 10_000_000:
        return "Low"
    elif p < 50_000_000:
        return "Mid"
    else:
        return "High"

df_no_dup["price_category"] = df_no_dup["price"].apply(categorize_price)

df_no_dup["added_date"] = pd.to_datetime(df_no_dup["added_date"], errors="coerce")
df_no_dup["month_posted"] = df_no_dup["added_date"].dt.to_period("M").astype(str)

# --- Step 7A: Categorize Property Type (New Feature) ---

def categorize_property_type(text):
    t = str(text).lower()

    # Land
    if "mixed-use land" in t:
        return "mixed-use land"
    if "commercial land" in t:
        return "commercial land"
    if "land" in t:
        return "land"

    # Duplexes / Houses
    if "fully detached" in t:
        return "fully detached"
    if "semi detached" in t or "semi-detached" in t:
        return "semi detached duplex"
    if "terraced" in t and "duplex" in t:
        return "terraced duplex"
    if "detached" in t and "duplex" in t:
        return "detached duplex"
    if "duplex" in t:
        return "house"
    if "bungalow" in t:
        return "bungalow"
    if "storey" in t:
        return "house"

    # Apartments
    if "block of flats" in t:
        return "block of flats"
    if "mini flat" in t:
        return "mini flat"
    if "self contain" in t or "self-contained" in t:
        return "self contain"
    if "flat" in t or "apartment" in t:
        return "flat/apartment"

    # Commercial
    if "plaza" in t or "complex" in t or "mall" in t:
        return "plaza / complex / mall"
    if "hotel" in t:
        return "hotel / guest house"
    if "office" in t:
        return "office space"
    if "shop" in t:
        return "shop"
    if "warehouse" in t:
        return "warehouse"
    if "factory" in t:
        return "factory"
    if "tank farm" in t:
        return "tank farm"
    if "commercial" in t:
        return "commercial property"

    # Mixed-use building
    if "mixed-use" in t:
        return "mixed-use building"

    return "house"

df_no_dup["property_category"] = df_no_dup["property_type"].apply(categorize_property_type)

# --- Step 8: Save cleaned CSV ---
df_no_dup.to_csv("dataset/new_cleaned_properties.csv", index=False)

print("\n✅ Done!")
print(f"Rows after cleaning: {df_no_dup.shape[0]}")
print("Unique property categories:")
print(df_no_dup['property_category'].value_counts().head(20))
print("Unique cities found:")
print(df_no_dup['city'].value_counts().head(20))
