# AuditFlow AI - app.py
# 여기부터 블록 2에서 직접 채운다.

import streamlit as st
import pandas as pd

st.title("AuditFlow AI")
st.write("비용정산 1차 검수 어시스턴트")


uploaded = st.file_uploader("CSV 올리기", type="csv")

if uploaded:
    df = pd.read_csv(uploaded)
    st.dataframe(df)
