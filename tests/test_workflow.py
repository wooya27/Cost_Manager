"""
LangGraph(agent_workflow) 전체 위험 처리 검증 — 외부 호출은 모두 Mock.

검증 목표 (11.08 B03·B04 / 10.17 Day4):
- 비용 1건에 위험 2개가 있을 때, 각 위험이 서로 다른 규정/상태를 유지하며 processed_risks[]에 보존된다.
- 한 위험만 근거가 없어도 다른 위험의 검색·초안 생성은 계속된다.
- 근거 없는 위험은 LLM을 호출하지 않고 draft_source='needs_review'가 된다.
- DB 저장은 processed_risks 전체를 '한 번만' 저장한다.
"""

from unittest.mock import patch

from src.agent_workflow import workflow


# 합성 입력: 식대 35000 + 영수증 없음 → 위험 2개(식대한도 초과, 영수증누락)
BASE_EXPENSE = {
    "employee": "테스트직원",
    "department": "개발팀",
    "category": "식대",
    "amount": 35000,
    "date": "2026-11-06",
    "vendor": "가상식당",
    "reason": "점심 식사",
    "has_receipt": "N",
}


def _fake_find_similar_policies(risk_reason, top_k=3):
    """식대 관련 위험에만 규정이 있고, 영수증 위험은 근거 없음([])으로 둔다."""
    if "식대" in risk_reason:
        return [(1, "식대는 1인 20,000원 한도.", "policy.txt", 0.95)]
    return []  # 영수증누락 → 근거 없음


def test_graph_keeps_two_risks_separate():
    with patch("src.agent_workflow.find_similar_policies",
               side_effect=_fake_find_similar_policies), \
         patch("src.agent_workflow.make_llm_draft",
               return_value=("초안: 한도 초과 사유 확인 요청", "llm")) as m_llm, \
         patch("src.agent_workflow.save_audit_result",
               return_value=999) as m_save:

        result = workflow.invoke({"expense": BASE_EXPENSE})

    processed = result["processed_risks"]

    # 1) 위험 2개가 각각 개별 항목으로 보존
    assert len(processed) == 2
    types = {r["risk_type"] for r in processed}
    assert types == {"식대한도 초과", "영수증누락"}

    by_type = {r["risk_type"]: r for r in processed}

    # 2) 식대 위험: 근거 있음 → LLM 초안
    meal = by_type["식대한도 초과"]
    assert meal["policy_evidence"]  # 비어있지 않음
    assert meal["draft_source"] == "llm"

    # 3) 영수증 위험: 근거 없음 → needs_review (서로 다른 상태 유지)
    receipt = by_type["영수증누락"]
    assert receipt["policy_evidence"] == ""
    assert receipt["draft_source"] == "needs_review"

    # 4) LLM은 근거 있는 위험(1건)에만 호출됨
    assert m_llm.call_count == 1

    # 5) DB 저장은 '한 번', processed_risks 전체(2건)를 넘김
    assert m_save.call_count == 1
    saved_risks = m_save.call_args.kwargs["risks"]
    assert len(saved_risks) == 2


def test_graph_no_risk_skips_to_save():
    """위험이 없으면 retrieve/generate 없이 save로 가고, 빈 risks를 저장한다."""
    normal = dict(BASE_EXPENSE, amount=10000, has_receipt="Y")  # 위험 없음

    with patch("src.agent_workflow.find_similar_policies") as m_find, \
         patch("src.agent_workflow.make_llm_draft") as m_llm, \
         patch("src.agent_workflow.save_audit_result",
               return_value=1000) as m_save:

        result = workflow.invoke({"expense": normal})

    assert result.get("risks") == []
    m_find.assert_not_called()   # 규정 검색 안 함
    m_llm.assert_not_called()    # LLM 안 함
    assert m_save.call_count == 1
    assert m_save.call_args.kwargs["risks"] == []
