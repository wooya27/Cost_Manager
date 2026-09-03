# AuditFlow AI - app.py
# 여기부터 블록 2에서 직접 채운다.

import streamlit as st
import pandas as pd 
from src.audit_rules import detect_risks

st.title("AuditFlow AI")
st.write("비용정산 1차 검수 어시스턴트")


uploaded = st.file_uploader("CSV 올리기", type="csv")

if uploaded:
    df = pd.read_csv(uploaded)
    st.dataframe(df) #실제 데이터 전체 보기  -->이한줄이 15개 행을 전부 표로 보여줌
    st.write("행",df.shape[0])
    st.write("열",df.shape[1])
    st.write("컬럼", list(df.columns))

    st.write("결측치",df.isna().sum())

 

    all_amount = df["amount"].sum()
    st.write("총 신청금액",all_amount)

    cat_sum = df.groupby("category")["amount"].sum()
    st.write("카테고리별 합",cat_sum) 
    df = detect_risks(df)
    # df.loc[df["has_receipt"]=="N","risk_type"]="영수증누락"
    # df.loc[df["has_receipt"]=="N","risk_reason"]="영수증 없음" #별도 데이터 변수를 만든 게 아니기 때문
    st.dataframe(df)