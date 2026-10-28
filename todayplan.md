# 오늘 할 일 (10/28 · DAY 3 — LangGraph + 장애복구 + Logging, Block 25~30 남음)

> 기준 로드맵: **`.claude/plans/10.17 계획 v5일분할.md`** DAY 3 (Block 21~30)
> Block 21~24는 됐다(노드 함수 7개 다 정의됨: audit/retrieve/generate/review_gate/fallback/save + AuditState).
> **아직 안 된 것:** 노드들을 `StateGraph`로 **실제로 연결**(조건분기·compile)하는 게 없다. 지금은 함수만 있고 그래프가 안 엮임.
> **지금 집중할 건 👉 표시된 1개뿐.** 나머지는 그거 끝나고 보면 돼.
> 세션 사이 10분 휴식. 에러 15분 넘게 막히면 질문.
>
> **DAY 3 끝나면 보여야 할 최종 결과:** 정상/위험/근거없음/LLM실패/DB실패 5가지 경로가 LangGraph에서 실제로 다르게 흐르고, run_id로 묶인 JSONL 로그가 남는다.

---
## 블록 25 (30분) — Conditional Edge: 그래프 조립 · 🧠 직접 작성  👉 지금 이거
- [ ] `StateGraph(AuditState)` 만들고 노드 7개 `add_node`
- [ ] 분기1: risks[] 없음 → save
- [ ] 분기2: risks[] 있음 → retrieve
- [ ] 분기3: 근거 없음 → review_gate
- [ ] `.compile()` 해서 app 만들기
- 끝나면 보여야 할 결과: **정상 건과 위험 건을 넣었을 때 실제로 경로가 달라진다** (출력/로그로 확인)

## 블록 26 (30분) — LLM 성공/실패 분기 · 🧠 직접 작성
- [ ] generate 성공 → review_gate
- [ ] generate 실패 → retry → fallback → review_gate
- [ ] 강제로 실패시켜 fallback 경로 확인
- 끝나면 보여야 할 결과: 일부러 LLM 실패시켰을 때 fallback으로 복구되는 로그

## 블록 27 (30분) — Timeout + Retry · 🧠 직접 작성
- [ ] timeout 값 명시
- [ ] Retry 1~2회 + 재시도 횟수 로그
- [ ] 최종 실패 시 template fallback
- 끝나면 보여야 할 결과: 무한대기 X / 무한재시도 X / 최종 복구 경로 O

## 블록 28 (30분) — run_id + JSONL Logging · 🧠 직접 작성
- [ ] run_id, expense_id, node, started_at, latency_ms, success
- [ ] error_type, error_message, retrieval_count, llm_success, fallback_used
- 끝나면 보여야 할 결과: 한 요청의 Node 기록을 run_id로 묶어 추적 가능

## 블록 29 (30분) — 장애 테스트 3종 · 🧠 직접 작성
- [ ] RAG 검색 0건 / LLM timeout / DB 저장 실패 일부러 발생
- [ ] 각각 "어디서·왜 실패 / 무엇으로 복구 / 로그 어디" 답하기
- 끝나면 보여야 할 결과: 3종 장애가 각각 복구되고 로그로 설명됨

## 블록 30 (30분) — DAY3 통합검증 + Workflow 설명 + PR · 🔧 세팅
- [ ] 정상/위험/근거없음/LLM실패/DB실패 5경로 통과
- [ ] Mermaid/텍스트 Workflow 메모
- [ ] commit / push / PR
- 끝나면 보여야 할 결과: LangGraph 실사용 + 조건분기 + Retry/Fallback + run_id 로깅 체크 완료

---
## 완료
- [x] (DAY 3) B21 LangGraph 설치/현재 workflow 비교
- [x] (DAY 3) B22 AuditState 정의 (`src/agent_workflow.py:10`)
- [x] (DAY 3) B23 audit_node + retrieve_node (`src/agent_workflow.py:26,45`)
- [x] (DAY 3) B24 generate/fallback/review_gate/save Node (`src/agent_workflow.py:81~`)
- [x] (DAY 2 전체) pgVector RAG + Keyword/Vector Hit@3 평가 비교
- [x] (DAY 1 전체) Backend/DB/Review 흐름 종료
