import json

import pandas as pd

from src.audit_rules import detect_risks


def test_1000_expense_regression():

    # 1. 테스트용 1,000건 읽기
    input_df = pd.read_csv(
        "sample_expenses_1000.csv"
    )


    # 2. 고정된 정답표 읽기
    expected_df = pd.read_csv(
        "tests/data/expected_risks_1000.csv"
    )


    # 3. 현재 위험 탐지 코드 실행
    result_df = detect_risks(
        input_df.copy()
    )


    # 4. expense_id → expected_risks 형태로 정리
    expected_map = {}

    for _, row in expected_df.iterrows():

        expected_map[row["expense_id"]] = (
            json.loads(
                row["expected_risks"]
            )
        )


    # 5. 틀린 결과를 모을 공간
    mismatches = []


    # 6. 1,000건 비교
    for _, row in result_df.iterrows():

        expense_id = row["expense_id"]

        actual_risks = [
            risk["risk_type"]
            for risk in row["risks"]
        ]

        expected_risks = expected_map[
            expense_id
        ]


        if actual_risks != expected_risks:

            mismatches.append({
                "expense_id": expense_id,
                "expected": expected_risks,
                "actual": actual_risks
            })


    # 7. 하나라도 달라졌으면 실패
    assert mismatches == [], (
        f"회귀 오류 {len(mismatches)}건 발생: "
        f"{mismatches[:10]}"
    )