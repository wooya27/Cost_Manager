from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd

from src.audit_rules import detect_risks
from src.policy_retriever import find_similar_policies
from src.draft_generator import make_draft
from src.llm_generator import make_llm_draft


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
    create_tables()
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

    # 1. Pydantic 객체 → Python dict

    expense_dict = expense.model_dump()


    # 2. 비용 1건 → DataFrame 1행

    df = pd.DataFrame([expense_dict])


    # 3. 위험 탐지

    df = detect_risks(df)


    # 4. 검사된 첫 번째 행 가져오기

    result = df.iloc[0]


    # 5. detect_risks()가 만든 여러 위험 가져오기

    risks = result["risks"]


    # 규정 검색 + 초안 생성까지 끝난
    # 최종 위험들을 저장할 리스트
    processed_risks = []


    # 6. 위험을 하나씩 처리

    for risk in risks:

        # 현재 처리 중인 위험
        risk_type = risk["risk_type"]
        risk_reason = risk["risk_reason"]


        # 6-1. 현재 위험에 맞는 규정 검색

        # 6-1. 현재 위험에 맞는 규정 Vector Search

        similar_policies = find_similar_policies(
            risk_reason,
            top_k=3
        )

        if similar_policies:
            policy_evidence = "\n\n".join(
                policy[1] for policy in similar_policies
            )
        else:
            policy_evidence = "관련 규정 확인 필요"

        processed_risk = risk.copy()
        processed_risk["policy_evidence"] = policy_evidence

        # 6-2. LLM / Template에 전달할 데이터 준비

        result_for_draft = result.copy()

        result_for_draft["risk_type"] = risk_type
        result_for_draft["risk_reason"] = risk_reason


        # 6-3. Block 7 안전장치
        #
        # 규정 근거 없음
        # → LLM 호출 금지
        # → 사람이 확인하도록 needs_review

        if (
            not policy_evidence
            or policy_evidence == "관련 규정 확인 필요"
        ):

            draft_message = None
            draft_source = "needs_review"


        # 규정 근거 있음
        # → LLM 초안 생성

        else:

            try:

                draft_message, draft_source = make_llm_draft(
                    result_for_draft,
                    policy_evidence
                )


            # LLM 실패
            # → Template Fallback
            except Exception:

                draft_message, draft_source = make_draft(
                    result_for_draft
                )


        # 6-4. 현재 위험에 후속 결과 붙이기

        processed_risk["draft_message"] = draft_message
        processed_risk["draft_source"] = draft_source


        # 최종 위험 리스트에 저장
        processed_risks.append(processed_risk)


    # =====================================================
    # 기존 단일 컬럼 호환 처리
    #
    # 현재 DB에는
    # risk_type / risk_reason / policy_evidence ...
    # 단일 컬럼도 존재하기 때문에
    # 첫 번째 위험을 대표값으로 사용한다.
    # =====================================================

    if processed_risks:

        primary_risk = processed_risks[0]

        risk_type = primary_risk["risk_type"]
        risk_reason = primary_risk["risk_reason"]
        policy_evidence = primary_risk["policy_evidence"]
        draft_message = primary_risk["draft_message"]
        draft_source = primary_risk["draft_source"]


    # 정상 건
    # → 위험 관련 값 없음
    else:

        risk_type = None
        risk_reason = None
        policy_evidence = None
        draft_message = None
        draft_source = None


    # 학습 / 디버깅용 출력

    for item in processed_risks:

        print("위험:", item["risk_type"])
        print("규정:", item["policy_evidence"])
        print("초안:", item["draft_message"])
        print("출처:", item["draft_source"])
        print("-----")


    # 7. PostgreSQL 저장
    #
    # 중요:
    # 원본 risks가 아니라
    # 규정/초안까지 붙은 processed_risks를 JSONB로 저장

    audit_id = save_audit_result(
        employee=result["employee"],
        department=result["department"],
        category=result["category"],
        amount=int(result["amount"]),

        risks=processed_risks,

        risk_type=risk_type,
        risk_reason=risk_reason,
        policy_evidence=policy_evidence,
        draft_message=draft_message,
        draft_source=draft_source
    )


    # 8. API 응답

    return {
        "id": audit_id,
        "employee": result["employee"],
        "category": result["category"],
        "amount": int(result["amount"]),

        # 위험별 규정/초안까지 포함된 최종 구조
        "risks": processed_risks,

        # 아래 단일 필드는 기존 구조 호환용 대표값
        "risk_type": risk_type,
        "risk_reason": risk_reason,
        "policy_evidence": policy_evidence,
        "draft_message": draft_message,
        "draft_source": draft_source
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