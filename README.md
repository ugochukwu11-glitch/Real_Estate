# 🏡 Nigeria Real Estate Intelligence Platform

> A data-driven platform providing clean, localized insights into Nigerian real estate markets using scraped listings, analytics, and interactive dashboards.

---

## 📌 Overview

Real estate decisions in Nigeria are often driven by fragmented listings, agent opinions, and anecdotal information. There is limited access to **centralized, data-backed insights** on pricing trends, land values, and market movement across cities.

This project addresses that gap by building a **Nigeria Real Estate Intelligence Platform** that aggregates property listings, cleans and normalizes the data, and delivers actionable insights through an interactive dashboard and API-ready architecture.

---

## 🎯 Objective

The primary goals of this project were to:

- Aggregate property listings across major Nigerian cities  
- Clean and normalize inconsistent real estate data  
- Separate fundamentally different asset types (buildings vs land)  
- Provide reliable pricing benchmarks and market trends  
- Deliver insights via a public dashboard designed for decision-making  

---

## 📊 Data Collection

- Scraped **4,000+ property listings**
- Sources included major Nigerian property platforms
- Property types covered:
  - Houses
  - Apartments
  - Duplexes
  - Land
- Key attributes extracted:
  - Price
  - Location
  - City
  - Bedrooms
  - Property category
  - Listing dates

The focus was on **broad city coverage**, enabling cross-market comparison rather than a single-location snapshot.

---

## 🧹 Data Cleaning & Structuring

Real estate data is inherently noisy. Several critical cleaning and modeling decisions were made:

- Removed rentals, shortlets, and lease listings  
- Converted all prices into numeric NGN values  
- Converted USD-denominated prices using current exchange rates  
- Separated **land** from **buildings** to avoid analytical distortion  
- Standardized city and location names  
- Engineered analytical features:
  - `price_per_bedroom`
  - `month_posted`
  - normalized property categories  
- Used **median** instead of mean to reduce the impact of luxury outliers  
- Trimmed extreme values (top 1%)  

These decisions ensure the insights reflect **typical market behavior**, not edge cases.

---

## 📈 Analytics & Insights

The platform supports multiple layers of real estate intelligence:

### 🏙️ Market Pricing
- Median property prices by city  
- Top 10 most expensive areas (median-based)

### 📉 Trend Analysis
- Monthly median price trends  
- City-level **Month-over-Month (MoM)** growth  
- Emerging **Year-over-Year (YoY)** growth where sufficient history exists  

### 🌍 Land Intelligence
- Median land prices per square meter (₦/sqm) by city  
- Identification of high-value land locations  

### 🛏️ Value Analysis
- Price per bedroom comparison  
- Location-level value benchmarking across cities  

---

## 🧱 Product Output

- **Public Streamlit dashboard**
  - Interactive filters
  - Clean UX with analytical safeguards
  - Downloadable datasets (CSV exports)
- **API-ready backend**
  - Designed to expose aggregated metrics programmatically
- **Scalable architecture**
  - Supports future automation and data expansion  

The dashboard is built as a **decision-support tool**, not just a visualization.

---

## ⚠️ Limitations

- Historical depth varies by city  
- Some markets lack sufficient data for stable long-term YoY analysis  
- Insights will improve as more historical data is collected over time  

These limitations are explicitly acknowledged and handled gracefully within the platform.

---

## 🚀 What’s Next

Planned next steps include:

- Expanding historical coverage across cities  
- Automating recurring data collection  
- Connecting the dashboard directly to live APIs  
- Extending into brand and consumer intelligence  
- Monetizing insights via subscriptions and custom reports  

---

## 💡 Why This Matters

This project demonstrates the **end-to-end lifecycle of a real-world data product**:

- Problem framing  
- Data acquisition  
- Cleaning and modeling decisions  
- Analytics design  
- UX considerations  
- Deployment and delivery  

It shows how **local data**, when properly structured and analyzed, can drive **smarter decisions in emerging markets**.

---

## 🔗 Live Demo

👉 **https://ngrealestate.streamlit.app**

---

## 🧠 Final Note

This is not a toy project or a learning exercise.

It is a **shipped, public, data intelligence product** — designed with real-world constraints, business logic, and analytical rigor.

---

*Built with Python, Pandas, Streamlit, and a focus on practical decision-making.*
