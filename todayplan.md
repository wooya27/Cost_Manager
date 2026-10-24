# 오늘 할 일 (10/23 · DAY 1 블록9~10 남음)

> 기준 로드맵: **`.claude/plans/10.17 계획 v5일분할.md`** DAY 1 (Block 1~10)
> 블록 1~8은 끝났고, 남은 건 블록 9~10. 순서대로 위에서부터. **지금 집중할 건 👉 표시된 1개뿐.** 나머지는 그거 끝나고 보면 돼.
> 세션 사이 10분 휴식. 에러 15분 넘게 막히면 질문. 2블록 넘게 같은 데서 막히면 기록하고 다음으로.
>
> **오늘 끝나면 보여야 할 최종 흐름:** POST /audit → risks[] 탐지 → 근거 확인 → LLM 또는 needs_review → PostgreSQL 저장 → GET 조회 → PATCH Review → 재실행 후 상태 유지

## 블록 9 (25~30분) — Audit Trail + DB 실패 확인 · 🧠 직접 작성  👉 지금 이거
- [ ] `review_note` / `reviewed_at` / `updated_at` 추가
- [ ] review 변경 시 timestamp 기록
- [ ] 서버 재시작 후 상태 유지 확인
- [ ] 가능하면 DB 잠깐 내려 실패 확인 (에러 위치 + 로그)
- 끝나면 보여야 할 결과: 누가/언제/어떤 상태로 검수했는지 최소 기록 가능

## 블록 10 (25~30분) — Day1 통합검증 + Commit/PR · 🔧 세팅
- [ ] 통합 테스트: /audit · /audit/batch · risks[] · needs_review · DB 저장 · GET · PATCH · 재시작 후 유지
- [ ] `git status` → 변경 파일 확인 → commit → push → PR 생성
- 끝나면 보여야 할 결과: Day1(= MASTER의 Day2) 핵심 Backend/DB/Review 흐름 종료

---
## 완료
- [x] (10/18) 블록1 기준점 고정 + 서버/DB 동작 확인
- [x] (10/18) 블록2 requirements.txt 충돌 제거 + .env.example + docker-compose 비밀번호 정리
- [x] (10/18) 블록3 FastAPI lifespan → create_tables() 자동 실행
- [x] (10/18) 블록4 detect_risks() → risks[] 구조로 변경 (복합 위험)
- [x] (10/18) 블록5 risks[]를 /audit 응답 + PostgreSQL 저장까지 연결
- [x] (10/21) 블록6 POST /audit/batch — 여러 건 입력 → DataFrame 여러 행 → 건별 risks[] 반환
- [x] (10/23) 블록7 needs_review — 근거 없으면 LLM 호출 X → draft_source="needs_review" (+ /audit 루프 버그 3개 수정)
- [x] (10/23) 블록8 PATCH /audit-results/{id}/review — 상태 검증 + 없는 id 404
- [x] (이전) `/audit` → 기존 3함수(detect_risks→find_policy_evidence→make_draft) 연결, 결과 JSON 반환
- [x] (이전) 실제 Gemini LLM 연결 + try/except fallback (성공→`llm`, 실패→`template`)
- [x] (이전) `/audit` → PostgreSQL 저장 + DB id 반환
- [x] (이전) `GET /audit-results` 조회
- [x] (이전) `update_review_status()` DB 함수 추가
