import streamlit as st
import joblib
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Attack Prediction", page_icon="🤖", layout="wide")
st.title("🤖 Tactical Attack Type Prediction")

# Load model artifacts safely
try:
    model = joblib.load("models/attack_prediction_model.pkl")
    encoders = joblib.load("models/feature_encoders.pkl")
    target_encoder = joblib.load("models/target_encoder.pkl")
except Exception as e:
    st.error("⚠️ Model files not found. Please run `py train_attack_model.py` in your terminal first.")
    st.stop()

st.markdown("Select operational and geographic parameters to predict the target attack classification using Machine Learning.")

# Form Input Controls
with st.form("prediction_form"):
    col1, col2 = st.columns(2)
    with col1:
        country = st.selectbox("🌍 Country", sorted(encoders["country_txt"].classes_))
        region = st.selectbox("🌎 Region", sorted(encoders["region_txt"].classes_))
        weapon = st.selectbox("🔫 Weapon Type", sorted(encoders["weaptype1_txt"].classes_))
        target = st.selectbox("🎯 Target Type", sorted(encoders["targtype1_txt"].classes_))

    with col2:
        group = st.selectbox("👥 Terrorist Group", sorted(encoders["gname"].classes_))
        success = st.selectbox("✅ Attack Successful?", [1, 0], format_func=lambda x: "Yes" if x == 1 else "No")
        suicide = st.selectbox("💣 Suicide Attack?", [1, 0], format_func=lambda x: "Yes" if x == 1 else "No")
        nkill = st.number_input("☠ Estimated Fatalities", min_value=0, max_value=5000, value=0, step=1)
        nwound = st.number_input("🏥 Estimated Injured", min_value=0, max_value=5000, value=0, step=1)

    submitted = st.form_submit_button("🚀 Run Prediction Model")

# Prediction Execution Block
if submitted:
    c_enc = encoders["country_txt"].transform([country])[0]
    r_enc = encoders["region_txt"].transform([region])[0]
    w_enc = encoders["weaptype1_txt"].transform([weapon])[0]
    t_enc = encoders["targtype1_txt"].transform([target])[0]
    g_enc = encoders["gname"].transform([group])[0]

    input_df = pd.DataFrame({
        "country_txt": [c_enc],
        "region_txt": [r_enc],
        "weaptype1_txt": [w_enc],
        "targtype1_txt": [t_enc],
        "gname": [g_enc],
        "success": [success],
        "suicide": [suicide],
        "nkill": [nkill],
        "nwound": [nwound]
    })

    pred = model.predict(input_df)
    predicted_label = target_encoder.inverse_transform(pred)[0]
    probabilities = model.predict_proba(input_df)[0]
    confidence = probabilities.max() * 100

    st.divider()
    res1, res2 = st.columns([2, 1])
    with res1:
        st.success(f"🎯 Predicted Attack Type: **{predicted_label}**")
    with res2:
        st.metric("Model Confidence Score", f"{confidence:.2f}%")

    # Probability Distribution Plot
    prob_df = pd.DataFrame({
        "Attack Class": target_encoder.classes_,
        "Probability (%)": probabilities * 100
    }).sort_values("Probability (%)", ascending=False).head(5)

    fig_prob = px.bar(prob_df, x="Probability (%)", y="Attack Class", orientation="h", title="Top 5 Classification Probabilities", color="Probability (%)", color_continuous_scale="Blues")
    fig_prob.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig_prob, width="stretch")