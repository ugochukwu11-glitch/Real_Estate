import os
import pandas as pd
from scrapers.propertypro_scraper import scrape_propertypro
from scrapers.nigeria_property_center_scraper import scrape_all as scrape_npc
from scrapers.private_propertng_scrapper import scrape_all as scrape_private

# -----------------------------
# 1️⃣ Helper: Normalize columns
# -----------------------------
def normalize_columns(df):
    """Ensure all DataFrames share the same column structure and names."""
    column_map = {
        "proper_type": "property_type",
        "date_added": "added_date",
        "date_updated": "updated_date",
        "updated_dates": "updated_date",
    }

    # Rename columns if necessary
    df = df.rename(columns=column_map)

    # Ensure all required columns exist
    standard_columns = [
        "title",
        "property_type",
        "location",
        "price",
        "bedrooms",
        "bathrooms",
        "toilets",
        "added_date",
        "updated_date",
    ]

    for col in standard_columns:
        if col not in df.columns:
            df[col] = None

    # Keep only standard columns
    return df[standard_columns]

# -----------------------------
# 2️⃣ Main scraping controller
# -----------------------------
def run_all_scrapers(propertypro_pages=2, npc_pages=1, private_pages=2):
    """Run all three scrapers and combine their results into one CSV."""
    all_dfs = []

    print("\n🏠 Starting PropertyPro scraper...")
    try:
        propertypro_data = scrape_propertypro(max_pages=propertypro_pages)
        if not isinstance(propertypro_data, pd.DataFrame):
            propertypro_data = pd.DataFrame(propertypro_data)
        propertypro_data = normalize_columns(propertypro_data)
        all_dfs.append(propertypro_data)
    except Exception as e:
        print(f"⚠️ PropertyPro failed: {e}")

    print("\n🏠 Starting NigeriaPropertyCentre scraper...")
    try:
        npc_data = scrape_npc(max_pages=npc_pages)
        npc_df = pd.DataFrame(npc_data)
        npc_df = normalize_columns(npc_df)
        all_dfs.append(npc_df)
    except Exception as e:
        print(f"⚠️ NigeriaPropertyCentre failed: {e}")

    print("\n🏠 Starting PrivateProperty scraper...")
    try:
        private_data = scrape_private(max_pages=private_pages)
        private_df = pd.DataFrame(private_data)
        private_df = normalize_columns(private_df)
        all_dfs.append(private_df)
    except Exception as e:
        print(f"⚠️ PrivateProperty failed: {e}")

    # Concatenate all DataFrames
    if all_dfs:
        final_df = pd.concat(all_dfs, ignore_index=True)
    else:
        final_df = pd.DataFrame(columns=[
            "title", "property_type", "location", "price",
            "bedrooms", "bathrooms", "toilets", "added_date", "updated_date"
        ])

    # Create dataset folder if not exists
    os.makedirs("dataset", exist_ok=True)

    # Save unified CSV
    output_path = os.path.join("dataset", "combined_listings.csv")
    final_df.to_csv(output_path, index=False, encoding="utf-8")

    print(f"\n📦 Data saved to: {output_path}")
    print(final_df.head())
    print(f"✅ Total records: {len(final_df)}")

    return final_df

# -----------------------------
# 3️⃣ Run script directly
# -----------------------------
if __name__ == "__main__":
    run_all_scrapers(
        propertypro_pages=100,
        npc_pages=50,
        private_pages=50
    )
