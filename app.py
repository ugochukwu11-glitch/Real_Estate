from fastapi import FastAPI, Query
import pandas as pd

# --- Load cleaned dataset ---
df = pd.read_csv("dataset/new_cleaned_properties.csv")

# Ensure date columns are datetime
df['added_date'] = pd.to_datetime(df['added_date'], errors='coerce')
df['updated_date'] = pd.to_datetime(df['updated_date'], errors='coerce')

app = FastAPI(title="Nigeria Real Estate API", version="1.0")


# -----------------------
# Endpoint: Average Price
# -----------------------
@app.get("/api/average_price")
def average_price(
        city: str = Query(..., description="City name"),
        property_type: str = Query(None, description="Optional property type filter")
):
    df_city = df[df['city'].str.lower() == city.lower()]

    if property_type:
        df_city = df_city[df_city['property_type'].str.lower() == property_type.lower()]

    avg_price = df_city['price'].mean()
    count = len(df_city)

    return {
        "city": city.title(),
        "property_type": property_type.title() if property_type else "All",
        "average_price": round(avg_price, 2) if not pd.isna(avg_price) else None,
        "count": count
    }


# -----------------------
# Endpoint: Monthly Trends
# -----------------------
@app.get("/api/trends")
def monthly_trends(
        city: str = Query(..., description="City name"),
        property_type: str = Query(None, description="Optional property type filter")
):
    df_city = df[df['city'].str.lower() == city.lower()]

    if property_type:
        df_city = df_city[df_city['property_type'].str.lower() == property_type.lower()]

    # Extract month-year from added_date
    df_city['month_posted'] = df_city['added_date'].dt.to_period('M')

    trends = df_city.groupby('month_posted')['price'].mean().reset_index()

    # Convert to dict for API response
    trend_list = [{"month": str(row['month_posted']), "average_price": round(row['price'], 2)} for _, row in
                  trends.iterrows()]

    return {
        "city": city.title(),
        "property_type": property_type.title() if property_type else "All",
        "trends": trend_list
    }


# -----------------------
# Root endpoint
# -----------------------
@app.get("/")
def root():
    return {"message": "Welcome to the Nigeria Real Estate API. Use /docs for interactive API documentation."}

# run app --- uvicorn app:app --reload