from typing_extensions import TypedDict
import pandas as pd

from src.audit_rules import detect_risks
from src.policy_retriever import find_similar_policies
from src.draft_generator import make_draft
from src.observability import log_workflow
from src.llm_generator import make_llm_draft

class AuditState(TypedDict, total=False):
    expense: dict
    risks: list
    policy_evidence: str
    draft_message: str
    draft_source: str
    review_status: str
    error: str
    run_id: str
# state = 현재 작업정보를 들고다니는 가방
# node = workflow 에서 자기 한가지 일만 하는 함수 
# node 함수 3개 만든것
    # 위험 확인 담당자 만들기 
    # 규정 검색 담당자 만들기 
    # 초안 작성 담당자 만들기 
    
def audit_node(state: AuditState):

    expense = state["expense"]

    df = pd.DataFrame(
        [expense]
    )

    df = detect_risks(df)

    result = df.iloc[0]

    risks = result["risks"]

    return {
        "risks": risks
    }


def retrieve_node(state: AuditState):

    risks = state.get(
        "risks",
        []
    )

    if not risks:
        return {
            "policy_evidence": ""
        }

    risk = risks[0]

    risk_reason = risk["risk_reason"]

    similar_policies = find_similar_policies(
        risk_reason,
        top_k=3
    )

    if not similar_policies:
        return {
            "policy_evidence": ""
        }

    policy_evidence = "\n\n".join(
        policy[1]
        for policy in similar_policies
    )

    return {
        "policy_evidence": policy_evidence
    }


def generate_node(state: AuditState):

    expense = state["expense"]

    risks = state.get(
        "risks",
        []
    )

    policy_evidence = state.get(
        "policy_evidence",
        ""
    )

    if not risks:
        return {
            "error": "위험 정보 없음"
        }

    if not policy_evidence:
        return {
            "error": "규정 근거 없음"
        }

    risk = risks[0]

    result_for_draft = expense.copy()

    result_for_draft["risk_type"] = risk["risk_type"]
    result_for_draft["risk_reason"] = risk["risk_reason"]

    try:

        draft_message, draft_source = make_llm_draft(
            result_for_draft,
            policy_evidence
        )

        return {
            "draft_message": draft_message,
            "draft_source": draft_source,
            "error": ""
        }

    except Exception as e:

        return {
            "error": str(e)
        }

def review_gate_node(state: AuditState):

    return {
        "review_status": "미검토"
    }

def fallback_node(state: AuditState):

    expense = state["expense"]

    risks = state.get(
        "risks",
        []
    )

    if not risks:
        return {
            "draft_message": "위험 정보를 확인해주세요.",
            "draft_source": "needs_review"
        }

    risk = risks[0]

    result_for_draft = expense.copy()

    result_for_draft["risk_type"] = risk["risk_type"]
    result_for_draft["risk_reason"] = risk["risk_reason"]

    draft_message, draft_source = make_draft(
        result_for_draft
    )

    return {
        "draft_message": draft_message,
        "draft_source": draft_source
    }


# 1. 위험 확인 Node
    # 정확히 말하면 아무것도 안 하는 게 아니라, 받은 state를 그대로 다음 단계로 넘기는 통과(pass-through) Node야.
    # 위험 정보가 이미 들어왔는지 확인하는 자리인데, 지금은 앞 단계에서 risk_type, risk_reason이 이미 만들어져 있으니까 그대로 넘긴다.”
def check_risk_node(state):
    return state

# 2. 규정 확인 Node
def policy_search_node(state): #현재 작업 정보를 state로 받아서 규정 검색을 담당하는 작업 단계를 만든다.
    risk_type = state["risk_type"]

    evidence = find_policy_evidence( 
        risk_type,
        policy_messages
    )

    state["policy_evidence"] = evidence #찾은 규정 근거를 State의 policy_evidence 칸에 써 넣는다.
    
    return state

# 3. 초안 생성 Node
def draft_message_node(state):  #초안생성을 node가 일했으니까, 일한결과를 state에도 기록해줘야 다음단계를 쓸수있다
    message, source = make_draft(state)
    # state가 함수 안으로 들어가는 순간, 함수 내부에서는 그걸 row라는 이름으로 부르게 돼.
    # state라는 표/가방 안에 "draft_message"라는 칸을 만들고, 오른쪽 message 안에 들어 있는 값을 그 칸에 넣어라.
    # 오른쪽 message 안에 들어 있는 값을 그 칸에 넣어라.

    state["draft_message"] = message # node 안에 잠깐 존재하는 임시변수
    state["draft_source"] = source

    return state

# state를 위험 확인 Node에 넣고 
# 그 결과 state를 규정 검색 Node에 넣고 
# 그 결과를 다시 초안 생성 Node에 넣는다.
def run_workflow(state): # node들을 연결하는 함수
    state = check_risk_node(state)
    state = policy_search_node(state)
    state = draft_message_node(state)

    log_workflow(state) #현재 결과를 파일에 기록
    return state


if __name__ == "__main__":

    test_state = {
        "employee": "김민수",
        "amount": 50000,
        "category": "식대",
        "risk_type": "영수증누락",
        "risk_reason": "영수증 없음"
    }

    result = run_workflow(test_state)

    print("규정 근거:", result["policy_evidence"])
    print("보완 요청 초안:", result["draft_message"])
    print("초안 출처:", result["draft_source"])


    def save_node(state: AuditState):

    expense = state["expense"]

    risks = state.get(
        "risks",
        []
    )

    policy_evidence = state.get(
        "policy_evidence",
        ""
    )

    draft_message = state.get(
        "draft_message",
        ""
    )

    draft_source = state.get(
        "draft_source",
        ""
    )

    if risks:

        risk = risks[0]

        risk_type = risk["risk_type"]
        risk_reason = risk["risk_reason"]

        processed_risk = risk.copy()

        processed_risk["policy_evidence"] = policy_evidence
        processed_risk["draft_message"] = draft_message
        processed_risk["draft_source"] = draft_source

        processed_risks = [
            processed_risk
        ]

    else:

        risk_type = None
        risk_reason = None
        processed_risks = []

    audit_id = save_audit_result(
        employee=expense["employee"],
        department=expense["department"],
        category=expense["category"],
        amount=int(expense["amount"]),
        risks=processed_risks,
        risk_type=risk_type,
        risk_reason=risk_reason,
        policy_evidence=policy_evidence,
        draft_message=draft_message,
        draft_source=draft_source
    )

    return {
        "audit_id": audit_id
    }