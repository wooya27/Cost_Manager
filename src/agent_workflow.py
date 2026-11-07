from typing_extensions import TypedDict
import pandas as pd
import uuid
import time
from langgraph.graph import StateGraph, START, END
from src.audit_rules import detect_risks
from src.policy_retriever import find_similar_policies
from src.draft_generator import make_draft
from src.observability import (log_workflow,log_node) 
from src.llm_generator import make_llm_draft
from src.database import save_audit_result




class AuditState(TypedDict, total=False):
    expense: dict
    risks: list
    policy_evidence: str
    draft_message: str
    draft_source: str
    review_status: str
    error: str
    run_id: str
    audit_id: int
    retry_count: int
    processed_risks: list[dict]
# state = 현재 작업정보를 들고다니는 가방
# node = workflow 에서 자기 한가지 일만 하는 함수 
# node 함수 3개 만든것
    # 위험 확인 담당자 만들기 
    # 규정 검색 담당자 만들기 
    # 초안 작성 담당자 만들기 
    
def audit_node(state: AuditState):
    start_time = time.perf_counter()

    expense = state["expense"]

    df = pd.DataFrame(
        [expense]
    )

    df = detect_risks(df)

    result = df.iloc[0]

    risks = result["risks"]

    latency_ms = (
    time.perf_counter() - start_time
    ) * 1000

    log_node(
        state,
        "audit",
        latency_ms
    )

    return {
        "risks": risks
    }


def retrieve_node(state: AuditState):

    start_time = time.perf_counter()
    try:
        risks = state.get(
            "risks",
            []
        )

        if not risks:
            return {
                "processed_risks": []
            }

        # 위험마다 '따로' 규정을 검색해 processed_risks[]에 누적한다.
        # (여러 위험을 policy_evidence 문자열 하나로 뭉치면 안 된다)
        processed_risks = []

        for risk in risks:

            similar_policies = find_similar_policies(
                risk["risk_reason"],
                top_k=3
            )

            if similar_policies:
                policy_evidence = "\n\n".join(
                    policy[1]
                    for policy in similar_policies
                )
            else:
                policy_evidence = ""

            processed_risks.append({
                "risk_type": risk["risk_type"],
                "risk_reason": risk["risk_reason"],
                "policy_evidence": policy_evidence
            })

        return {
            "processed_risks": processed_risks
        }

    finally:
        latency_ms = (
                    time.perf_counter() - start_time
                ) * 1000
        log_node(
            state,
            "retrieve",
            latency_ms
        )


def generate_node(state: AuditState):
    start_time = time.perf_counter()

    try:
        expense = state["expense"]

        processed_risks = state.get(
            "processed_risks",
            []
        )

        if not processed_risks:
            return {
                "error": "위험 정보 없음"
            }

        for risk in processed_risks:

            policy_evidence = risk.get("policy_evidence")

            if (
                not policy_evidence
                or policy_evidence == "관련 규정 확인 필요"
            ):
                risk["draft_message"] = None
                risk["draft_source"] = "needs_review"
                continue

            result_for_draft = expense.copy()

            result_for_draft["risk_type"] = risk["risk_type"]
            result_for_draft["risk_reason"] = risk["risk_reason"]

            try:
                draft_message, draft_source = make_llm_draft(
                    result_for_draft,
                    policy_evidence
                )

            except Exception:
                draft_message, draft_source = make_draft(
                    result_for_draft
                )

            risk["draft_message"] = draft_message
            risk["draft_source"] = draft_source

        return {
            "processed_risks": processed_risks,
            "error": ""
        }

    finally:
        latency_ms = (
            time.perf_counter() - start_time
        ) * 1000

        log_node(
            state,
            "generate",
            latency_ms
        )




def retry_node(state: AuditState):
    start_time = time.perf_counter()
    try:
        expense = state["expense"]

        risks = state.get(
            "risks",
            []
        )

        policy_evidence = state.get(
            "policy_evidence",
            ""
        )
        retry_count = state.get(
            "retry_count",
            0
        )

        retry_count += 1

        if not risks:
            return {
                "error": "위험 정보 없음"
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
                "error": "",
                "retry_count": retry_count
            }

        except Exception as e:
            return {
                "error": str(e),
                "retry_count": retry_count
            }
    finally:
        latency_ms = (
            time.perf_counter() - start_time
        ) * 1000
        log_node(
            state,
            "retry",
            latency_ms
        )

    
def review_gate_node(state: AuditState):
    start_time = time.perf_counter()
    try:
        # API 상태값(unreviewed/approved/need_revision/rejected)과 통일
        return {
            "review_status": "unreviewed"
        }
    finally:
        latency_ms = (
            time.perf_counter() - start_time
        ) * 1000
        log_node(
            state,
            "review",
            latency_ms
        )

def fallback_node(state: AuditState):
    start_time = time.perf_counter()
    try:
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
    finally:
        latency_ms = (
            time.perf_counter() - start_time
        ) * 1000
        log_node(
            state,
            "fallback",
            latency_ms
        )


def run_workflow(state: AuditState):

    state["run_id"] = str(
        uuid.uuid4()
    )

    result = workflow.invoke(
        state
    )

    log_workflow(
        result
    )

    return result


def save_node(state: AuditState):
    start_time = time.perf_counter()
    try:
        expense = state["expense"]

        processed_risks = state.get("processed_risks",[])

        if processed_risks:

            primary_risk = processed_risks[0]

            risk_type = primary_risk["risk_type"]
            risk_reason = primary_risk["risk_reason"]

            policy_evidence = primary_risk.get("policy_evidence")
            draft_message = primary_risk.get("draft_message")
            draft_source = primary_risk.get("draft_source")

        else:

            risk_type = None
            risk_reason = None
            policy_evidence = None
            draft_message = None
            draft_source = None

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
    finally:
        latency_ms = (
            time.perf_counter() - start_time
        ) * 1000
        log_node(
            state,
            "save",
            latency_ms
        )

def route_after_audit(state: AuditState):

    risks = state.get(
        "risks",
        []
    )

    if risks:
        return "retrieve"

    return "save"

def route_after_generate(state: AuditState):

    error = state.get(
        "error",
        ""
    )

    if error:
        return "retry"

    return "review"

def route_after_retry(state: AuditState):

    error = state.get(
        "error",
        ""
    )

    if error:
        return "fallback"

    return "review"

def route_after_retrieve(state: AuditState):

    processed_risks = state.get(
        "processed_risks",
        []
    )

    if processed_risks:
        return "generate"

    return "review"


graph = StateGraph(
    AuditState
)

graph.add_node(
    "audit",
    audit_node
)

graph.add_node(
    "retrieve",
    retrieve_node
)

graph.add_node(
    "generate",
    generate_node
)
graph.add_node(
    "retry",
    retry_node
)
graph.add_node(
    "fallback",
    fallback_node
)

graph.add_node(
    "review",
    review_gate_node
)

graph.add_node(
    "save",
    save_node
)


graph.add_edge(
    START,
    "audit"
)



graph.add_conditional_edges(
    "audit",
    route_after_audit,
    {
        "retrieve": "retrieve",
        "save": "save"
    }
)
graph.add_conditional_edges(
    "retrieve",
    route_after_retrieve,
    {
        "generate": "generate",
        "review": "review"
    }
)
graph.add_conditional_edges(
    "generate",
    route_after_generate,
    {
        "retry": "retry",
        "review": "review"
    }
)


graph.add_conditional_edges(
    "retry",
    route_after_retry,
    {
        "fallback": "fallback",
        "review": "review"
    }
)

graph.add_edge("fallback", "review")   # fallback 방 → review 방
graph.add_edge("review", "save")       # review 방 → save 방
graph.add_edge("save", END)            # save 방 → END(그래프 끝)


workflow = graph.compile()



if __name__ == "__main__":

    test_state = {
    "expense": {
        "employee": "김민수",
        "department": "개발팀",
        "category": "식대",
        "amount": 50000,
        "date": "2026-10-28",
        "vendor": "테스트식당",
        "reason": None,
        "has_receipt": "N"
    }
}
    result = run_workflow(
        test_state
    )

    print(
        "최종 State:",result
    )