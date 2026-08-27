import pandas as pd
import streamlit as st

@st.cache_data
def load_data():

    df = pd.read_csv(
        "data/globalterrorism.csv",
        encoding="latin1",
        low_memory=False
    )

    df["nkill"] = df["nkill"].fillna(0)
    df["nwound"] = df["nwound"].fillna(0)

    return df