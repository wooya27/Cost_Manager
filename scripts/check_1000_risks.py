import pandas as pd

from src.audit_rules import detect_risks


# 1. 1,000건 데이터 읽기
df = pd.read_csv(
    "sample_expenses_1000.csv"
)


# 2. 위험 탐지
result_df = detect_risks(
    df.copy()
)


# 3. 전체 위험 개수
total_risks = sum(
    len(risks)
    for risks in result_df["risks"]
)


# 4. 위험이 하나 이상 있는 비용 건수
risk_rows = result_df[
    result_df["risks"].apply(
        lambda risks: len(risks) > 0
    )
]


# 5. 위험 타입별 개수 세기
risk_types = []

for risks in result_df["risks"]:
    for risk in risks:
        risk_types.append(
            risk["risk_type"]
        )


risk_counts = (
    pd.Series(risk_types)
    .value_counts()
)


# 6. 결과 출력
print(
    "전체 비용 건수:",
    len(result_df)
)

print(
    "위험이 있는 비용 건수:",
    len(risk_rows)
)

print(
    "전체 탐지 위험 개수:",
    total_risks
)

print(
    "\n=== 위험 유형별 개수 ==="
)

print(
    risk_counts
)


print(
    "\n=== 위험 유형별 실제 사례 확인 ==="
)

risk_names = [
    "영수증누락",
    "식대한도 초과",
    "이상 비용 후보",
    "교통비 한도 초과",
    "사무용품 추가 승인",
    "택시비 사유 부족",
    "중복 신청 의심"
]

for risk_name in risk_names:

    matched_rows = result_df[
        result_df["risks"].apply(
            lambda risks: any(
                risk["risk_type"] == risk_name
                for risk in risks
            )
        )
    ]

    if len(matched_rows) > 0:

        row = matched_rows.iloc[0]

        print(
            "\n위험 유형:",
            risk_name
        )

        print(
            "employee:",
            row["employee"]
        )

        print(
            "category:",
            row["category"]
        )

        print(
            "amount:",
            row["amount"]
        )

        print(
            "reason:",
            row["reason"]
        )

        print(
            "has_receipt:",
            row["has_receipt"]
        )

        print(
            "risks:",
            row["risks"]
        )