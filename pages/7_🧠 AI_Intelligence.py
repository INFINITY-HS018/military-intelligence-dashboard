import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_data

st.set_page_config(page_title="AI Intelligence Report", page_icon="🧠", layout="wide")
st.title("🧠 Automated AI Intelligence Summary")

df = load_data()

st.sidebar.header("🎯 Scope Filters")
years = ["All"] + sorted(df["iyear"].unique().tolist())
selected_year = st.sidebar.selectbox("Year Filter", years)
regions = ["All"] + sorted(df["region_txt"].dropna().unique().tolist())
selected_region = st.sidebar.selectbox("Region Filter", regions)

filtered_df = df.copy()
if selected_year != "All":
    filtered_df = filtered_df[filtered_df["iyear"] == selected_year]
if selected_region != "All":
    filtered_df = filtered_df[filtered_df["region_txt"].isin([selected_region])]

total_incidents = len(filtered_df)
total_killed = int(filtered_df["nkill"].sum())
total_wounded = int(filtered_df["nwound"].sum())
avg_kills = filtered_df["nkill"].mean() if total_incidents > 0 else 0

threat_rating = "LOW 🟢" if avg_kills < 1.5 else "MEDIUM 🟡" if avg_kills < 4.0 else "HIGH 🔴"

# Key Indicators
st.subheader("📊 Primary Operational Indicators")
k1, k2, k3, k4 = st.columns(4)
k1.metric("Recorded Incidents", f"{total_incidents:,}")
k2.metric("Total Fatalities", f"{total_killed:,}")
k3.metric("Total Injuries", f"{total_wounded:,}")
k4.metric("Assessed Threat Posture", threat_rating)

st.divider()

if total_incidents > 0:
    top_country = filtered_df["country_txt"].mode()[0]
    top_group = filtered_df[filtered_df["gname"] != "Unknown"]["gname"].mode()
    group_name = top_group[0] if not top_group.empty else "Unidentified Factions"
    top_weapon = filtered_df["weaptype1_txt"].mode()[0]

    # Executive Summary Text Box
    st.subheader("📝 Executive Summary")
    exec_text = f"""
    During the specified operational period, a total of **{total_incidents:,}** incidents were logged within the scope.
    These events led to **{total_killed:,}** fatalities and **{total_wounded:,}** reported injuries.
    
    * **Primary Hotspot Region/Country:** {top_country}
    * **Most Active Identified Faction:** {group_name}
    * **Dominant Armament Category:** {top_weapon}
    * **Overall Operational Posture:** Assessed as **{threat_rating}**.
    """
    st.info(exec_text)

    # Charts
    c1, c2 = st.columns(2)
    with c1:
        top_c_df = filtered_df["country_txt"].value_counts().head(8).reset_index()
        top_c_df.columns = ["Country", "Attacks"]
        fig1 = px.bar(top_c_df, x="Attacks", y="Country", orientation="h", title="Highest Risk Countries", color="Attacks")
        fig1.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig1, width="stretch")

    with c2:
        top_t_df = filtered_df["targtype1_txt"].value_counts().head(8).reset_index()
        top_t_df.columns = ["Target Sector", "Attacks"]
        fig2 = px.bar(top_t_df, x="Attacks", y="Target Sector", orientation="h", title="Top Target Categories", color="Attacks")
        fig2.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig2, width="stretch")
else:
    st.warning("No incident data matching criteria.")