# 오늘 할 일 (9/17) — DAY1 마무리 (Day10 블록4 → Day11)

> 기준 로드맵: **`AuditFlow_AI_Day9-14_2일_마무리플랜.md`**
> 9/16까지: Day9 초안 + Day10 상세화면 완료. `review_status` 컬럼은 만들어만 둠(화면 표시 X).
> 순서대로 위에서부터. 지금 집중은 👉 1개만. **세션 사이 10분 휴식.**

---

## 블록 3 — 완료 아래로 이동 ✅
> 새 코드 X. 이미 만든 기능을 Agent 관점으로 이름 붙이기
- [ ] 4개 Agent 역할 매핑: 위험탐지→AuditRule / 규정검색→PolicySearch / 초안→DraftMessage / 검수→ReviewSupport
- 끝나면 보여야 할 결과: "왜 역할을 이렇게 나눴는가"를 30초 말로 설명 가능

---

## 오늘 목표선
- **최소선:** 블록1 = 검수 상태 화면 표시 → 오늘 성공 (= DAY1 필수 마무리)
- **목표:** 블록1~2 = Dashboard까지
- **욕심선:** 블록3 = Agent 역할 정리 = **DAY1 완성 → 내일 DAY2(Day12~14)**

## 오늘 배우는 개념
- Human-in-the-loop (`review_status` 표시)
- `st.selectbox` / `st.radio`로 상태 선택
- `st.metric` / `value_counts()` / `st.bar_chart`
- Agent 역할 분리 사고

## 막혔을 때 최소선
- 상태 선택 UI가 막히면 → 그냥 `st.write("검수 상태:", row["review_status"])` 표시만.
- Dashboard 차트가 막히면 → 숫자 카드 3개만.
- 15분 넘게 막히면 → 질문하기.

---

## 내일 (DAY2 · Day12~14)
- Day12: CSV 다운로드(`to_csv`+`st.download_button`) + 입력 검증(필수 컬럼)
- Day13: `agent_workflow.py` State/Node + 위험 1건 workflow 실행 (막히면 함수형)
- Day14: `logs/llm_calls.jsonl` 로컬 로그 + README + 전체 점검

---
## 완료
- [x] (9/17) Day 11 블록3 — Agent 역할 정리(말로). 4단계 매핑: 위험탐지→AuditRule / 규정검색→PolicySearch / 초안→DraftMessage / 사람검수→ReviewSupport. 왜 나눴나=한 군데씩 관리·수정·교체 쉬우려고 / 왜 사람검수=AI가 틀릴 수 있어 최종은 사람(Human-in-the-loop). **DAY1 완성**
- [x] (9/17) Day 11 블록2 — Dashboard 숫자 카드 3개(`st.metric`: 전체 건수/위험 건수/총액). `st.columns(3)`로 나란히 배치, 총액은 `f"{total_amount}원"`. 배운 것: metric=숫자 1개 카드(≠ dataframe 표), 숫자+글자는 f-string으로 합침. (차트는 욕심선 → 보류)
- [x] (9/17) Day 10 블록4 — 검수 상태(`review_status`)를 상세 화면에 표시. 핵심 배움: **코드는 위→아래 실행, 변수는 "태어난 줄보다 아래"에서만 사용 가능**(안 그러면 NameError). `row` 쓰는 줄들과 같은 무리로 이동해 해결
- [x] (9/16) Day 10 블록3 — 위험 건 상세 화면. `st.selectbox`로 위험 건 선택 → `.loc`로 행 전체 → 신청자/금액/카테고리/위험유형/사유/근거/초안 표시
- [x] (9/15) Day 9 블록2 — `make_draft`가 `draft_message`+`draft_source` 2개 리턴(언패킹) + `df.iterrows()` for문으로 두 컬럼 생성
- [x] (9/14) Day 9 블록1 — `make_draft(row)` 템플릿 초안 (값 꺼내기 → if-elif-else 유형별 분기 → f-string → return)
- [x] (9/13) Day 8 완성 — 검수용 요약 표 + "규정 근거 확인 필요" 목록
- [x] (9/11) Day 7 완성 — 위험유형→키워드→규정 chunk 검색 + 실패 기본값
- [x] (9/8) Day 6 — policy.txt 규정 문서 + 문단 분리
- [x] (9/6) Day 5 완성 — 7종 위험 탐지
- [x] (8/18) Day 3~4 — 위험 컬럼 + 규칙 함수 분리
- [x] (8/15) Day 1~2 — Streamlit 화면 + CSV 업로드 + 데이터 요약
