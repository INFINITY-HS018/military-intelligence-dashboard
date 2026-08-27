import streamlit as st
import plotly.express as px
from utils.data_loader import load_data

st.set_page_config(page_title="Country Analysis", page_icon="🌎", layout="wide")
st.title("🌎 Country-Level Intelligence Analysis")

df = load_data()

st.sidebar.header("🎯 Country Filters")
countries = sorted(df["country_txt"].dropna().unique())
selected_country = st.sidebar.selectbox("Select Country", countries, index=countries.index("India") if "India" in countries else 0)

min_yr, max_yr = int(df["iyear"].min()), int(df["iyear"].max())
selected_years = st.sidebar.slider("Year Range", min_yr, max_yr, (min_yr, max_yr))

# Filter data for country and year range
country_df = df[(df["country_txt"] == selected_country) & (df["iyear"] >= selected_years[0]) & (df["iyear"] <= selected_years[1])]

st.header(f"Intelligence Brief: {selected_country} ({selected_years[0]} - {selected_years[1]})")

if country_df.empty:
    st.warning("⚠️ No incident data recorded for this country during the selected timeframe.")
else:
    # Top KPI Metrics
    c1, c2, c3, c4, c5 = st.columns(5)
    total_attacks = len(country_df)
    total_kills = int(country_df["nkill"].sum())
    total_wounds = int(country_df["nwound"].sum())
    active_groups = country_df["gname"].nunique()
    success_rate = (country_df["success"].mean() * 100) if total_attacks > 0 else 0

    c1.metric("Total Incidents", f"{total_attacks:,}")
    c2.metric("Fatalities", f"{total_kills:,}")
    c3.metric("Injuries", f"{total_wounds:,}")
    c4.metric("Active Groups", active_groups)
    c5.metric("Success Rate", f"{success_rate:.1f}%")

    st.divider()

    # Time Series & Attack Type Charts
    col1, col2 = st.columns(2)
    with col1:
        yearly = country_df.groupby("iyear").size().reset_index(name="Attacks")
        fig_line = px.line(yearly, x="iyear", y="Attacks", markers=True, title="Incident Frequency Over Time")
        st.plotly_chart(fig_line, width="stretch")

    with col2:
        attack_dist = country_df["attacktype1_txt"].value_counts().reset_index()
        attack_dist.columns = ["Attack Type", "Count"]
        fig_pie = px.pie(attack_dist, names="Attack Type", values="Count", title="Tactical Attack Distribution")
        st.plotly_chart(fig_pie, width="stretch")

    st.divider()

    # Perpetrators & Targets
    col3, col4 = st.columns(2)
    with col3:
        top_groups = country_df[country_df["gname"] != "Unknown"]["gname"].value_counts().head(8).reset_index()
        top_groups.columns = ["Group", "Count"]
        fig_grp = px.bar(top_groups, x="Count", y="Group", orientation="h", title="Top Perpetrator Organizations", color="Count")
        fig_grp.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig_grp, width="stretch")

    with col4:
        top_targets = country_df["targtype1_txt"].value_counts().head(8).reset_index()
        top_targets.columns = ["Target Sector", "Count"]
        fig_targ = px.bar(top_targets, x="Count", y="Target Sector", orientation="h", title="Primary Targeted Sectors", color="Count")
        fig_targ.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig_targ, width="stretch")

    st.divider()

    # Incident Locations Map
    st.subheader("Geographical Incident Locations")
    map_df = country_df.dropna(subset=["latitude", "longitude"])
    if not map_df.empty:
        fig_map = px.scatter_geo(
            map_df, lat="latitude", lon="longitude", hover_name="city",
            hover_data={"iyear": True, "attacktype1_txt": True, "gname": True, "nkill": True},
            color="attacktype1_txt", projection="natural earth", height=500
        )
        st.plotly_chart(fig_map, width="stretch")
    else:
        st.info("No spatial coordinates available for geographical mapping.")

    # Data Table & Download
    with st.expander("📋 Detailed Incident Records"):
        preview_cols = ["iyear", "city", "attacktype1_txt", "targtype1_txt", "weaptype1_txt", "gname", "nkill", "nwound"]
        st.dataframe(country_df[preview_cols], width="stretch", hide_index=True)
        csv_data = country_df.to_csv(index=False).encode()
        st.download_button("📥 Download Country Data CSV", csv_data, file_name=f"{selected_country}_intelligence.csv", mime="text/csv")