# 오늘 할 일 (9/15) — DAY1 (Day9~11) · 마무리플랜

> 기준 로드맵: **`AuditFlow_AI_Day9-14_2일_마무리플랜.md`** (오늘=Day9~11, 내일=Day12~14)
> ✅ Day9 블록1(템플릿 `make_draft`)은 이미 완료 → 오늘은 **블록2(fallback)부터** 실제 시작.
> 순서대로 위에서부터. 지금 집중은 👉 1개만. **세션 사이 10분 휴식.**

---

## 블록 3 (40분) — Day10 검수 상태 (Human-in-the-loop) · 🧠 직접 작성  👉 다음 시작점
> AI가 최종 승인 X, 사람이 마지막 확인
- [ ] `review_status` 컬럼 추가 (기본값 `미검토`)
- [ ] 상세 화면에서 상태 표시 (가능하면 미검토/보완요청/승인 선택 UI)
- 끝나면 보여야 할 결과: 상세 화면에 "검수 상태: 미검토"가 보인다

## 블록 4 (50분) — Day11 Dashboard · 🧠 직접 작성
> 개별 건이 아니라 전체 현황 요약
- [ ] 전체 신청 건수 / 위험 건수 / 총 신청 금액 계산 → `st.metric` 카드 3개
- [ ] 위험 유형별 `value_counts()` → (가능하면) `st.bar_chart`
- 끝나면 보여야 할 결과: 숫자 카드 3개 (+ 차트 1개면 완성)

## 블록 5 (30분) — Day11 Agent 역할 정리 + 복습 · ✍️ 말로 설명
> 새 코드 X. 이미 만든 기능을 Agent 관점으로 이름 붙이기
- [ ] 4개 Agent 역할 매핑: 위험탐지→AuditRule / 규정검색→PolicySearch / 초안→DraftMessage / 검수→ReviewSupport
- 끝나면 보여야 할 결과: "왜 역할을 이렇게 나눴는가"를 30초 말로 설명 가능

---

## 오늘 목표선
- **최소선:** 블록1~2 = fallback + 상세화면 → 오늘 성공
- **목표:** 블록1~4 = 검수상태 + Dashboard까지
- **욕심선:** 블록5 = Agent 역할 정리 = **DAY1 완성**

## 오늘 배우는 개념
- fallback / `draft_source` 분기
- `st.selectbox` + 행 선택 → 상세 표시
- Human-in-the-loop (`review_status`)
- `st.metric` / `value_counts()` / `st.bar_chart`
- Agent 역할 분리 사고

## 막혔을 때 최소선
- LLM이 막히면 → 오늘은 템플릿 + `draft_source`만. LLM은 "줄여도 됨" 목록.
- Dashboard 차트가 막히면 → 숫자 카드 3개만.
- 15분 넘게 막히면 → 질문하기.

---

## 내일 (DAY2 · Day12~14) — 그날 옮겨 적음
- Day12: CSV 다운로드(`to_csv`+`st.download_button`) + 입력 검증(필수 컬럼)
- Day13: `agent_workflow.py` State/Node + 위험 1건 workflow 실행 (막히면 함수형)
- Day14: `logs/llm_calls.jsonl` 로컬 로그 + README + 전체 점검
- 이후: Day15 발표 스크립트 + 포트폴리오화

---
## 완료
- [x] (9/15) 복습 세션 — 오늘 개념 3개(값2개 리턴·언패킹 / `for _, row`의 `_` / `st.selectbox`+`.loc`) 재학습 후 study/_recap-inbox.md에 Q&A 저장. `_`="안 쓸 거라 버림" 한 줄 기억으로 마무리
- [x] (9/15) Day 10 블록1 — 위험 건 상세화면. `st.selectbox("...", risk_df.index)`로 위험 건 선택 → `risk_df.loc[selected]`로 그 행 전체 꺼내기 → `st.write`로 신청자/금액/카테고리/위험유형/사유/규정근거/초안 7개 표시. 배운 것: selectbox는 고른 값을 돌려줌, `.loc[번호]`는 그 행 전체, row["컬럼"]로 값 하나씩
- [x] (9/15) Day 9 블록2 — `make_draft`가 `draft_message`+`draft_source` 2개 리턴(언패킹) + app.py에서 `df.iterrows()` for문으로 두 컬럼 생성. 배운 것: 함수 값 2개 리턴/받기(`return a,b` / `x,y=f()`), `for _, row in df.iterrows()`(인덱스 버리고 행 전체), 컬럼 붙이기는 for 밖에서 한 번만. LLM 실연결은 보류(템플릿 항상 작동이 핵심)
- [x] (9/14) Day 9 블록1 — `make_draft(row)` 템플릿 초안 (값 꺼내기 → if-elif-else 유형별 분기 → f-string 조립 → return). else 덕에 매핑 안 된 유형도 문구 항상 생성. 배운 것: row(한 줄) vs df(표 전체), return은 계산 다 하고 맨 마지막
- [x] (9/13) Day 8 블록3 — 검수용 요약 표(위험유형/사유/규정근거) + "규정 근거 확인 필요" 목록 화면 표시 · **Day8 완성**
- [x] (9/13) Day 8 블록2 — 근거 안 붙는 3종 파악(전부 경우 A) + 사무용품·야근식대 매핑 보강(policy.txt 문단 + RISK_KEYWORDS). 이상 비용 후보는 의도적으로 "확인 필요" 유지(환각 방지)
- [x] (9/12) Day 8 블록1 — `policy_evidence` 컬럼 생성 (import 연결 + for문으로 각 행에 `find_policy_evidence` 실행)
- [x] (9/11) Day 7 블록3 — 실패 케이스 기본값 (`keyword` None + for 다 돌고 못 찾음 → "관련 규정 확인 필요") · **Day7 완성**
- [x] (9/10) Day 7 블록2 — `find_policy_evidence()` 검색 함수 (위험유형→키워드→chunk 반환)
- [x] (9/10) Day 7 블록1 — `RISK_KEYWORDS` dict (위험유형→규정 키워드 매핑, 규정 있는 4종만)
- [x] (9/8) Day 6 블록1 — `policy.txt` 규정 문서 작성 (영수증/식대/택시/중복 4문단)
- [x] (9/8) Day 6 블록2~3 — policy.txt 읽기 + `split("\n\n")`로 문단 분리 + 출력
- [x] (9/6) Day 5 블록2 — 이상 비용 후보 + 나머지 위험 태그 → **7종 완성**
- [x] (9/3) Day 5 블록1 — 중복 신청 탐지 (`duplicated`)
- [x] (9/3) Day 4 블록3 — 규칙 함수 분리 (`detect_risks(df)`)
- [x] (8/28) Day 4 블록2 — 소모품 범위 탐지
- [x] (8/27) Day 4 블록1 — 택시비 사유 부족 탐지
- [x] (8/18) Day 3 — 영수증 누락·한도 초과·위험 컬럼
- [x] (8/15~18) Day 2 — 데이터 요약 (행/열/결측치/groupby)
- [x] (8/13) Day 1 — Streamlit 화면 + CSV 업로드
