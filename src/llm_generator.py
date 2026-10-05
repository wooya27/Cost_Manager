import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)


def make_llm_draft(result, policy_evidence):

    employee = result["employee"]
    amount = result["amount"]
    category = result["category"]
    risk_type = result["risk_type"]
    risk_reason = result.get("risk_reason")

    prompt = f"""
너는 회사 비용정산 검수 담당자를 돕는 AI다.

다음 비용 신청과 관련 규정을 보고
직원에게 전달할 짧고 정중한 보완 요청 문장을 작성해라.

신청자: {employee}
금액: {amount}
카테고리: {category}
위험 유형: {risk_type}
위험 사유: {risk_reason}

관련 규정:
{policy_evidence}
"""

    response = client.chat.completions.create(
        model= "gemini-3.5-flash",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    draft_message = response.choices[0].message.content

    return draft_message, "llm"