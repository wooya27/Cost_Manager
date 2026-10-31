import json

import pandas as pd

from src.audit_rules import detect_risks


# 1. 고정된 1,000건 데이터 읽기
df = pd.read_csv(
    "sample_expenses_1000.csv"
)


# 2. 현재 검수된 위험 규칙 실행
result_df = detect_risks(
    df.copy()
)


# 3. 정답표 만들기
expected_rows = []

for _, row in result_df.iterrows():

    risk_types = [
        risk["risk_type"]
        for risk in row["risks"]
    ]

    expected_rows.append({
        "expense_id": row["expense_id"],
        "expected_risks": json.dumps(
            risk_types,
            ensure_ascii=False
        )
    })


# 4. DataFrame으로 변환
expected_df = pd.DataFrame(
    expected_rows
)


# 5. 정답 파일 저장
expected_df.to_csv(
    "tests/data/expected_risks_1000.csv",
    index=False,
    encoding="utf-8-sig"
)


print(
    "expected_risks 저장 건수:",
    len(expected_df)
)

print(
    "tests/data/expected_risks_1000.csv 생성 완료"
)