

from fastapi import FastAPI # FastAPI라는 도구를 갖고온다
from pydantic import BaseModel #들어오는ㄴ 데이터의 규격을 정의하고 검사하기 위한 BaseModel을 갖고온다
import pandas as pd # → 비용 한 건을 DataFrame으로 만들기 #pandas를 가져오고,앞으로 pd fkrh qnfmrpTek
from src.audit_rules import detect_risks #→ 네가 기존에 만든 위험 탐지 함수 가져오기
from src.policy_retriever import find_policy_evidence, policy_messages #규정 검색 함수와 검색할 규정 문단 목록
from src.draft_generator import make_draft #보완요청 초안 생성 함수
from src.llm_generator import make_llm_draft
from src.database import save_audit_result, get_audit_results, create_tables
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("▶ create_tables() 실행 시작")
    create_tables()
    print("✅ create_tables() 실행 완료")
    yield

app = FastAPI(lifespan=lifespan) # app이라는 변수에 FastAPI 서버하나를 만든다

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

class BatchAuditRequest(BaseModel):
    expenses: list[ExpenseRequest]

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
    df = pd.DataFrame([expense_dict])

    # 3. audit_rules.py의 위험 탐지 함수 실행
    df = detect_risks(df)

    # 4. 검사된 DataFrame의 첫 번째 행
    result = df.iloc[0]

    # 5. Block4에서 만든 여러 위험 가져오기
    risks = result["risks"]

    # 위험이 하나도 없는 경우
    if not risks:
        processed_risks = []

    else:
        processed_risks = []

    for risk in risks:
        risk_type = risk["risk_type"]
        risk_reason = risk["risk_reason"]

        # Block 8 - 규정 찾기
        policy_evidence = find_policy_evidence(
            risk_type,
            policy_messages
        )

        processed_risk = risk.copy()
        processed_risk["policy_evidence"] = policy_evidence

            # Block 9 - LLM 초안 만들기
        result_for_draft = result.copy()
        result_for_draft["risk_type"] = risk_type
        result_for_draft["risk_reason"] = risk_reason

        try:
            draft_message, draft_source = make_llm_draft(
                result_for_draft,
                policy_evidence
            )

        except Exception:
            draft_message, draft_source = make_draft(
                result_for_draft
            )

        processed_risk["draft_message"] = draft_message
        processed_risk["draft_source"] = draft_source

        processed_risks.append(processed_risk)

        for item in processed_risks:
            print("위험:", item["risk_type"])
            print("규정:", item["policy_evidence"])
            print("초안:", item["draft_message"])
            print("출처:", item["draft_source"])
            print("-----")
        # 보완 요청 초안 생성
        try:
            draft_message, draft_source = make_llm_draft(
                result_for_draft,
                policy_evidence
            )

        except Exception:
            draft_message, draft_source = make_draft(
                result_for_draft
            )

    
    # 6. PostgreSQL 저장  DB저장
    audit_id = save_audit_result(
        employee=result["employee"],
        department=result["department"],
        category=result["category"],
        amount=int(result["amount"]),
        risks=risks,
        risk_type=risk_type,
        risk_reason=risk_reason,
        policy_evidence=policy_evidence,
        draft_message=draft_message,
        draft_source=draft_source
    )


    # 7. API 결과 반환
    return {
        "id": audit_id,
        "employee": result["employee"],
        "category": result["category"],
        "amount": int(result["amount"]),
        "risks": risks,
        "risk_type": risk_type,
        "risk_reason": risk_reason,
        "policy_evidence": policy_evidence,
        "draft_message": draft_message,
        "draft_source": draft_source
    }

@app.post("/audit/batch")
def audit_expenses_batch(batch: BatchAuditRequest):

    # 1. 여러 비용을 dict로 변환
    expense_dicts = []

    for expense in batch.expenses:
        expense_dicts.append(expense.model_dump())

    # 2. 여러 비용 → DataFrame 여러 행
    df = pd.DataFrame(expense_dicts)

    # 3. 여러 행을 한 번에 위험 검사
    df = detect_risks(df)

    # 4. 검사 결과 모으기
    results = []

    for _, row in df.iterrows():
        results.append({
            "employee": row["employee"],
            "department": row["department"],
            "category": row["category"],
            "amount": int(row["amount"]),
            "date": row["date"],
            "vendor": row["vendor"],
            "reason": None if pd.isna(row["reason"]) else row["reason"],
            "has_receipt": row["has_receipt"],
            "risks": row["risks"]
        })

    # 5. 결과 반환
    return {
        "count": len(results),
        "results": results
    }
    

@app.get("/audit-results") #저장된 검사 결과를 조회해라
def read_audit_results():
    rows = get_audit_results()

    return {
        "results": rows
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

