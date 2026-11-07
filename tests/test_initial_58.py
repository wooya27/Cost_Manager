"""
초기 58건 진단 데이터로 '구조 수정'이 유지되는지 지키는 회귀 테스트.
(10.17 업무 규칙 검증 1단계 — 복수위험 보존 / 비교형 배치 탐지 / 복합위험 동시표현)
"""

import pandas as pd

from src.audit_rules import detect_risks

DATA = "tests/data/initial_58_cases.csv"


def _detect():
    df = pd.read_csv(DATA)
    return df, detect_risks(df.copy())


def test_58_cases_loaded():
    df, _ = _detect()
    assert len(df) == 58


def test_no_receipt_risk_is_not_lost():
    """has_receipt=N 건은 전부 '영수증누락'으로 보존된다 (복수위험 구조 효과)."""
    df, result = _detect()
    n_count = int((df["has_receipt"] == "N").sum())
    detected = sum(
        1
        for risks in result["risks"]
        for r in risks
        if r["risk_type"] == "영수증누락"
    )
    assert detected == n_count  # 소실 0


def test_comparison_rules_fire_in_batch():
    """중복/이상비용 같은 비교형 규칙이 배치 전체 처리에서 탐지된다 (단건 API면 0)."""
    _, result = _detect()
    types = [r["risk_type"] for risks in result["risks"] for r in risks]
    assert "중복 신청 의심" in types
    assert "이상 비용 후보" in types


def test_multiple_risks_coexist():
    """한 비용에 위험 2개 이상이 동시에 표현된다."""
    _, result = _detect()
    assert any(len(risks) >= 2 for risks in result["risks"])
