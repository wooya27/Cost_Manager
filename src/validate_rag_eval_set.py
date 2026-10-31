import pandas as pd


df = pd.read_csv(
    "rag_eval_set_v2.csv"
)


print("전체 데이터:", len(df))

print(
    "빈 query:",
    df["query"].isna().sum()
)

print(
    "중복 query:",
    df["query"].duplicated().sum()
)

print(
    "규정 개수:",
    df["expected_policy"].nunique()
)

print(
    "\n규정별 질문 개수:"
)

print(
    df["expected_policy"].value_counts()
)