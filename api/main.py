

from fastapi import FastAPI # FastAPI라는 도구를 갖고온다
from pydantic import BaseModel #들어오는ㄴ 데이터의 규격을 정의하고 검사하기 위한 BaseModel을 갖고온다
import pandas as pd # → 비용 한 건을 DataFrame으로 만들기 #pandas를 가져오고,앞으로 pd fkrh qnfmrpTek
from src.audit_rules import detect_risks #→ 네가 기존에 만든 위험 탐지 함수 가져오기
from src.policy_retriever import find_policy_evidence, policy_messages #규정 검색 함수와 검색할 규정 문단 목록
from src.draft_generator import make_draft #보완요청 초안 생성 함수
from src.llm_generator import make_llm_draft
app = FastAPI() # app이라는 변수에 FastAPI 서버하나를 만든다

# AuditFlow가 받을 비용 데이터의 양식을 만든다.
class ExpenseRequest(BaseModel): # 컬럼양식
    employee: str
    department: str
    category: str
    amount: int
    date: str
    vendor: str
    reason: str | None = None # reason은 글자일 수도 있고, 비어 있을 수도 있다.
    has_receipt: str

# 누군가 서버의 / 주소를 조회하면 root()를 실행해서 "running"이라는 결과를 돌려준다
@app.get("/")
def root():
    return{"status": "running"}



@app.post("/audit") # 누군가 /audit 주소로 POST 요청을 보내면 아래 함수를 실행해라.
                    # 들어온 비용 데이터를 expense라는 이름으로 받아라.+ 단, 데이터 형식은 ExpenseRequest 규칙을 따라야 한다.
                    #expense라는 데이터를 받을 건데, ExpenseRequest 형식이어야 해.
def audit_expense(expense: ExpenseRequest): # 현재함수는 아무처리도 아직안함. 입력->받고=확인->다시 보냄


    # 1. Pydantic 객체 → 일반 Python 딕셔너리
    expense_dict = expense.model_dump()

    # 2. 딕셔너리 데이터 1건 → DataFrame 1행
    df = pd.DataFrame([expense_dict]) #이 딕셔너리 1개를 표의 1행으로 넣어라”

    # 3. 기존 위험 탐지 함수에 전달
    df = detect_risks(df)

    # 4. 검사된 DataFrame의 첫 번째 행 꺼내기
    result = df.iloc[0]

    # 5. 위험탐지 다음에 규정 검색 추가
    risk_type = result.get("risk_type")

    if pd.isna(risk_type):
        policy_evidence = None
    else:
        policy_evidence = find_policy_evidence(
            risk_type,
            policy_messages
        )

    # 6.보완요청 초안 생성 함수    
    if pd.isna(risk_type):
        draft_message = None
        draft_source = None
    else:
        draft_message, draft_source = make_draft(result)
    # 7. API 결과로 돌려주기
    # 검사가 끝난 result에서 필요한 값만 골라서 API 응답용 JSON으로 만드는 부분
    # “검사 결과에서 직원명, 카테고리, 금액, 위험유형, 위험사유를 꺼내서 사용자에게 돌려줘.”
    return {
        "employee": result["employee"], #result의 employee
        "category": result["category"], #result의 category
        "amount": int(result["amount"]), # result 의 amount
        "risk_type": None if pd.isna(result.get("risk_type")) else result.get("risk_type"),
        "risk_reason": None if pd.isna(result.get("risk_reason")) else result.get("risk_reason"),
        "policy_evidence": policy_evidence,
        "draft_message": draft_message,
        "draft_source": draft_source

    }




# JSON
# ↓
# Pydantic 검사
# ↓
# expense
# ↓
# 딕셔너리
# ↓
# DataFrame 1행
# ↓
# detect_risks()
# ↓
# result = 검사 결과 한 행
# ↓
# return
# ↓
# FastAPI가 JSON 응답으로 변환

