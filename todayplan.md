# 오늘 할 일 (9/22 화) — DAY2 시작 (Day12~14)

> 기준 로드맵: **`AuditFlow_AI_Day9-14_2일_마무리플랜.md`** DAY2
> DAY1(Day9~11) 완성됨: 초안 생성 → 사람 검수 화면 → Dashboard.
> 오늘 블록은 다 적어뒀다. 순서대로 위에서부터. **지금 집중은 👉 1개만.** 나머지는 그거 끝나고 보면 돼.
> **세션 사이 10분 휴식.** 에러는 15분 넘게 막히면 나한테 질문.

---

## 블록 5 (30~35분) — Day14 로컬 로그(JSONL) · 🧠 직접 작성  👉 지금 이거
- [ ] `src/observability.py` + `logs/` 폴더
- [ ] 로그 함수 (timestamp, risk_type, draft_source, fallback_used 등)
- [ ] 성공/실패/fallback 기록
- 끝나면 보여야 할 결과: `logs/llm_calls.jsonl`에 로그 최소 1줄 존재

## 블록 6 (40~60분) — Day14 README + 전체 점검 · 🔧 문서/세팅
- [ ] README 최소 구조 채우기 (소개/문제/흐름/기능/기술스택/Agent구조/실행법/한계)
- [ ] 전체 앱 한 번 처음부터 돌려보며 점검
- 끝나면 보여야 할 결과: GitHub에서 처음 보는 사람도 이해할 수 있는 상태

---

## 오늘 목표선
- **최소선:** 블록1 = CSV 다운로드 → 오늘 성공 (업무 산출물 확보)
- **목표:** 블록1~4 = 다운로드 + 검증 + Workflow 1건
- **욕심선:** 블록5~6 = 로그 + README = **DAY2 완성 → 프로젝트 MVP 완성**

## 시간 부족 시 무조건 완료 (마무리플랜 기준)
CSV 다운로드 → workflow 1건 → 로컬 로그 → README. (줄여도 됨: LLM 실제 연결, 실제 LangGraph, 실제 Langfuse, 차트)

---
## 완료
- [x] (9/22) 블록4 — Day13 위험 1건 workflow 실행. `run_workflow(state)`로 node 3개 `state=노드(state)` 체이닝 → 최종 state에 policy_evidence+draft_message 나옴 (`python -m src.agent_workflow`로 확인)
- [x] (9/22) 블록3 — Day13 State+Node. State=결과 쌓는 가방(dict), Node=일 하나씩 하는 함수. node 3개(check_risk/policy_search/draft_message) + state 입출력 구조
- [x] (9/22) 블록2 — Day12 입력 검증. 필수 컬럼 목록 → 리스트 컴프리헨션으로 빠진 컬럼만 모으기 → `st.error` + `st.stop()`으로 앱 안 죽게
- [x] (9/22) 블록1 — Day12 검수 결과 CSV 다운로드. `df.to_csv(index=False)` → `st.download_button`(data/file_name/mime)
- [x] (9/17) **DAY1 완성** — Day11 블록3 Agent 역할 정리(말로). 위험탐지→AuditRule / 규정검색→PolicySearch / 초안→DraftMessage / 사람검수→ReviewSupport
- [x] (9/17) Day 11 블록2 — Dashboard 숫자 카드 3개(`st.metric`: 전체/위험/총액), `st.columns(3)` 배치
- [x] (9/17) Day 10 블록4 — 검수 상태(`review_status`) 상세 화면 표시. 배움: 변수는 태어난 줄보다 아래에서만 사용 가능(NameError)
- [x] (9/16) Day 10 블록3 — 위험 건 상세 화면. `st.selectbox` → `.loc`로 행 전체 표시
- [x] (9/15) Day 9 블록2 — `make_draft`가 draft_message+draft_source 2개 리턴(언패킹) + `df.iterrows()`
- [x] (9/14) Day 9 블록1 — `make_draft(row)` 템플릿 초안 (값 꺼내기 → if-elif-else → f-string → return)
- [x] (9/13) Day 8 완성 — 검수용 요약 표 + "규정 근거 확인 필요" 목록
- [x] (9/11) Day 7 완성 — 위험유형→키워드→규정 chunk 검색 + 실패 기본값
- [x] (9/8) Day 6 — policy.txt 규정 문서 + 문단 분리
- [x] (9/6) Day 5 완성 — 7종 위험 탐지
- [x] (8/18) Day 3~4 — 위험 컬럼 + 규칙 함수 분리
- [x] (8/15) Day 1~2 — Streamlit 화면 + CSV 업로드 + 데이터 요약
