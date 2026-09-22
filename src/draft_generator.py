# 보완 요청 문장을 만든다
import streamlit as st
import pandas as pd
from src.audit_rules import detect_risks
# DraftMessageAgent
def make_draft(row):  # 그함수 안에서 붙인이름
    employee = row["employee"]
    amount = row["amount"]
    category = row["category"]
    risk_type = row["risk_type"]


    if risk_type == "영수증누락":
        request = "영수증을 첨부해 주세요."

    elif risk_type == "택시비 사유 부족":
        request = "택시 이용 사유를 작성해 주세요."

    elif risk_type == "중복 신청 의심":
        request = "중복 신청 여부를 확인해 주세요."

    else:
        request = "해당 지출 건을 확인해 주세요."

    
    draft_source = "template" #이 초안은 어디에서 만들어졌는가?w
    draft_message = (
        f"{employee}님, "
        f"{amount:,}원 {category} 지출 건에 대해 확인이 필요합니다. "
        f"{request}"
    )
    return draft_message, draft_source
    
    