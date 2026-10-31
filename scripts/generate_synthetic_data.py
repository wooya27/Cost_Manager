import random
from datetime import datetime, timedelta

import pandas as pd


SEED = 42
random.seed(SEED)


# 1. 기존 500건 읽기
base_df = pd.read_csv(
    "sample_expenses_500.csv"
)


# 2. 새로 만들 500건을 담을 공간
new_rows = []


# 3. 기존 500건을 참고해서 새로운 500건 생성
for i in range(500):

    # 기존 데이터 중 한 행을 랜덤하게 선택
    original_row = base_df.sample(
        n=1,
        random_state=SEED + i
    ).iloc[0]

    new_row = original_row.copy()


    # 4. 새로운 expense_id 부여
    new_row["expense_id"] = (
        f"E{501 + i:03d}"
    )


    # 5. 금액을 조금씩 변경
    amount_change = random.uniform(
        0.8,
        1.2
    )

    new_amount = int(
        original_row["amount"]
        * amount_change
    )

    # 최소 500원 단위로 정리
    new_amount = max(
        500,
        round(new_amount / 500) * 500
    )

    new_row["amount"] = new_amount


    # 6. 날짜 새로 지정
    start_date = datetime(
        2026,
        8,
        1
    )

    random_days = random.randint(
        0,
        90
    )

    new_date = (
        start_date
        + timedelta(days=random_days)
    )

    new_row["date"] = (
        new_date.strftime("%Y-%m-%d")
    )


    new_rows.append(
        new_row
    )


# 7. 새 500건 → DataFrame
new_df = pd.DataFrame(
    new_rows
)


# 8. 기존 500건 + 새 500건
combined_df = pd.concat(
    [
        base_df,
        new_df
    ],
    ignore_index=True
)


# 9. 1,000건인지 확인
print(
    "기존 데이터:",
    len(base_df)
)

print(
    "추가 데이터:",
    len(new_df)
)

print(
    "최종 데이터:",
    len(combined_df)
)


# 10. 새로운 파일로 저장
combined_df.to_csv(
    "sample_expenses_1000.csv",
    index=False,
    encoding="utf-8-sig"
)

print(
    "sample_expenses_1000.csv 생성 완료"
)