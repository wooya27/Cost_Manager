# 오늘 할 일 (10/4 토 · 3블록) — Day1 마무리 (LLM 연결 → Fallback → 디버깅)

> 기준 로드맵: **`.claude/plans/AuditFlow_AI_4일_집중_구현_플랜.md`** Day 1 (Block 4~6)
> 오늘 블록은 다 적어뒀다. 순서대로 위에서부터. **지금 집중할 건 👉 1개뿐.** 나머지는 그거 끝나고 보면 돼.
> 세션 사이 10분 휴식. 에러 15분 넘게 막히면 질문.

## 블록 5 (30~40분) — LLM Fallback 구현 · 🧠 직접 작성  👉 지금 이거
- [ ] `make_llm_draft` 호출을 `try/except`로 감싸서, LLM 실패하면 기존 `make_draft` 템플릿으로 안전하게 넘어가게
- [ ] 성공 → `draft_source="llm"`, 실패 → `draft_source="template"`
- [ ] 일부러 실패시켜보기 (잘못된 API Key / 강제 Exception 중 하나)
- 끝나면 보여야 할 결과: LLM 강제 실패시켜도 `/audit`이 안 죽고, 템플릿 문장 + `draft_source: "template"`로 응답한다

## 블록 6 (25~30분) — Day1 디버깅 + 안 보고 설명 · 🧠 직접 작성
- [ ] 테스트 4건 넣어보기: ① 정상 ② 한도초과 ③ 영수증 누락 ④ LLM 강제 실패
- [ ] 각각 응답의 `risk_type` / `draft_source`가 기대대로인지 확인
- [ ] 안 보고 30초 설명: "위험 판단은 Pandas 규칙, 문장 생성은 LLM, 실패하면 템플릿 fallback"
- 끝나면 보여야 할 결과: 4케이스 응답 캡처 + 전체 흐름 입으로 설명 성공

---
## 완료
- [x] (10/1) Day1 블록1 — 기존 3함수 흐름 안 보고 설명 (detect_risks / find_policy_evidence / make_draft 2개 리턴·출처 꼬리표가 fallback 핵심)
- [x] (10/1) Day1 블록2 — FastAPI `api/main.py`: `GET /` + `POST /audit`, Pydantic `ExpenseRequest` 입력검사, `/docs` echo 확인
- [x] (10/4까지) Day1 블록3 — `/audit`에서 기존 3함수(detect_risks→find_policy_evidence→make_draft) 연결, 결과 JSON 반환
- [x] (10/4) Day1 블록4 — `/audit`에 실제 Gemini LLM 연결. llm_generator.py를 OpenAI 호환 엔드포인트로 변경(base_url=generativelanguage.../openai/, api_key=OPENAI_API_KEY에 든 Gemini키, model=gemini계열), `responses.create`→`chat.completions.create`로 교체. 한도초과 건 → `draft_source:"llm"` + 실제 LLM 문장 확인
