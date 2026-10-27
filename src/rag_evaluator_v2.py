import pandas as pd

from src.policy_retriever import find_similar_policies


eval_df = pd.read_csv(
    "rag_eval_set_v2.csv"
)


hit_1 = 0
hit_3 = 0
hit_5 = 0


for index, row in eval_df.iterrows():

    query = row["query"]
    expected_policy = row["expected_policy"]

    vector_results = find_similar_policies(
        query,
        top_k=5
    )

    retrieved_policies = [
        policy[1]
        for policy in vector_results
    ]


    if any(
        expected_policy in policy
        for policy in retrieved_policies[:1]
    ):
        hit_1 += 1


    if any(
        expected_policy in policy
        for policy in retrieved_policies[:3]
    ):
        hit_3 += 1


    if any(
        expected_policy in policy
        for policy in retrieved_policies[:5]
    ):
        hit_5 += 1


    if (index + 1) % 50 == 0:
        print(
            "진행:",
            index + 1,
            "/",
            len(eval_df)
        )


total = len(eval_df)


hit_1_rate = hit_1 / total * 100
hit_3_rate = hit_3 / total * 100
hit_5_rate = hit_5 / total * 100


print()
print("=== Vector Search Evaluation ===")

print(
    f"Hit@1 = "
    f"{hit_1} / {total} = "
    f"{hit_1_rate:.1f}%"
)

print(
    f"Hit@3 = "
    f"{hit_3} / {total} = "
    f"{hit_3_rate:.1f}%"
)

print(
    f"Hit@5 = "
    f"{hit_5} / {total} = "
    f"{hit_5_rate:.1f}%"
)