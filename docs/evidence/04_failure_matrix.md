# 04 · 핵심 실패 처리 매트릭스 (DAY1 B07)

> 기록일: 2026-11-07 (KST) · 11.08 계획 B07 + 10.17 Day4 Block6

> **"검색 결과 없음"과 "DB 고장"은 다른 오류다.** 전자는 정상 업무 흐름(사람 검수로 넘김), 후자는 시스템 장애(거짓 성공 금지).

| # | 장애 상황 | 기대 동작 | 검증 테스트 | 경로 | 결과 |
|---|---|---|---|---|---|
| 1 | 규정 검색 결과 `[]` (근거 없음) | LLM **미호출**, `draft_source="needs_review"` | `test_no_policy_evidence_skips_llm` | API `/audit` | PASS |
| 1' | 〃 (그래프) | 해당 위험만 needs_review, 다른 위험은 계속 | `test_workflow.py::...two_risks_separate` | Graph | PASS |
| 2 | LLM 예외/Timeout (근거는 있음) | Template fallback (`draft_source="template"`) | `test_api_llm_failure_falls_back_to_template` | API `/audit` | PASS |
| 2' | 〃 (노드 단위) | `fallback_node` → template | `test_llm_fallback` | Graph node | PASS |
| 3 | DB 저장 예외 | **거짓 성공 id 반환 금지** → 500 | `test_api_db_save_failure_no_false_success` | API `/audit` | PASS |
| 4 | 잘못된 입력 (amount 문자열 등) | `422` | `test_invalid_request_returns_422` | API `/audit` | PASS |

## 실행 명령 / 결과

```
python -m pytest -m "not integration" -q
→ 13 passed, 3 deselected
```

## run_id 로깅 (관찰성)
- `src/observability.py`가 `run_id`를 node/workflow 로그(JSONL)에 묶어 기록(`log_node`, `log_workflow`).
- ⚠️ 로그의 `draft_message`에 실데이터가 섞이면 유출 위험 → **합성 데이터만 사용**, 민감정보 로깅은 개선 대상으로 표기.

## 30초 설명
> "검색 결과가 없다는 것은 '규정을 못 찾았으니 사람이 보라(needs_review)'는 **정상 업무 분기**이고,
> DB가 고장 난 것은 '저장 자체가 실패'한 **시스템 장애**다. 전자는 흐름을 계속 이어가고,
> 후자는 가짜 성공 id를 돌려주지 않고 500으로 실패를 드러낸다. 둘을 같은 오류로 묶으면 안 된다."

## 상태: 완료
