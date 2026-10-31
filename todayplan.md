# 오늘 할 일 (10/30 · DAY 3 마무리 — 장애 테스트 + 통합검증)

> 기준 로드맵: **`.claude/plans/10.17 계획 v5일분할.md`** DAY 3 (Block 21~30)
> 그래프 조립·분기·retry·fallback·latency 로깅까지 **다 됐고 로그로 확인됨.** (block 25~27 완료, 28은 latency만)
> **지금 집중할 건 👉 표시된 1개뿐.** 나머지는 그거 끝나고 보면 돼.
> 세션 사이 10분 휴식. 에러 15분 넘게 막히면 질문.
>
> **DAY 3 끝나면 보여야 할 최종 결과:** 정상/위험/근거없음/LLM실패/DB실패 5가지 경로가 LangGraph에서 실제로 다르게 흐르고, run_id로 묶인 JSONL 로그가 남는다.

---
## 블록 29 (30분) — 장애 테스트 3종 · 🧠 직접 작성  👉 지금 이거
- [ ] 장애①: RAG 검색 0건 일부러 발생 → 복구 경로 확인
- [ ] 장애②: LLM 실패/timeout → retry→fallback 복구 확인
- [ ] 장애③: DB 저장 실패 일부러 발생 → 어떻게 되는지 확인
- [ ] 각각 "어디서·왜 실패 / 무엇으로 복구 / 로그 어디" 한 줄씩 답하기
- 끝나면 보여야 할 결과: 3종 장애가 각각 복구되거나 안전하게 처리되고 로그로 설명됨

## 블록 30 (30분) — DAY3 통합검증 + Workflow 설명 + PR · 🔧 세팅
- [ ] 정상/위험/근거없음/LLM실패/DB실패 5경로 통과 확인
- [ ] Mermaid/텍스트 Workflow 메모
- [ ] commit / push / PR
- 끝나면 보여야 할 결과: LangGraph 실사용 + 조건분기 + Retry/Fallback + run_id 로깅 체크 완료

---
## 보류 (나중에)
- [ ] **블록 28 나머지** — node_calls 로그 필드 확장: 공통(success/error_type/error_message) + 노드별(retrieval_count·llm_success·fallback_used). 설계 A안(success=크래시 여부). `log_node`에 `**extra` 받는 것부터.

---
## 완료
- [x] (10/30) 블록 28 일부 — 7개 노드 전부 `try/finally`로 latency_ms 로깅
- [x] (DAY 3) 블록 25 그래프 조립 + 조건분기 + compile (로그로 경로 분기 확인)
- [x] (DAY 3) 블록 26 LLM 성공/실패 분기 (fallback 경로 로그 확인)
- [x] (DAY 3) 블록 27 retry 노드 + retry_count
- [x] (DAY 3) B21~24 LangGraph 설치 / AuditState / 노드 함수 7개 정의
- [x] (DAY 2 전체) pgVector RAG + Keyword/Vector Hit@3 평가 비교
- [x] (DAY 1 전체) Backend/DB/Review 흐름 종료
