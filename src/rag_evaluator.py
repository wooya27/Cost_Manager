#기존 6개 규정 / 50개 평가 기록 보존
import pandas as pd

from src.policy_retriever import (
    find_keyword_policies,
    find_similar_policies,
)

with open(
    "policy.txt",
    "r",
    encoding="utf-8"
) as f:
    policy_txt = f.read()

policy_messages = policy_txt.split("\n\n")

eval_df = pd.read_csv("rag_eval_set.csv")

keyword_hits = 0
vector_hits = 0


for _, row in eval_df.iterrows():

    query = row["query"]
    expected_policy = row["expected_policy"]

    keyword_results = find_keyword_policies(
        query,
        policy_messages,
        top_k=3
    )

    vector_results = find_similar_policies(
        query,
        top_k=3
    )

    keyword_hit = any(
        expected_policy in policy
        for policy in keyword_results
    )

    vector_hit = any(
        expected_policy in policy[1]
        for policy in vector_results
    )

    if keyword_hit:
        keyword_hits += 1

    if vector_hit:
        vector_hits += 1


total = len(eval_df)

keyword_hit_at_3 = keyword_hits / total * 100
vector_hit_at_3 = vector_hits / total * 100


print(
    f"Keyword Hit@3 = "
    f"{keyword_hits} / {total} = "
    f"{keyword_hit_at_3:.1f}%"
)

print(
    f"Vector Hit@3 = "
    f"{vector_hits} / {total} = "
    f"{vector_hit_at_3:.1f}%"
)