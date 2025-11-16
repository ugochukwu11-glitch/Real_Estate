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

# --- Step 5: Remove rentals / shortlets (check property_type + title + price) ---
exclude_keywords = ["for rent", "shortlet", "lease"]
pattern = "|".join(exclude_keywords)

# Drop if any keyword appears in property_type or title
df_no_dup = df_no_dup[~df_no_dup["property_type"].str.contains(pattern)]
df_no_dup = df_no_dup[~df_no_dup["title"].str.contains(pattern)]

# Drop listings that have /day or /year in price (likely rentals)
df_no_dup = df_no_dup[~df_no_dup["price"].astype(str).str.contains("/day|/year", regex=True)]

# --- Step 6: Clean price column ---
EXCHANGE_RATE_USD_NGN = 1438  # adjust to current rate


def clean_price(price):
    if pd.isna(price):
        return None

    price_str = str(price).lower().replace(",", "").strip()

    # /sqm case (lands)
    if "/sqm" in price_str:
        num_match = re.search(r"[\d\.]+", price_str)
        return float(num_match.group()) if num_match else None

    # Convert $ to NGN
    if price_str.startswith("$"):
        num_match = re.search(r"[\d\.]+", price_str)
        if num_match:
            return float(num_match.group()) * EXCHANGE_RATE_USD_NGN

    # Remove ₦ or other symbols
    price_str = re.sub(r"[^\d\.]", "", price_str)

    try:
        return float(price_str) if price_str else None
    except:
        return None


df_no_dup["price"] = df_no_dup["price"].apply(clean_price)

# --- Step 7: Derived columns for analytics ---

# Price per bedroom (avoid divide-by-zero)
df_no_dup["price_per_bedroom"] = df_no_dup.apply(
    lambda x: x["price"] / x["bedrooms"] if pd.notnull(x["bedrooms"]) and x["bedrooms"] > 0 else None,
    axis=1
)

# Price category
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

# Month posted
df_no_dup["added_date"] = pd.to_datetime(df_no_dup["added_date"], errors="coerce")
df_no_dup["month_posted"] = df_no_dup["added_date"].dt.to_period("M").astype(str)

# --- Step 8: Save cleaned CSV ---
df_no_dup.to_csv("dataset/cleaned_properties.csv", index=False)

print("\n✅ Done!")
print(f"Rows after cleaning: {df_no_dup.shape[0]}")
print("Unique cities found:")
print(df_no_dup['city'].value_counts().head(20))
