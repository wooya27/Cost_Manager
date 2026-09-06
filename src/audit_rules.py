# 위험을 찾는다

def detect_risks(df):

    no_receipt = df[df["has_receipt"]=="N"]

    df.loc[df["has_receipt"]=="N","risk_type"]="영수증누락"
    df.loc[df["has_receipt"]=="N","risk_reason"]="영수증 없음" #별도 데이터 변수를 만든 게 아니기 때문


    
    mask = df.duplicated(subset=["employee", "date", "amount","vendor"],keep= False)

    df.loc[mask, "risk_type"] = "중복 신청 의심"
    df.loc[mask, "risk_reason"] = "동일 직원/날짜/금액/사용처 중복"
   

    df["category_mean"] = df.groupby("category")["amount"].transform("mean")

    abnormal_mask = df["amount"] >= df["category_mean"] * 2

    df.loc[abnormal_mask, "risk_type"] = "이상 비용 후보"
    df.loc[abnormal_mask, "risk_reason"] = "카테고리 평균의 2배 이상"


    df.loc[(df["category"]=="식대") &(df["amount"]>20000), "risk_type"]="식대한도 초과"    
    df.loc[(df["category"]== "교통") & (df["amount"]>15000),"risk_type"] = "야근 식대 한도초과"
    df.loc[(df["category"]== "교통") & (df["amount"]>30000) & (df["reason"].isna()),"risk_type"] = "택시비 사유 부족"

    df.loc[(df["category"]== "소모품") & (df["amount"]>2000) & (df["amount"]<50000),"risk_type"] = "사무용품 추가 승인"
    return df

 