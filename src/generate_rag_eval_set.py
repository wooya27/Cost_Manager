import os
import json
import pandas as pd
from dotenv import load_dotenv
from google import genai


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)



with open(
    "policy.txt",
    "r",
    encoding="utf-8"
) as f:
    policy_txt = f.read()


policy_messages = policy_txt.split("\n\n")

policies = []


for policy_message in policy_messages:

    lines = policy_message.strip().splitlines()

    if not lines:
        continue

    policy_name = lines[0].strip("[]")

    policy_text = "\n".join(
        lines[1:]
    )

    policies.append(
        {
            "policy_name": policy_name,
            "policy_text": policy_text
        }
    )


print("규정 개수:", len(policies))

for policy in policies[:5]:
    print(policy)

def generate_queries(
    policy_name,
    policy_text,
    count=3
):
    prompt = f"""
다음 회사 비용 규정에 해당하는
직원 질문을 {count}개 만들어주세요.

규정명:
{policy_name}

규정 내용:
{policy_text}

조건:
- 서로 다른 표현을 사용한다.
- 규정 문장을 그대로 복사하지 않는다.
- 실제 직원이 질문하거나 비용을 신청하는 상황처럼 작성한다.
- 정답은 반드시 이 규정이어야 한다.
- 다른 규정이 더 적절한 질문은 만들지 않는다.
- JSON 배열만 출력한다.

출력 예시:
[
  "질문 1",
  "질문 2",
  "질문 3"
]
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt
    )

    queries = json.loads(
    response.text
)

    queries = json.loads(
    response.text
)

    return queries[:count]

#=======================================
eval_rows = []


for policy in policies:

    queries = generate_queries(
        policy["policy_name"],
        policy["policy_text"],
        count=17
    )

    for query in queries:
        eval_rows.append(
            {
                "query": query,
                "expected_policy": policy["policy_name"]
            }
        )

    print(
        policy["policy_name"],
        "생성:",
        len(queries)
    )


eval_df = pd.DataFrame(
    eval_rows
)


eval_df.to_csv(
    "rag_eval_set_v2.csv",
    index=False,
    encoding="utf-8-sig"
)


print(
    "전체 평가 데이터:",
    len(eval_df)
)