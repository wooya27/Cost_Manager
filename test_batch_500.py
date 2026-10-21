import pandas as pd
import requests
from collections import Counter


# 1. CSV 500건 읽기
df = pd.read_csv("sample_expenses_500.csv")


# 2. /audit/batch가 필요한 컬럼만 선택
columns = [
    "employee",
    "department",
    "category",
    "amount",
    "date",
    "vendor",
    "reason",
    "has_receipt"
]

df = df[columns]


# 3. 비어 있는 값 정리
df["vendor"] = df["vendor"].fillna("")

df["reason"] = (
    df["reason"]
    .astype(object)
    .where(df["reason"].notna(), None)
)


# 4. DataFrame 500행 → dict 500개
expenses = df.to_dict(orient="records")


# 5. BatchAuditRequest 형식으로 감싸기
payload = {
    "expenses": expenses
}


# 6. /audit/batch에 POST 요청
response = requests.post(
    "http://127.0.0.1:8000/audit/batch",
    json=payload
)


# 7. 결과 확인
print("HTTP 상태:", response.status_code)

data = response.json()

print("검사된 건수:", data["count"])


# 위험 종류별 개수 확인
risk_types = []

for result in data["results"]:
    for risk in result["risks"]:
        risk_types.append(risk["risk_type"])

print("위험 종류별 개수:")
print(Counter(risk_types))