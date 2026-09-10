# 관련 규정을 찾는다

import streamlit as st
import pandas as pd
from src.audit_rules import detect_risks

with open("policy.txt","r",encoding="utf-8")as f:  #열기
    #"r":읽고 | encoding="utf-8": 한글이 깨지지않게 | as f : 지금 열린 파일 이름을 잠깐 f라고 부를게

    policy_txt = f.read() #읽기
    chunks = policy_txt.split("\n\n") #자르기
    st.write("조각 개수:",len(chunks))  
for chunk in chunks:
    #st.write(chunk)
    print(chunk)

RISK_KEYWORDS = {
    "식대한도 초과" : "식대",
    "택시비 사유 부족" : "택시비",
    "영수증누락" : "영수증",
    "중복 신청 의심" : "중복"
}



def find_policy_evidence(risk_type): # 함수를 사용할때 값을 받아오는 입력칸
    # risk_type과 chunks는 이 함수를 만들면서 처음 등장해도 돼.
    keyword =RISK_KEYWORDS.get(risk_type)
    for chunk in chunks:
        if keyword in chunk:
            return chunk      # 찾았으면 그 문단
# 돌려주고 끝
