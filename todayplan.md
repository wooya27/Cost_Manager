# 오늘 할 일 (10/1 수) — AuditFlow 4일 플랜 Day1 시작

> 기준 로드맵: **`.claude/plans/AuditFlow_AI_4일_집중_구현_플랜.md`** Day 1
> 오늘 범위: Day1 Block 1~3 (코드이해 → FastAPI 띄우기 → 기존 함수 연결)
> **지금 집중은 👉 1개만.** 세션 사이 10분 휴식. 에러 15분 넘게 막히면 질문.

## 오늘 목표선
- **최소선:** Block 1~2 = 기존 흐름 설명 + FastAPI `/docs` 뜨기
- **목표:** Block 3 = `/audit`에 기존 함수(detect_risks/find_policy_evidence/make_draft) 연결
- (Day1 나머지 Block4~6=LLM+fallback, Day2 전체는 내일)

---
## 완료
- [x] (10/1) Day1 블록1 — 기존 3함수 흐름 안 보고 설명. detect_risks=전체 df 받아 위험행에 risk_type/risk_reason 채워 df 반환 / find_policy_evidence(risk_type, policy_messages)=규정문단 반환, 못찾으면 "관련 규정 확인 필요" / make_draft(row)=draft_message+draft_source **2개** 리턴(출처 꼬리표가 fallback 핵심)

## 완료 (이어서)
- [x] (10/1) Day1 블록2 — FastAPI `api/main.py`: `GET /`(상태확인) + `POST /audit`. Pydantic `ExpenseRequest` 모델로 입력 규격 검사(reason만 Optional). `uvicorn api.main:app --reload` → `/docs`에서 echo 응답 확인

## 진행 중 / 다음
- [ ] Day1 블록3 — `/audit` 안에서 기존 3함수 호출 연결: 입력 1건→DataFrame→detect_risks→find_policy_evidence→make_draft→결과 JSON (Streamlit 로직과 중복 안 되게)
