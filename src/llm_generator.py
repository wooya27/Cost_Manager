
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()


def make_llm_draft(row, policy_evidence):

    employee = row["employee"]
    amount = row["amount"]
    category = row["category"]
    risk_type = row["risk_type"]
    risk_reason = row.get("risk_reason")

    prompt = f"""
당신은 회사 비용정산 검수 담당자를 돕는 AI입니다.

다음 비용 신청을 검토하고,
직원에게 전달할 짧고 정중한 보완 요청 문장을 작성하세요.

신청자: {employee}
금액: {amount}
카테고리: {category}
위험 유형: {risk_type}
위험 사유: {risk_reason}

관련 사내 규정:
{policy_evidence}

규정에 근거해서 보완이 필요한 내용을 명확하게 작성하세요.
"""

    response = client.responses.create(
        model="Gemini API",
        input=prompt
    )

    return response.output_text, "llm"