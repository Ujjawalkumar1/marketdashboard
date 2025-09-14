# 📊 Marketing Intelligence Dashboard

A **Business Intelligence (BI) dashboard** that integrates marketing campaign data from **Facebook, Google, and TikTok** with **e-commerce business performance** to understand how marketing spend drives revenue, orders, profit, and customer growth.  

Built with **Python, Pandas, Streamlit, and Plotly**.  

---

## 🚀 Features
- **Executive Summary**  
  - KPI cards for Spend, Revenue, Profit, ROAS, Orders, New Customers  
  - Time series: Marketing Spend vs Business Revenue  
  - Channel performance comparison  
  - Geographic spend/revenue distribution (if available)  

- **Marketing Performance**  
  - Channel-level CTR, CPC, CPM  
  - Top 10 campaigns by ROAS  
  - Spend vs Clicks vs Revenue trends  

- **Business Outcomes**  
  - Orders & new customers over time  
  - Gross profit and margin analysis  
  - Funnel: Impressions → Clicks → Orders → Revenue  

---

## 🗂️ Project Structure
marketing-intelligence-dashboard/
│
├── app_streamlit.py # Streamlit app (dashboard UI)
├── preprocessing.py # Data cleaning & processing script
├── requirements.txt # Python dependencies
├── Facebook.csv # Raw Facebook campaign data
├── Google.csv # Raw Google campaign data
├── TikTok.csv # Raw TikTok campaign data
├── Business.csv # E-commerce performance data
├── processed/ # Folder with cleaned .parquet files
└── README.md # Project documentation
Data Model

Marketing Table → Facebook, Google, TikTok campaigns (impressions, clicks, spend, attributed revenue)

Business Table → Orders, Revenue, Profit, New Customers

Calendar Table → Time intelligence (day, month, quarter, year)

Joined by date

🔑 Key Metrics

CPC (Cost per Click) = Spend ÷ Clicks

CPM (Cost per 1000 Impressions) = Spend ÷ Impressions × 1000

CTR (Click Through Rate) = Clicks ÷ Impressions

ROAS (Return on Ad Spend) = Attributed Revenue ÷ Spend

AOV (Average Order Value) = Revenue ÷ Orders

Gross Margin % = Gross Profit ÷ Revenue
