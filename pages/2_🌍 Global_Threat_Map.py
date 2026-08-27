import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_data

st.set_page_config(
    page_title="Global Threat Map",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 Global Threat & Spatial Intelligence Map")

# Load GTD Data
df = load_data()

# Drop rows missing coordinates for spatial mapping
spatial_df = df.dropna(subset=["latitude", "longitude"]).copy()

# -------------------------------------------------------------
# Sidebar Map Controls & Filters
# -------------------------------------------------------------
st.sidebar.header("🎯 Spatial Filters")

# Map Display Mode Switcher
map_mode = st.sidebar.radio(
    "Map Display Mode",
    ["Scatter Point Map", "Country Heatmap (Choropleth)"],
    index=0
)

# Temporal & Categorical Filters
years = ["All"] + sorted(spatial_df["iyear"].unique().tolist())
selected_year = st.sidebar.selectbox("Year", years)

regions = sorted(spatial_df["region_txt"].dropna().unique().tolist())
selected_region = st.sidebar.multiselect("Region", regions, default=[])

attack_types = sorted(spatial_df["attacktype1_txt"].dropna().unique().tolist())
selected_attacks = st.sidebar.multiselect("Attack Type", attack_types, default=[])

min_kills = st.sidebar.slider("Min Fatalities Threshold", 0, int(spatial_df["nkill"].max()), 0)

st.sidebar.header("⚙️ Map Settings & Performance")

# Projection Control
projection = st.sidebar.selectbox(
    "Map Projection",
    ["natural earth", "orthographic", "mercator", "equirectangular"],
    index=0
)

# Anti-Freeze Sampling Control (Prevents browser tab lockup on large data)
max_display_points = st.sidebar.slider(
    "Max Mapped Markers (Performance Cap)",
    min_value=500,
    max_value=15000,
    value=3000,
    step=500,
    help="Limits mapped scatter points to preserve rendering speed."
)

# -------------------------------------------------------------
# Data Filtering Pipeline
# -------------------------------------------------------------
filtered_df = spatial_df.copy()

if selected_year != "All":
    filtered_df = filtered_df[filtered_df["iyear"] == selected_year]

if selected_region:
    filtered_df = filtered_df[filtered_df["region_txt"].isin(selected_region)]

if selected_attacks:
    filtered_df = filtered_df[filtered_df["attacktype1_txt"].isin(selected_attacks)]

if min_kills > 0:
    filtered_df = filtered_df[filtered_df["nkill"] >= min_kills]

# -------------------------------------------------------------
# Dynamic Map KPIs
# -------------------------------------------------------------
m1, m2, m3, m4 = st.columns(4)

mapped_count = len(filtered_df)
total_mapped_kills = int(filtered_df["nkill"].sum())
top_country = filtered_df["country_txt"].mode()[0] if not filtered_df.empty else "N/A"
top_attack = filtered_df["attacktype1_txt"].mode()[0] if not filtered_df.empty else "N/A"

m1.metric("Matching Incidents", f"{mapped_count:,}")
m2.metric("Total Fatalities", f"{total_mapped_kills:,}")
m3.metric("Primary Hotspot", top_country)
m4.metric("Leading Attack Type", top_attack)

st.divider()

# -------------------------------------------------------------
# Map Rendering Logic
# -------------------------------------------------------------
if filtered_df.empty:
    st.warning("⚠️ No incident data found matching the selected filter criteria.")
else:
    if map_mode == "Scatter Point Map":
        # Apply anti-freeze sampling if dataset exceeds maximum threshold
        if len(filtered_df) > max_display_points:
            render_df = filtered_df.sample(n=max_display_points, random_state=42)
            st.info(f"⚡ Performance mode active: Displaying a representative sample of **{max_display_points:,}** markers out of **{len(filtered_df):,}** total matching incidents. Adjust the slider in the sidebar to view more.")
        else:
            render_df = filtered_df

        fig = px.scatter_geo(
            render_df,
            lat="latitude",
            lon="longitude",
            color="attacktype1_txt",
            hover_name="country_txt",
            hover_data={
                "city": True,
                "iyear": True,
                "gname": True,
                "nkill": True,
                "nwound": True,
                "latitude": False,
                "longitude": False
            },
            projection=projection,
            height=680,
            opacity=0.7,
            title=f"Geographical Incident Map ({projection.title()} View)"
        )
        fig.update_layout(margin=dict(l=0, r=0, t=40, b=0), legend_title_text="Attack Type")
        st.plotly_chart(fig, width="stretch")

    elif map_mode == "Country Heatmap (Choropleth)":
        country_agg = filtered_df.groupby("country_txt").agg(
            Incidents=("iyear", "count"),
            Fatalities=("nkill", "sum")
        ).reset_index()

        fig = px.choropleth(
            country_agg,
            locations="country_txt",
            locationmode="country names",
            color="Incidents",
            hover_name="country_txt",
            hover_data=["Incidents", "Fatalities"],
            color_continuous_scale="Reds",
            projection=projection,
            height=680,
            title="Country Incident Density Heatmap"
        )
        fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig, width="stretch")

    # -------------------------------------------------------------
    # Data Table Snapshot
    # -------------------------------------------------------------
    with st.expander("📋 View Mapped Data Snapshot"):
        preview_cols = ["iyear", "country_txt", "city", "attacktype1_txt", "gname", "nkill", "nwound", "latitude", "longitude"]
        st.dataframe(filtered_df[preview_cols].head(100), width="stretch", hide_index=True)