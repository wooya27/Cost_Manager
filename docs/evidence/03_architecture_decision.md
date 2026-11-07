# 03 · LangGraph ↔ /audit 실연결 여부 결정 (DAY1 B03~B05)

> 기록일: 2026-11-07 (KST) · 11.08 계획 B03~B05 + 10.17 Day4

## 결정: **B = 기존 `/audit`(api/main.py)를 데모 기준으로 고정. LangGraph는 '독립 구현, API 미연동'.**

### 왜 B인가
- `api/main.py`의 `POST /audit`는 이미 위험별 `processed_risks` 루프(규정검색→근거없음 needs_review / 있으면 LLM·실패 시 template)로 **완전 동작**하고 DB 저장·조회·검수까지 검증됨.
- Graph를 API에 끼워 넣다가 응답 계약(`id`, `risks[]`, 대표필드, `draft_source`)이 깨지면 데모 전체가 위험. 박람회(11/09) 전에는 **확실히 되는 경로**가 우선.
- 11.08 계획의 핵심 의사결정 규칙과 일치: *"미검증 Graph를 실행 경로처럼 묘사하지 않는다."*

## 이번 블록에서 고친 Graph 버그 (독립 구현으로서 올바르게 동작하도록)

`src/agent_workflow.py`

| # | 문제 (수정 전) | 수정 후 |
|---|---|---|
| 1 | `retrieve_node`가 `processed_risks`를 **안 만들고** `policy_evidence` 문자열 하나만 반환. 루프 안에서 `similar_policies`가 매 위험마다 덮어써져 **마지막 위험 것만** 남음 | 위험마다 따로 검색해 `processed_risks[]`(각 위험 + 그 위험의 `policy_evidence`)로 **누적** |
| 2 | 그 결과 `route_after_retrieve`가 항상 `review`로 가서 **`generate_node`(LLM 초안)가 실행조차 안 됨** → DB에 **빈 risks 저장** | `processed_risks`가 채워져 `generate`로 진입 → 위험별 초안 생성 후 저장 |
| 3 | `review_gate_node`가 `review_status="미검토"`(한글) → API 영문 상태값과 불일치 | `"unreviewed"`로 통일 |
| 4 | 미사용 레거시 스캐폴드 노드 3개(`check_risk_node`/`policy_search_node`/`draft_message_node`) 혼재 | 제거 (저장소 정리) |

## 완료 증거 (B03·B04)

`tests/test_workflow.py` — 외부 호출(규정검색/LLM/DB) 전부 Mock, 컴파일된 `workflow.invoke()` 실행:

```
tests/test_workflow.py::test_graph_keeps_two_risks_separate PASSED
tests/test_workflow.py::test_graph_no_risk_skips_to_save     PASSED
```

검증 내용:
- 위험 2개(식대한도 초과 / 영수증누락)가 **각각 다른 규정·상태**로 `processed_risks[]`에 보존.
- 영수증 위험은 근거 없음 → `draft_source="needs_review"` + **LLM 미호출**(`call_count==1`, 식대 위험만).
- `save_audit_result`는 **1회** 호출, `risks` 인자에 **2건 전체** 포함.
- 위험 없음 입력 → retrieve/generate 건너뛰고 save로, 빈 `risks` 저장(`find/llm` 미호출).

## 남은 것 (행사 이후)
- Graph를 `/audit`에 실제 연결(`run_workflow()` 호출로 교체)하고 응답 계약 동일 유지 — 10.17 Day4 완전 통합.
- `retry_node`/`fallback_node`는 현재 대표 위험 기준의 보조 경로. 전체 위험 단위 재시도는 추후.

## 30초 설명
> "모듈에 Graph 코드가 있다는 것과, 사용자가 호출하는 API에서 그 Graph가 실행된다는 것은 다르다.
> 지금 데모는 `/audit`(API 내부 루프)로 돌고, LangGraph는 같은 로직을 상태·분기·실패경로로 재구성한
> **독립 구현**이며 테스트로 검증했다. API 실연결은 계약을 깨지 않는 선에서 다음 단계로 둔다."

## 상태: 완료 (결정 B 확정 + Graph 독립 구현 버그 수정·테스트 통과)
