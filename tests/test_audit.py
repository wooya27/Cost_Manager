import pandas as pd

from src.audit_rules import detect_risks

from fastapi.testclient import TestClient

from src.policy_retriever import find_similar_policies
from src.agent_workflow import fallback_node
from api.main import app
from src.database import save_audit_result, get_audit_results, update_review_status
from unittest.mock import patch

client = TestClient(app)


def test_normal_expense():
    df = pd.DataFrame([
        {
            "employee": "김민수",
            "date": "2026-10-31",
            "amount": 10000,
            "vendor": "테스트식당",
            "category": "식대",
            "reason": "점심 식사",
            "has_receipt": "Y"
        }
    ])

    result = detect_risks(df)

    risks = result.iloc[0]["risks"]

    assert risks == []


def test_meal_limit_exceeded():
    df = pd.DataFrame([
        {
            "employee": "김민수",
            "date": "2026-10-31",
            "amount": 50000,
            "vendor": "테스트식당",
            "category": "식대",
            "reason": "점심 식사",
            "has_receipt": "Y"
        }
    ])

    result = detect_risks(df)

    risks = result.iloc[0]["risks"]

    risk_types = [
        risk["risk_type"]
        for risk in risks
    ]

    assert "식대한도 초과" in risk_types

def test_missing_receipt():
    df = pd.DataFrame([
        {
            "employee": "김민수",
            "date": "2026-10-31",
            "amount": 10000,
            "vendor": "테스트식당",
            "category": "식대",
            "reason": "점심 식사",
            "has_receipt": "N"
        }
    ])

    result = detect_risks(df)

    risks = result.iloc[0]["risks"]

    risk_types = [
        risk["risk_type"]
        for risk in risks
    ]

    assert "영수증누락" in risk_types


def test_invalid_request_returns_422():
    response = client.post(
        "/audit",
        json={
            "employee": "김민수"
        }
    )

    assert response.status_code == 422

def test_vector_search_top3():
    results = find_similar_policies(
        "영수증이 첨부되지 않았습니다.",
        top_k=3
    )

    assert len(results) == 3    

def test_llm_fallback():
    state = {
        "expense": {
            "employee": "김민수",
            "department": "개발팀",
            "category": "식대",
            "amount": 50000,
            "date": "2026-10-31",
            "vendor": "테스트식당",
            "reason": "점심 식사",
            "has_receipt": "N"
        },
        "risks": [
            {
                "risk_type": "영수증누락",
                "risk_reason": "영수증 없음"
            }
        ]
    }

    result = fallback_node(state)

    assert result["draft_source"] == "template"

def test_database_save_and_read():
    audit_id = save_audit_result(
        employee="pytest테스트",
        department="개발팀",
        category="식대",
        amount=10000,
        risks=[],
        risk_type=None,
        risk_reason=None,
        policy_evidence="",
        draft_message="",
        draft_source=""
    )

    rows = get_audit_results()

    saved_row = next(
        row
        for row in rows
        if row[0] == audit_id
    )

    assert saved_row[1] == "pytest테스트"
    assert saved_row[4] == 10000


def test_review_status_update():
    audit_id = save_audit_result(
        employee="review테스트",
        department="개발팀",
        category="식대",
        amount=10000,
        risks=[],
        risk_type=None,
        risk_reason=None,
        policy_evidence="",
        draft_message="",
        draft_source=""
    )

    update_review_status(
        audit_id,
        "approved",
        "테스트 승인"
    )

    rows = get_audit_results()

    saved_row = next(
        row
        for row in rows
        if row[0] == audit_id
    )

    assert saved_row[11] == "approved"
    assert saved_row[12] == "테스트 승인"

def test_batch_audit():
    response = client.post(
        "/audit/batch",
        json={
            "expenses": [
                {
                    "employee": "김민수",
                    "department": "개발팀",
                    "category": "식대",
                    "amount": 10000,
                    "date": "2026-10-31",
                    "vendor": "테스트식당",
                    "reason": "점심 식사",
                    "has_receipt": "Y"
                },
                {
                    "employee": "김민수",
                    "department": "개발팀",
                    "category": "식대",
                    "amount": 10000,
                    "date": "2026-10-31",
                    "vendor": "테스트식당",
                    "reason": "점심 식사",
                    "has_receipt": "Y"
                }
            ]
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 2

    first_risk_types = [
        risk["risk_type"]
        for risk in data["results"][0]["risks"]
    ]

    second_risk_types = [
        risk["risk_type"]
        for risk in data["results"][1]["risks"]
    ]

    assert "중복 신청 의심" in first_risk_types
    assert "중복 신청 의심" in second_risk_types       

def test_no_policy_evidence_skips_llm():
    with patch(
        "api.main.find_similar_policies",
        return_value=[]
    ):
        with patch(
            "api.main.make_llm_draft"
        ) as mock_llm:
            with patch(
                "api.main.save_audit_result",
                return_value=999
            ):
                response = client.post(
                    "/audit",
                    json={
                        "employee": "김민수",
                        "department": "개발팀",
                        "category": "식대",
                        "amount": 50000,
                        "date": "2026-10-31",
                        "vendor": "테스트식당",
                        "reason": "점심 식사",
                        "has_receipt": "Y"
                    }
                )

    assert response.status_code == 200

    data = response.json()

    assert data["draft_source"] == "needs_review"

    mock_llm.assert_not_called()