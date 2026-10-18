# 위험을 찾는다

def detect_risks(df):

    # 각 비용 행마다 위험들을 담을 빈 리스트를 만든다.
    df["risks"] = [[] for _ in range(len(df))]

    # 조건에 해당하는 행에 위험 하나를 추가하는 함수
    def add_risk(mask, risk_type, risk_reason):
        for idx in df[mask].index:
            df.at[idx, "risks"].append({
                "risk_type": risk_type,
                "risk_reason": risk_reason
            })

    # 1. 영수증 누락
    mask = df["has_receipt"] == "N"
    add_risk(
        mask,
        "영수증누락",
        "영수증 없음"
    )

    # 2. 중복 신청
    duplicate_mask = df.duplicated(
        subset=["employee", "date", "amount", "vendor"],
        keep=False
    )

    add_risk(
        duplicate_mask,
        "중복 신청 의심",
        "동일 직원/날짜/금액/사용처 중복"
    )

    # 3. 카테고리 평균 계산
    df["category_mean"] = (
        df.groupby("category")["amount"]
        .transform("mean")
    )

    abnormal_mask = (
        df["amount"] >= df["category_mean"] * 2
    )

    add_risk(
        abnormal_mask,
        "이상 비용 후보",
        "카테고리 평균의 2배 이상"
    )

    # 4. 식대 한도 초과
    meal_mask = (
        (df["category"] == "식대")
        & (df["amount"] > 20000)
    )

    add_risk(
        meal_mask,
        "식대한도 초과",
        "식대 20,000원 초과"
    )

    # 5. 교통비 규칙
    transport_mask = (
        (df["category"] == "교통")
        & (df["amount"] > 15000)
    )

    add_risk(
        transport_mask,
        "교통비 한도 초과",
        "교통 비용 15,000원 초과"
    )

    # 6. 택시비 사유 부족
    taxi_mask = (
        (df["category"] == "교통")
        & (df["amount"] > 30000)
        & (df["reason"].isna())
    )

    add_risk(
        taxi_mask,
        "택시비 사유 부족",
        "30,000원 초과 교통비에 사유 없음"
    )

    # 7. 사무용품 추가 승인
    supply_mask = (
        (df["category"] == "소모품")
        & (df["amount"] > 2000)
        & (df["amount"] < 50000)
    )

    add_risk(
        supply_mask,
        "사무용품 추가 승인",
        "사무용품 추가 승인 대상"
    )

    return df

 