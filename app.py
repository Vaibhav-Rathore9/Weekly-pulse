import pandas as pd
import streamlit as st
from collections import Counter

st.title("Groww Weekly Pulse Generator")

uploaded_file = st.file_uploader("Upload Reviews CSV", type=["csv"])

def simple_theme_classifier(text):
    text = text.lower()
    if "kyc" in text or "verify" in text:
        return "KYC"
    elif "crash" in text or "slow" in text or "lag" in text:
        return "Performance"
    elif "withdraw" in text or "money" in text:
        return "Withdrawals"
    elif "payment" in text or "upi" in text:
        return "Payments"
    else:
        return "Others"

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df["theme"] = df["text"].apply(simple_theme_classifier)

    st.subheader("Top Themes")
    st.write(df["theme"].value_counts().head(3))

    st.subheader("Sample Quotes")
    st.write(df[["text"]].head(3))

    st.success("Weekly pulse ready (use LLM for final polish)")
