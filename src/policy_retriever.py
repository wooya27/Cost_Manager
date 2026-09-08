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