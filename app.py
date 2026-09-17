# AuditFlow AI - app.py
# 여기부터 블록 2에서 직접 채운다.
# app.py가 실제로 "돌아가는 프로그램"이야
import streamlit as st
import pandas as pd 
from src.audit_rules import detect_risks
from src.policy_retriever import find_policy_evidence, policy_messages 
from src.draft_generator import make_draft

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
    # risk_type : 어떤 위험인지 ,policy_messages : 검색할 규정 문서들 
    df = detect_risks(df) # detect_risks(df)가 risk_type컬럼을 만들어내는 함수다.
    risk_explanation = []
    for rt in df["risk_type"]:
        ev = find_policy_evidence(rt, policy_messages)   # rt(한 행의 위험유형 값)를 넣고, 결과는 ev에
        risk_explanation.append(ev)             # append는 한 개만: ev  append:ev에 들어 있는 값을 리스트 맨 뒤에 하나 추가하는 것이야.
    df["policy_evidence"] = risk_explanation    # for 밖! 다 모은 뒤 컬럼으로

    draft_messages = []
    draft_sources = []
    for _, row in df.iterrows():
          message, source = make_draft(row)
          draft_messages.append(message)
          draft_sources.append(source)
    df["draft_message"] = draft_messages
    df["draft_source"] = draft_sources



    # df.loc[df["has_receipt"]=="N","risk_type"]="영수증누락"
    # df.loc[df["has_receipt"]=="N","risk_reason"]="영수증 없음" #별도 데이터 변수를 만든 게 아니기 때문
    st.dataframe(df)

    df["review_status"]= "미검토" #컬럼만들기 : df라는 표에 review_status라는 새로운 칸을 만들고, 처음에는 전부 "미검토"라고 적는다.
    

    # ── 블록3: 검수용 요약 표 (위험유형 / 사유 / 규정 근거를 한 화면에) ──
    risk_df = df[df["risk_type"].notna()]   # 위험이 잡힌 행만 골라내기 (risk_type이 비어있지 않은 행)

    st.subheader("Dashboard")

    total_count = df.shape[0]
    risk_count = risk_df.shape[0]
    total_amount = df["amount"].sum()

    col1, col2, col3 = st.columns(3)

    col1.metric("전체 신청 건수", df.shape[0])
    col2.metric("위험 건수",risk_df.shape[0])
    col3.metric("총 신청 금액", f"{ df["amount"].sum() }원")

    # 기존 위험 건 표
    st.subheader("검수 결과 (위험 건)")

    st.subheader("검수 결과 (위험 건)")
    st.dataframe(
        risk_df[["employee", "department", "category", "amount",
                 "risk_type", "risk_reason", "policy_evidence"]]
    )
   
    st.subheader("위험 건 상세확인")
    selected = st.selectbox("확인할 위험 건을 선택",risk_df.index)
    row = risk_df.loc[selected]

    st.write("신청자:",row["employee"])
    st.write("금액:",row["amount"])
    st.write("카테고리:", row["category"])
    st.write("위험 유형:", row["risk_type"])
    st.write("위험 사유:", row["risk_reason"])
    st.write("규정 근거:", row["policy_evidence"])
    st.write("보완 요청 초안:", row["draft_message"])
    st.write("검수상태:", row["review_status"]) #st.write() 화면에 보여주는것
    

    # ── 규정 근거가 안 붙은 건 = 사람이 직접 확인해야 하는 목록 ──
    missing_policy = df[df["policy_evidence"] == "관련 규정 확인 필요"]  # 함수 반환값과 글자를 정확히 맞춰야 걸러짐
    missing_types = missing_policy["risk_type"].dropna().unique()
    # dropna() : 비어있는 값 제외 / unique() : 중복 제거
    st.subheader("규정 근거 확인 필요")
    st.write("확인 필요 유형:", list(missing_types))
    st.dataframe(
        missing_policy[["employee", "category", "amount", "risk_type", "policy_evidence"]]
    )






