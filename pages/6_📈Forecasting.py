import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from utils.data_loader import load_data

st.set_page_config(page_title="Forecasting", page_icon="📈", layout="wide")
st.title("📈 Terrorism Trend Forecasting & Projection")

df = load_data()

st.sidebar.header("🎯 Forecast Settings")
country_list = sorted(df["country_txt"].dropna().unique())
selected_country = st.sidebar.selectbox("Country Scope", country_list, index=country_list.index("India") if "India" in country_list else 0)
target_metric = st.sidebar.radio("Metric to Forecast", ["Attacks", "Fatalities"])
forecast_years = st.sidebar.slider("Projection Horizon (Years)", 1, 10, 5)

# Group dataset by year
country_df = df[df["country_txt"] == selected_country]
agg_col = "iyear"
if target_metric == "Attacks":
    yearly = country_df.groupby(agg_col).size().reset_index(name="MetricValue")
else:
    yearly = country_df.groupby(agg_col)["nkill"].sum().reset_index(name="MetricValue")

yearly = yearly.sort_values("iyear")

if len(yearly) < 5:
    st.warning("⚠️ Insufficient historical data points available to fit a linear regression forecast model.")
    st.stop()

# Model Fitting
X = yearly[["iyear"]]
y = yearly["MetricValue"]

lr = LinearRegression()
lr.fit(X, y)
r2_score = lr.score(X, y)

last_year = int(yearly["iyear"].max())
future_years = np.arange(last_year + 1, last_year + forecast_years + 1)
future_preds = np.maximum(lr.predict(pd.DataFrame({"iyear": future_years})), 0)

forecast_df = pd.DataFrame({
    "Year": future_years,
    f"Forecasted {target_metric}": future_preds.astype(int)
})

# Plotting Forecast
fig = go.Figure()
fig.add_trace(go.Scatter(x=yearly["iyear"], y=yearly["MetricValue"], mode="lines+markers", name="Historical Data", line=dict(color="#1f77b4", width=2)))
fig.add_trace(go.Scatter(x=forecast_df["Year"], y=forecast_df[f"Forecasted {target_metric}"], mode="lines+markers", name="Linear Projection", line=dict(color="#ff7f0e", dash="dash", width=2)))

fig.update_layout(title=f"Historical & Projected {target_metric} for {selected_country}", xaxis_title="Year", yaxis_title=target_metric, height=480)
st.plotly_chart(fig, width="stretch")

# Metrics & Growth Analysis
m1, m2, m3, m4 = st.columns(4)
current_val = yearly.iloc[-1]["MetricValue"]
proj_val = forecast_df.iloc[-1][f"Forecasted {target_metric}"]
growth_pct = ((proj_val - current_val) / max(current_val, 1)) * 100

m1.metric("Recent Historical Baseline", int(current_val))
m2.metric(f"Projected ({forecast_years} Yrs)", int(proj_val))
m3.metric("Projected Trajectory", f"{growth_pct:+.1f}%")
m4.metric("Model R² Fit Score", f"{r2_score:.2f}")

st.divider()
st.dataframe(forecast_df, width="stretch", hide_index=True)