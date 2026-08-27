import streamlit as st

st.set_page_config(
    page_title="AI Military Intelligence Dashboard",
    page_icon="🛡",
    layout="wide"
)

st.title("🛡 AI-Based Military Intelligence Dashboard")

st.markdown("""
### Welcome

This dashboard provides military intelligence analysis using the
Global Terrorism Database (GTD).

👈 Select a page from the sidebar.
""")

st.info("""
Available Modules

- 🏠 Home
- 🌍 Global Threat Map
- 🌎 Country Analysis
- 🤖 Attack Prediction
- 🚨 Threat Level Prediction
- 📈 Forecasting
- 🧠 AI Intelligence Report
- 📊 Data Explorer
- ⚙ Settings

👈 Use the **left sidebar** to navigate.
""")

st.info("Select a page from the sidebar to begin.")

