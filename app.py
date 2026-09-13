# AuditFlow AI - app.py
# 여기부터 블록 2에서 직접 채운다.
# app.py가 실제로 "돌아가는 프로그램"이야
import streamlit as st
import pandas as pd 
from src.audit_rules import detect_risks
from src.policy_retriever import find_policy_evidence, chunks


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


    #함수는 "만들어 두는 것"과 "실제로  실행하는 것"이 별개라는 거.
    # from src.audit_rules import detect_risks 
    # risk_type : 어떤 위험인지 ,chunks : 검색할 규정 문서들 
    df = detect_risks(df) # detect_risks(df)가 risk_type컬럼을 만들어내는 함수다.
    risk_explanation = []
    for rt in df["risk_type"]:
        ev = find_policy_evidence(rt, chunks)   # rt(한 행의 위험유형 값)를 넣고, 결과는 ev에
        risk_explanation.append(ev)             # append는 한 개만: ev  append:ev에 들어 있는 값을 리스트 맨 뒤에 하나 추가하는 것이야.
    df["policy_evidence"] = risk_explanation    # for 밖! 다 모은 뒤 컬럼으로
    # df.loc[df["has_receipt"]=="N","risk_type"]="영수증누락"
    # df.loc[df["has_receipt"]=="N","risk_reason"]="영수증 없음" #별도 데이터 변수를 만든 게 아니기 때문
    st.dataframe(df)

    # ── 블록3: 검수용 요약 표 (위험유형 / 사유 / 규정 근거를 한 화면에) ──
    risk_df = df[df["risk_type"].notna()]   # 위험이 잡힌 행만 골라내기 (risk_type이 비어있지 않은 행)
    st.subheader("검수 결과 (위험 건)")
    st.dataframe(
        risk_df[["employee", "department", "category", "amount",
                 "risk_type", "risk_reason", "policy_evidence"]]
    )

    # ── 규정 근거가 안 붙은 건 = 사람이 직접 확인해야 하는 목록 ──
    missing_policy = df[df["policy_evidence"] == "관련 규정 확인 필요"]  # 함수 반환값과 글자를 정확히 맞춰야 걸러짐
    missing_types = missing_policy["risk_type"].dropna().unique()
    # dropna() : 비어있는 값 제외 / unique() : 중복 제거
    st.subheader("규정 근거 확인 필요")
    st.write("확인 필요 유형:", list(missing_types))
    st.dataframe(
        missing_policy[["employee", "category", "amount", "risk_type", "policy_evidence"]]
    )