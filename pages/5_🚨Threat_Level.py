import streamlit as st
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from utils.data_loader import load_data

st.set_page_config(page_title="Threat Level Prediction", page_icon="🚨", layout="wide")
st.title("🚨 AI Threat Level Prediction System")

# Cache model training so page reloads instantly
@st.cache_resource
def train_threat_model():
    df = load_data()
    features = ["country_txt", "region_txt", "attacktype1_txt", "weaptype1_txt", "targtype1_txt", "nkill", "nwound"]
    clean_df = df[features].dropna().copy()
    clean_df["impact"] = clean_df["nkill"] + clean_df["nwound"]

    def classify_threat(x):
        if x <= 2: return "LOW"
        elif x <= 10: return "MEDIUM"
        else: return "HIGH"

    clean_df["threat_level"] = clean_df["impact"].apply(classify_threat)

    encoders = {}
    for col in ["country_txt", "region_txt", "attacktype1_txt", "weaptype1_txt", "targtype1_txt"]:
        le = LabelEncoder()
        clean_df[col] = le.fit_transform(clean_df[col])
        encoders[col] = le

    target_encoder = LabelEncoder()
    clean_df["threat_level"] = target_encoder.fit_transform(clean_df["threat_level"])

    X = clean_df[["country_txt", "region_txt", "attacktype1_txt", "weaptype1_txt", "targtype1_txt", "nkill", "nwound"]]
    y = clean_df["threat_level"]

    X_train, _, y_train, _ = train_test_split(X, y, test_size=0.2, random_state=42)
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    rf_model.fit(X_train, y_train)

    return rf_model, encoders, target_encoder

model, encoders, target_encoder = train_threat_model()

# Inputs Configuration
st.sidebar.header("🎯 Input Parameters")
country_sel = st.sidebar.selectbox("Country", sorted(encoders["country_txt"].classes_))
region_sel = st.sidebar.selectbox("Region", sorted(encoders["region_txt"].classes_))
attack_sel = st.sidebar.selectbox("Attack Type", sorted(encoders["attacktype1_txt"].classes_))
weapon_sel = st.sidebar.selectbox("Weapon Type", sorted(encoders["weaptype1_txt"].classes_))
target_sel = st.sidebar.selectbox("Target Type", sorted(encoders["targtype1_txt"].classes_))

nkill = st.sidebar.number_input("Fatalities (Number Killed)", 0, 1000, 0)
nwound = st.sidebar.number_input("Injuries (Number Wounded)", 0, 1000, 0)

if st.button("🚨 Assess Threat Level"):
    input_vector = np.array([[
        encoders["country_txt"].transform([country_sel])[0],
        encoders["region_txt"].transform([region_sel])[0],
        encoders["attacktype1_txt"].transform([attack_sel])[0],
        encoders["weaptype1_txt"].transform([weapon_sel])[0],
        encoders["targtype1_txt"].transform([target_sel])[0],
        nkill,
        nwound
    ]])

    pred = model.predict(input_vector)
    probabilities = model.predict_proba(input_vector)[0]
    res_label = target_encoder.inverse_transform(pred)[0]
    confidence = np.max(probabilities) * 100

    st.subheader("🔍 Intelligence Assessment Result")

    c1, c2 = st.columns([2, 1])
    with c1:
        if res_label == "LOW":
            st.success(f"🟢 Threat Level Rating: **{res_label}**")
        elif res_label == "MEDIUM":
            st.warning(f"🟡 Threat Level Rating: **{res_label}**")
        else:
            st.error(f"🔴 Threat Level Rating: **{res_label}**")

    with c2:
        st.metric("Assessment Confidence", f"{confidence:.2f}%")

    prob_df = pd.DataFrame({
        "Threat Level": target_encoder.classes_,
        "Probability": probabilities
    })
    st.bar_chart(prob_df.set_index("Threat Level"), width="stretch")