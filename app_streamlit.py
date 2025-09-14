# app_streamlit.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

st.set_page_config(layout="wide", page_title="Marketing Intelligence Dashboard")

DATA_DIR = Path("./processed")

# Load processed data
if (DATA_DIR / "marketing_campaign.parquet").exists():
    marketing = pd.read_parquet(DATA_DIR / "marketing_campaign.parquet")
    business = pd.read_parquet(DATA_DIR / "business.parquet")
    cal = pd.read_parquet(DATA_DIR / "calendar.parquet")
else:
    st.error("❌ Processed files not found. Please run preprocessing.py first.")
    st.stop()

# Sidebar filters
st.sidebar.header("Filters")
min_date = min(marketing['date'].min(), business['date'].min())
max_date = max(marketing['date'].max(), business['date'].max())
date_range = st.sidebar.date_input("Date range", value=(min_date.date(), max_date.date()))
channels = st.sidebar.multiselect("Channel", options=sorted(marketing['channel'].unique()),
                                  default=list(marketing['channel'].unique()))
start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
mkt = marketing[(marketing['date'] >= start) & (marketing['date'] <= end) & (marketing['channel'].isin(channels))]
biz = business[(business['date'] >= start) & (business['date'] <= end)]

# KPIs
total_spend = mkt['spend'].sum()
total_attr_revenue = mkt['attributed_revenue'].sum()
total_revenue = biz['total_revenue'].sum()
total_orders = biz['orders'].sum()
gross_profit = biz['gross_profit'].sum()
roas = (total_attr_revenue / total_spend) if total_spend > 0 else np.nan

page = st.sidebar.radio("Page", ["Executive Summary","Marketing Performance","Business Outcomes"])

if page == "Executive Summary":
    st.title("Executive Summary")
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Spend", f"₹{total_spend:,.0f}")
    c2.metric("Revenue", f"₹{total_revenue:,.0f}")
    c3.metric("Gross Profit", f"₹{gross_profit:,.0f}")
    c4.metric("ROAS", f"{roas:.2f}" if not np.isnan(roas) else "N/A")
    c5.metric("Orders", f"{int(total_orders):,}")

    ts = mkt.groupby('date', as_index=False)['spend'].sum().merge(
        biz.groupby('date', as_index=False)['total_revenue'].sum(),
        on='date', how='outer').fillna(0)
    fig = px.bar(ts, x='date', y='spend', title="Spend vs Revenue")
    fig.add_scatter(x=ts['date'], y=ts['total_revenue'], mode='lines', name='Revenue', yaxis='y2')
    fig.update_layout(yaxis2=dict(overlaying='y', side='right'))
    st.plotly_chart(fig, use_container_width=True)

elif page == "Marketing Performance":
    st.title("Marketing Performance")
    ch = mkt.groupby('channel', as_index=False).agg({'impressions':'sum','clicks':'sum','spend':'sum','attributed_revenue':'sum'})
    ch['ctr'] = ch['clicks']/ch['impressions'].replace({0:np.nan})
    ch['cpc'] = ch['spend']/ch['clicks'].replace({0:np.nan})
    ch['cpm'] = ch['spend']*1000/ch['impressions'].replace({0:np.nan})
    st.dataframe(ch)

    camp = mkt.groupby(['channel','campaign'], as_index=False).agg({'spend':'sum','attributed_revenue':'sum'})
    camp['roas'] = camp['attributed_revenue']/camp['spend'].replace({0:np.nan})
    st.subheader("Top Campaigns by ROAS")
    st.dataframe(camp.sort_values('roas', ascending=False).head(10))

elif page == "Business Outcomes":
    st.title("Business Outcomes")
    ord_ts = biz.groupby('date', as_index=False).agg({'orders':'sum','new_customers':'sum'})
    fig = px.area(ord_ts, x='date', y=['orders','new_customers'])
    st.plotly_chart(fig, use_container_width=True)
