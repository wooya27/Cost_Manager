from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd

from src.audit_rules import detect_risks
from src.policy_retriever import find_similar_policies
from src.draft_generator import make_draft
from src.llm_generator import make_llm_draft
from src.agent_workflow import run_workflow

from src.database import (
    save_audit_result,
    get_audit_results,
    create_tables,
    update_review_status,
)

from contextlib import asynccontextmanager


# =========================================================
# 서버 시작 시 DB 테이블 준비
# =========================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("▶ create_tables() 실행 시작")

    try:
        create_tables()

    except Exception as e:
        print(
            "❌ create_tables() 실패:",
            repr(e)
        )

        raise

    print("✅ create_tables() 실행 완료")

    yield

app = FastAPI(lifespan=lifespan)


# =========================================================
# Request 데이터 형식
# =========================================================

# 비용 1건의 입력 형식
class ExpenseRequest(BaseModel):
    employee: str
    department: str
    category: str
    amount: int
    date: str
    vendor: str
    reason: str | None = None
    has_receipt: str


# 여러 비용을 한 번에 받을 때의 입력 형식
class BatchAuditRequest(BaseModel):
    expenses: list[ExpenseRequest]


# Human Review 상태 변경용 입력 형식
class ReviewRequest(BaseModel):
    review_status: str
    review_note: str | None = None


# 사람이 변경할 수 있는 검수 상태
ALLOWED_REVIEW_STATUSES = {
    "unreviewed",
    "approved",
    "need_revision",
    "rejected",
}


@app.get("/")
def root():
    return {
        "status": "running"
    }

@app.post("/audit")
def audit_expense(expense: ExpenseRequest):

    # 1. 요청 데이터를 dict로 변환
    expense_dict = expense.model_dump()

    # 2. LangGraph 실행
    result = run_workflow({
        "expense": expense_dict
    })

    # 3. LangGraph에서 처리한 위험 목록
    processed_risks = result.get(
        "processed_risks",
        []
    )

    # 4. 기존 API 호환용 대표 위험
    primary_risk = (
        processed_risks[0]
        if processed_risks
        else {}
    )

    # 5. 기존과 같은 JSON 응답 반환
    return {
        "id": result["audit_id"],
        "employee": expense_dict["employee"],
        "category": expense_dict["category"],
        "amount": expense_dict["amount"],
        "risks": processed_risks,
        "risk_type": primary_risk.get("risk_type"),
        "risk_reason": primary_risk.get("risk_reason"),
        "policy_evidence": primary_risk.get("policy_evidence"),
        "draft_message": primary_risk.get("draft_message"),
        "draft_source": primary_risk.get("draft_source")
    }


# =========================================================
# POST /audit/batch
# 여러 비용을 한 번에 위험 검사
# =========================================================

@app.post("/audit/batch")
def audit_expenses_batch(batch: BatchAuditRequest):

    # 1. 여러 ExpenseRequest → 여러 dict

    expense_dicts = []

    for expense in batch.expenses:
        expense_dicts.append(
            expense.model_dump()
        )


    # 2. 여러 비용 → DataFrame 여러 행

    df = pd.DataFrame(expense_dicts)


    # 3. 여러 행을 한 번에 위험 검사
    #
    # 중복 신청 / 카테고리 평균 비교처럼
    # 여러 행이 있어야 가능한 검사를 여기서 수행

    df = detect_risks(df)


    # 4. 결과 모으기

    results = []

    for _, row in df.iterrows():

        results.append({
            "employee": row["employee"],
            "department": row["department"],
            "category": row["category"],
            "amount": int(row["amount"]),
            "date": row["date"],
            "vendor": row["vendor"],

            # pandas NaN → JSON null 변환
            "reason": (
                None
                if pd.isna(row["reason"])
                else row["reason"]
            ),

            "has_receipt": row["has_receipt"],
            "risks": row["risks"]
        })


    # 5. 결과 반환

    return {
        "count": len(results),
        "results": results
    }


# =========================================================
# GET /audit-results
# PostgreSQL에 저장된 감사 결과 조회
# =========================================================

@app.get("/audit-results")
def read_audit_results():

    rows = get_audit_results()

    return {
        "results": rows
    }


# =========================================================
# PATCH /audit-results/{id}/review
# Block 8 — Human Review
# =========================================================

@app.patch("/audit-results/{audit_id}/review")
def review_audit_result(
    audit_id: int,
    review: ReviewRequest
):

    # 1. 허용된 상태인지 검사

    if review.review_status not in ALLOWED_REVIEW_STATUSES:

        raise HTTPException(
            status_code=400,
            detail=(
                "review_status는 "
                "unreviewed, approved, "
                "need_revision, rejected 중 하나여야 합니다."
            )
        )


    # 2. PostgreSQL review_status UPDATE

    row = update_review_status(
        audit_id,
        review.review_status,
        review.review_note
)


    # 3. 해당 id가 DB에 없는 경우

    if row is None:

        raise HTTPException(
            status_code=404,
            detail="Audit result not found"
        )


    # 4. 변경 결과 반환

    return {
        "id": audit_id,
        "review_status": review.review_status,
        "review_note": review.review_note
    }

# =========================================================
# AuditFlow 현재 전체 흐름
# =========================================================

# 비용 JSON 입력
# ↓
# ExpenseRequest / Pydantic 검증
# ↓
# dict
# ↓
# DataFrame
# ↓
# detect_risks()
# ↓
# risks[]
# ↓
# for risk in risks
# ↓
# 각 위험별 find_policy_evidence()
# ↓
# 규정 근거 있음?
#
# ├─ YES
# │   ↓
# │   make_llm_draft()
# │   ↓
# │   실패 시 make_draft() Template Fallback
# │
# └─ NO
#     ↓
#     LLM 호출 금지
#     ↓
#     draft_source = needs_review
#
# ↓
# processed_risks[]
# ↓
# PostgreSQL risks JSONB 저장
# ↓
# GET /audit-results
# ↓
# 사람이 결과 확인
# ↓
# PATCH /audit-results/{id}/review
# ↓
# approved / need_revision / rejected
# ↓
# PostgreSQL review_status 변경