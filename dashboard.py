import pandas as pd
import streamlit as st

# helper functions
def calculate_growth(df):
    df = df.sort_values("month_posted")
    df["MoM_growth_%"] = df["price"].pct_change() * 100
    df["YoY_growth_%"] = df["price"].pct_change(12) * 100
    return df




def to_csv(df):
    return df.to_csv(index=False).encode("utf-8")

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="Nigeria Real Estate Intelligence",
    layout="wide"
)

st.title("🏡 Nigeria Real Estate Intelligence Dashboard")
st.caption(
    "Market-level insights derived from cleaned property listings. "
    "Prices shown use median values to reduce distortion from extreme listings."
)

# ======================================================
# LOAD DATA
# ======================================================
@st.cache_data
def load_data():
    df = pd.read_csv("dataset/new_cleaned_properties.csv")
    return df

df = load_data()

# ======================================================
# ENFORCE ANALYTICAL RULES
# ======================================================

# ---- Buildings only (exclude land for building analytics)
buildings_df = df[df["property_category"] != "land"].copy()

# ---- Remove extreme outliers (top 1%)
upper_cap = buildings_df["price"].quantile(0.99)
buildings_df = buildings_df[buildings_df["price"] <= upper_cap]

# ---- Date handling
buildings_df["added_date"] = pd.to_datetime(
    buildings_df["added_date"],
    errors="coerce",
    dayfirst=True
)
buildings_df = buildings_df.dropna(subset=["added_date"])
buildings_df["month_posted"] = buildings_df["added_date"].dt.to_period("M").astype(str)

# ---- Price per bedroom (for value analysis)
buildings_df = buildings_df[
    (buildings_df["bedrooms"].notna()) & (buildings_df["bedrooms"] > 0)
]
buildings_df["price_per_bedroom"] = buildings_df["price"] / buildings_df["bedrooms"]

# Remove extreme outliers for price per bedroom
ppb_cap = buildings_df["price_per_bedroom"].quantile(0.99)
buildings_df = buildings_df[buildings_df["price_per_bedroom"] <= ppb_cap]

# ======================================================
# SIDEBAR — GLOBAL FILTERS
# ======================================================
st.sidebar.markdown("### 🌍 Global Filters")
st.sidebar.caption("These filters apply to all tabs below.")

cities = sorted(buildings_df["city"].dropna().unique())
selected_city = st.sidebar.selectbox("City", ["All"] + cities)

property_categories = sorted(buildings_df["property_category"].dropna().unique())
selected_category = st.sidebar.selectbox(
    "Property Category",
    ["All"] + property_categories
)

min_price = int(buildings_df["price"].min())
max_price = int(buildings_df["price"].max())

price_range = st.sidebar.slider(
    "Price Range (₦)",
    min_price,
    max_price,
    (min_price, max_price)
)

# ======================================================
# APPLY FILTERS
# ======================================================
filtered_df = buildings_df.copy()

growth_df = (
    filtered_df
    .groupby(["city", "month_posted"])["price"]
    .median()
    .reset_index()
)


if selected_city != "All":
    filtered_df = filtered_df[filtered_df["city"] == selected_city]

if selected_category != "All":
    filtered_df = filtered_df[filtered_df["property_category"] == selected_category]

filtered_df = filtered_df[
    (filtered_df["price"] >= price_range[0]) &
    (filtered_df["price"] <= price_range[1])
]

# ======================================================
# TABS (UX STRUCTURE)
# ======================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Market Overview",
    "📈 Trends",
    "🌍 Land Intelligence",
    "🛏️ Value Analysis",
    "🏙️ City Comparison"
])

# ======================================================
# TAB 1 — MARKET OVERVIEW
# ======================================================
with tab1:
    st.subheader("Median Property Prices by City")
    st.caption("Buildings only. Median reduces distortion from luxury outliers.")

    city_price = (
        filtered_df
        .groupby("city")["price"]
        .median()
        .sort_values(ascending=False)
        .reset_index()
    )

    st.bar_chart(city_price.set_index("city")["price"])

    st.subheader("Top 10 Most Expensive Areas")
    st.caption("Ranked by median listing price.")

    top_areas = (
        filtered_df
        .groupby("location")["price"]
        .median()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    st.dataframe(top_areas, use_container_width=True)

    st.download_button(
        label="⬇️ Download Top Areas (CSV)",
        data=to_csv(top_areas),
        file_name="top_expensive_areas.csv",
        mime="text/csv"
    )

# ======================================================
# TAB 2 — MONTHLY TRENDS
# ======================================================
with tab2:
    st.subheader("Market Growth Trends")
    st.caption(
        "Median prices with Month-over-Month (MoM) and Year-over-Year (YoY) growth. "
        "Growth metrics are only meaningful where sufficient history exists."
    )

    city_for_growth = st.selectbox(
        "Select city for growth analysis",
        sorted(growth_df["city"].unique())
    )

    city_growth = growth_df[growth_df["city"] == city_for_growth].copy()
    city_growth = calculate_growth(city_growth)

    # Display growth table
    st.dataframe(
        city_growth.tail(15),
        use_container_width=True
    )

    # Plot median price trend
    st.line_chart(
        city_growth.set_index("month_posted")["price"]
    )

    # Show latest growth numbers
    latest = city_growth.dropna().iloc[-1:] if not city_growth.dropna().empty else None

    if latest is not None:
        col1, col2 = st.columns(2)
        col1.metric(
            "Latest MoM Growth",
            f"{latest['MoM_growth_%'].values[0]:.2f} %"
        )
        col2.metric(
            "Latest YoY Growth",
            f"{latest['YoY_growth_%'].values[0]:.2f} %"
        )


# ======================================================
# TAB 3 — LAND INTELLIGENCE
# ======================================================
with tab3:
    st.subheader("Land Price Intelligence (₦ per sqm)")
    st.caption("Land is analyzed separately using price per square meter.")

    land_df = df[df["property_category"] == "land"].copy()

    if land_df.empty:
        st.warning("No land data available.")
    else:
        land_cap = land_df["price"].quantile(0.99)
        land_df = land_df[land_df["price"] <= land_cap]

        land_city = (
            land_df
            .groupby("city")["price"]
            .median()
            .sort_values(ascending=False)
            .reset_index()
        )

        st.bar_chart(land_city.set_index("city")["price"])

        st.subheader("Top 10 Most Expensive Land Locations (₦/sqm)")
        top_land = (
            land_df
            .groupby("location")["price"]
            .median()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )

        st.dataframe(top_land, use_container_width=True)

        st.download_button(
            label="⬇️ Download Land Prices (CSV)",
            data=to_csv(top_land),
            file_name="land_price_intelligence.csv",
            mime="text/csv"
        )

# ======================================================
# TAB 4 — VALUE ANALYSIS
# ======================================================
with tab4:
    st.subheader("Price per Bedroom Analysis")
    st.caption("Normalizes prices to compare value across property sizes.")

    ppb_city = (
        filtered_df
        .groupby("city")["price_per_bedroom"]
        .median()
        .sort_values(ascending=False)
        .reset_index()
    )

    st.bar_chart(ppb_city.set_index("city")["price_per_bedroom"])

    st.subheader("Top 10 Locations by Price per Bedroom")

    top_ppb = (
        filtered_df
        .groupby("location")["price_per_bedroom"]
        .median()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    st.dataframe(top_ppb, use_container_width=True)

# ======================================================
# TAB 5 — CITY COMPARISON
# ======================================================
with tab5:
    st.subheader("City Comparison Summary")
    st.caption("Side-by-side metrics for investment decisions.")

    comparison_table = (
        filtered_df
        .groupby("city")
        .agg(
            median_price=("price", "median"),
            median_price_per_bedroom=("price_per_bedroom", "median"),
            listings=("price", "count")
        )
        .sort_values(by="median_price", ascending=False)
        .reset_index()
    )

    st.dataframe(comparison_table, use_container_width=True)
    st.download_button(
        label="⬇️ Download City Comparison (CSV)",
        data=to_csv(comparison_table),
        file_name="city_comparison.csv",
        mime="text/csv"
    )

# ======================================================
# FOOTER
# ======================================================
st.caption(f"Total listings after filtering: {filtered_df.shape[0]:,}")
