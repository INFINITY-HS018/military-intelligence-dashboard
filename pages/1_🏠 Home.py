import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import load_data

st.set_page_config(
    page_title="AI Military Intelligence Dashboard",
    page_icon="🛡️",
    layout="wide"
)

st.title("🏠 Executive Overview & Home Analytics")

# Load data using cached loader
df = load_data()

# -------------------------------------------------------------
# Sidebar Filter: Date Range & Region
# -------------------------------------------------------------
st.sidebar.header("🎯 Home Filters")

min_year = int(df["iyear"].min())
max_year = int(df["iyear"].max())

year_range = st.sidebar.slider(
    "Select Year Range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

selected_region = st.sidebar.multiselect(
    "Filter by Region",
    options=sorted(df["region_txt"].dropna().unique()),
    default=[]
)

# Filter dataset based on sidebar inputs
filtered_df = df[(df["iyear"] >= year_range[0]) & (df["iyear"] <= year_range[1])]

if selected_region:
    filtered_df = filtered_df[filtered_df["region_txt"].isin(selected_region)]

# -------------------------------------------------------------
# Top Metrics Bar (KPIs)
# -------------------------------------------------------------
st.subheader(f"📊 Global Summary ({year_range[0]} - {year_range[1]})")

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

total_incidents = len(filtered_df)
total_fatalities = int(filtered_df["nkill"].sum())
total_injured = int(filtered_df["nwound"].sum())
total_countries = filtered_df["country_txt"].nunique()
success_rate = (filtered_df["success"].mean() * 100) if total_incidents > 0 else 0

kpi1.metric("Incidents", f"{total_incidents:,}")
kpi2.metric("Fatalities", f"{total_fatalities:,}")
kpi3.metric("Injuries", f"{total_injured:,}")
kpi4.metric("Countries Affected", total_countries)
kpi5.metric("Attack Success Rate", f"{success_rate:.1f}%")

st.divider()

# -------------------------------------------------------------
# Row 1: Incident Trends & Attack Type Breakdown
# -------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Annual Attack & Casualties Trend")
    yearly_summary = filtered_df.groupby("iyear").agg({
        "country_txt": "count",
        "nkill": "sum",
        "nwound": "sum"
    }).reset_index().rename(columns={"country_txt": "Attacks", "nkill": "Fatalities", "nwound": "Injured"})

    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(x=yearly_summary["iyear"], y=yearly_summary["Attacks"], mode="lines+markers", name="Attacks", line=dict(color="#1f77b4", width=2)))
    fig_trend.add_trace(go.Scatter(x=yearly_summary["iyear"], y=yearly_summary["Fatalities"], mode="lines+markers", name="Fatalities", line=dict(color="#d62728", width=2)))
    fig_trend.update_layout(xaxis_title="Year", yaxis_title="Count", height=380, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_trend, width="stretch")

with col2:
    st.subheader("🎯 Top 7 Attack Tactics Breakdown")
    attack_counts = filtered_df["attacktype1_txt"].value_counts().head(7).reset_index()
    attack_counts.columns = ["Attack Type", "Count"]

    fig_attack = px.pie(
        attack_counts,
        names="Attack Type",
        values="Count",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_attack.update_layout(height=380, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_attack, width="stretch")

st.divider()

# -------------------------------------------------------------
# Row 2: Regional Impact & Top Perpetrator Groups
# -------------------------------------------------------------
col3, col4 = st.columns(2)

with col3:
    st.subheader("🌍 Most Affected Regions")
    region_counts = filtered_df["region_txt"].value_counts().head(8).reset_index()
    region_counts.columns = ["Region", "Incidents"]

    fig_region = px.bar(
        region_counts,
        x="Incidents",
        y="Region",
        orientation="h",
        color="Incidents",
        color_continuous_scale="Reds"
    )
    fig_region.update_layout(height=380, margin=dict(l=20, r=20, t=30, b=20), yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig_region, width="stretch")

with col4:
    st.subheader("👥 Most Active Recognized Groups")
    known_groups = filtered_df[filtered_df["gname"] != "Unknown"]
    group_counts = known_groups["gname"].value_counts().head(8).reset_index()
    group_counts.columns = ["Group", "Attacks"]

    fig_group = px.bar(
        group_counts,
        x="Attacks",
        y="Group",
        orientation="h",
        color="Attacks",
        color_continuous_scale="Viridis"
    )
    fig_group.update_layout(height=380, margin=dict(l=20, r=20, t=30, b=20), yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig_group, width="stretch")

st.divider()

# -------------------------------------------------------------
# High-Impact Incident Table
# -------------------------------------------------------------
st.subheader("🚨 High-Impact Incident Snapshot (Deadliest Attacks)")

display_cols = ["iyear", "country_txt", "city", "attacktype1_txt", "gname", "nkill", "nwound"]
high_impact_df = filtered_df.sort_values(by=["nkill", "nwound"], ascending=False).head(5)[display_cols]
high_impact_df.columns = ["Year", "Country", "City", "Attack Type", "Group", "Fatalities", "Injured"]

st.dataframe(high_impact_df, width="stretch", hide_index=True)

st.info("👈 Use the left sidebar to navigate to specialized analytics modules like forecasting, mapping, and AI prediction.")