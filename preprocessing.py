# preprocessing.py
import pandas as pd
import numpy as np
from pathlib import Path

# === CONFIG ===
DATA_DIR = Path(".")       # current folder
OUT_DIR = Path("./processed")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def safe_div(a, b):
    return np.where((b == 0) | pd.isna(b), np.nan, a / b)

def read_marketing_file(path, channel_name):
    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]
    if "attributed revenue" in df.columns:
        df = df.rename(columns={"attributed revenue": "attributed_revenue"})
    for col in ["impressions","clicks","spend","attributed_revenue"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        else:
            df[col] = 0
    df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.normalize()
    df['channel'] = channel_name
    for col in ["tactic","state","campaign"]:
        if col not in df.columns:
            df[col] = None
    return df[['date','channel','tactic','state','campaign','impressions','clicks','spend','attributed_revenue']]

# === Read campaign CSVs ===
fb = read_marketing_file(DATA_DIR / "Facebook.csv", "Facebook")
gg = read_marketing_file(DATA_DIR / "Google.csv", "Google")
tt = read_marketing_file(DATA_DIR / "TikTok.csv", "TikTok")

marketing = pd.concat([fb, gg, tt], ignore_index=True, sort=False)
marketing['cpc'] = safe_div(marketing['spend'], marketing['clicks'])
marketing['cpm'] = safe_div(marketing['spend'], marketing['impressions']) * 1000
marketing['ctr'] = safe_div(marketing['clicks'], marketing['impressions'])
marketing['roas'] = safe_div(marketing['attributed_revenue'], marketing['spend'])
marketing['state'] = marketing['state'].astype(str).str.strip().replace({'nan': None})

# Campaign-level aggregation
marketing_campaign = marketing.groupby(
    ['date','channel','tactic','state','campaign'], as_index=False
).agg({
    'impressions':'sum','clicks':'sum','spend':'sum','attributed_revenue':'sum'
})
marketing_campaign['cpc'] = safe_div(marketing_campaign['spend'], marketing_campaign['clicks'])
marketing_campaign['cpm'] = safe_div(marketing_campaign['spend'], marketing_campaign['impressions'])*1000
marketing_campaign['ctr'] = safe_div(marketing_campaign['clicks'], marketing_campaign['impressions'])
marketing_campaign['roas'] = safe_div(marketing_campaign['attributed_revenue'], marketing_campaign['spend'])

# === Business table ===
business = pd.read_csv(DATA_DIR / "Business.csv")

# Normalize column names
business.columns = [c.strip().lower() for c in business.columns]

# Map actual CSV column names -> expected names
rename_map = {
    '# of orders': 'orders',
    '# of new orders': 'new_orders',
    'new customers': 'new_customers',
    'total revenue': 'total_revenue',
    'gross profit': 'gross_profit',
    'cogs': 'cogs'
}
business = business.rename(columns=rename_map)

# Parse types
business['date'] = pd.to_datetime(business['date'], errors='coerce').dt.normalize()
for col in ['orders','new_orders','new_customers']:
    if col in business.columns:
        business[col] = pd.to_numeric(business[col], errors='coerce').fillna(0).astype(int)
for col in ['total_revenue','gross_profit','cogs']:
    if col in business.columns:
        business[col] = pd.to_numeric(business[col], errors='coerce').fillna(0.0)

# Derived metrics
business['avg_order_value'] = safe_div(business['total_revenue'], business['orders'])
business['gross_margin_pct'] = safe_div(business['gross_profit'], business['total_revenue'])

# === Calendar table ===
min_date = min(marketing['date'].min(), business['date'].min())
max_date = max(marketing['date'].max(), business['date'].max())
cal = pd.DataFrame({'date': pd.date_range(start=min_date, end=max_date, freq='D')})
cal['day'] = cal['date'].dt.day
cal['month'] = cal['date'].dt.month_name()
cal['month_num'] = cal['date'].dt.month
cal['quarter'] = cal['date'].dt.quarter
cal['year'] = cal['date'].dt.year

# === Save outputs ===
marketing.to_parquet(OUT_DIR / "marketing_raw.parquet", index=False)
marketing_campaign.to_parquet(OUT_DIR / "marketing_campaign.parquet", index=False)
business.to_parquet(OUT_DIR / "business.parquet", index=False)
cal.to_parquet(OUT_DIR / "calendar.parquet", index=False)

print("✅ Preprocessing done. Cleaned files are in ./processed/")