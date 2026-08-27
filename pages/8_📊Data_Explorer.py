import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_data

st.set_page_config(page_title="Data Explorer", page_icon="📊", layout="wide")
st.title("📊 Global Terrorism Data Explorer")

df = load_data()

st.sidebar.header("🎯 Multi-Variable Filters")
selected_years = st.sidebar.multiselect("Filter Years", sorted(df["iyear"].unique()))
selected_countries = st.sidebar.multiselect("Filter Countries", sorted(df["country_txt"].dropna().unique()))
selected_attacks = st.sidebar.multiselect("Filter Attack Types", sorted(df["attacktype1_txt"].dropna().unique()))

filtered_df = df.copy()
if selected_years:
    filtered_df = filtered_df[filtered_df["iyear"].isin(selected_years)]
if selected_countries:
    filtered_df = filtered_df[filtered_df["country_txt"].isin(selected_countries)]
if selected_attacks:
    filtered_df = filtered_df[filtered_df["attacktype1_txt"].isin(selected_attacks)]

# Free Text Search
search_term = st.text_input("🔍 Search by City or Terrorist Group Name")
if search_term:
    filtered_df = filtered_df[
        filtered_df["city"].fillna("").str.contains(search_term, case=False) |
        filtered_df["gname"].fillna("").str.contains(search_term, case=False)
    ]

# Summary KPI Bar
st.subheader("Filtered Dataset Snapshot")
d1, d2, d3, d4 = st.columns(4)
d1.metric("Total Rows", f"{len(filtered_df):,}")
d2.metric("Countries Represented", filtered_df["country_txt"].nunique())
d3.metric("Fatalities Sum", int(filtered_df["nkill"].sum()))
d4.metric("Injuries Sum", int(filtered_df["nwound"].sum()))

st.divider()

# Tabs for Data View & Summary Stats
tab_data, tab_stats = st.tabs(["📋 Data Records View", "📈 Statistical Summary"])

with tab_data:
    all_cols = filtered_df.columns.tolist()
    default_cols = ["iyear", "country_txt", "city", "attacktype1_txt", "targtype1_txt", "gname", "nkill", "nwound"]
    selected_cols = st.multiselect("Customize Display Columns", all_cols, default=[c for c in default_cols if c in all_cols])
    
    st.dataframe(filtered_df[selected_cols], width="stretch", height=420)
    
    csv = filtered_df[selected_cols].to_csv(index=False).encode()
    st.download_button("📥 Export Current Filtered CSV", csv, file_name="filtered_gtd_export.csv", mime="text/csv")

with tab_stats:
    st.subheader("Numeric Column Descriptives")
    st.dataframe(filtered_df[["iyear", "nkill", "nwound", "success", "suicide"]].describe(), width="stretch")