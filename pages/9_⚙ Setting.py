import streamlit as st
import json

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")
st.title("⚙️ Dashboard Configuration & Preferences")

# Session State Initialization
if "theme" not in st.session_state:
    st.session_state["theme"] = "Dark"
if "default_country" not in st.session_state:
    st.session_state["default_country"] = "India"
if "confidence_threshold" not in st.session_state:
    st.session_state["confidence_threshold"] = 75

st.header("🎨 Appearance & Global Defaults")

st.session_state["theme"] = st.selectbox("Application Theme", ["Dark", "Light"], index=0 if st.session_state["theme"] == "Dark" else 1)
st.session_state["default_country"] = st.text_input("Default Focus Country", st.session_state["default_country"])
st.session_state["confidence_threshold"] = st.slider("Minimum Prediction Confidence Threshold (%)", 50, 95, st.session_state["confidence_threshold"])

st.divider()

st.header("💾 Configuration Management")
col_s, col_r = st.columns(2)

with col_s:
    if st.button("💾 Persist Preferences"):
        st.success("Configuration preferences successfully updated in active session state!")

with col_r:
    if st.button("🔄 Reset Defaults"):
        st.session_state["theme"] = "Dark"
        st.session_state["default_country"] = "India"
        st.session_state["confidence_threshold"] = 75
        st.warning("Configuration reset to initial default settings.")

# Export config JSON
config_dump = json.dumps(dict(st.session_state), indent=4)
st.download_button("📥 Export Settings File (JSON)", config_dump, file_name="dashboard_settings.json", mime="application/json")