# 오늘 할 일 (10/18 · Day1 전체 10블록) — Day2 완전 종료

> 기준 로드맵: **`.claude/plans/10.17 계획 v5일분할.md`** DAY 1 (Block 1~10)
> 오늘 블록은 다 적어뒀다. 순서대로 위에서부터. **지금 집중할 건 👉 표시된 1개뿐.** 나머지는 그거 끝나고 보면 돼.
> 세션 사이 10분 휴식. 에러 15분 넘게 막히면 질문. 2블록 넘게 같은 데서 막히면 기록하고 다음으로.
>
> **오늘 끝나면 보여야 할 최종 흐름:** POST /audit → risks[] 탐지 → 근거 확인 → LLM 또는 needs_review → PostgreSQL 저장 → GET 조회 → PATCH Review → 재실행 후 상태 유지

## 블록 1 (25~30분) — 기준점 고정 + 작업 브랜치 · 🔧 세팅  👉 지금 이거
- [ ] `git status`로 현재 변경 파일 확인
- [ ] 새 작업 브랜치 생성: `git switch -c portfolio/day2-finish`
- [ ] 서버 실행 → `/docs` 접속
- [ ] 기존 `/audit`, `/audit-results` 각각 1회 호출
- [ ] PostgreSQL에 실제 데이터 들어가는지 확인
- 끝나면 보여야 할 결과: "현재 정상 API / DB 상태 / 오류 / 브랜치" 4줄을 내 말로 채울 수 있음

## 블록 2 (25~30분) — requirements.txt + Secret 정리 · 🔧 세팅
- [ ] `<<<<<<<` `=======` `>>>>>>>` 충돌 표식 제거
- [ ] 실제 import 기준 패키지 확인 (openai, psycopg[binary], python-dotenv, fastapi, uvicorn, pandas)
- [ ] `.env`가 Git 제외되는지 확인 + `.env.example` 생성/보완
- [ ] `docker-compose.yml` 하드코딩된 비밀번호 제거
- 끝나면 보여야 할 결과: `pip install -r requirements.txt` 충돌 표식 없이 설치 가능

## 블록 3 (25~30분) — FastAPI lifespan → create_tables() 자동 실행 · 🧠 직접 작성
- [ ] FastAPI startup/lifespan 위치 확인
- [ ] 서버 시작 시 `create_tables()` 실행되게 연결
- [ ] 기존 DB 있어도 문제없는지 확인 + 서버 재시작
- 끝나면 보여야 할 결과: 서버 시작 시 수동 테이블 생성 필요 없음

## 블록 4 (25~30분) — detect_risks()를 risks[] 구조로 변경 · 🧠 직접 작성
- [ ] 기존 `risk_type`/`risk_reason` 덮어쓰기 위치 찾기
- [ ] `risks = []` 구조로 변경, 각 규칙이 `{risk_type, risk_reason}` 추가
- [ ] 정상 건은 빈 리스트 `[]`
- [ ] 사례 확인: 정상 / 영수증 누락 / 한도 초과 / 복합 위험
- 끝나면 보여야 할 결과: 한 건에 위험 2개 이상이 동시에 보임

## 블록 5 (25~30분) — risks[]를 API + PostgreSQL까지 연결 · 🧠 직접 작성
- [ ] `/audit` 응답을 `risks[]` 기준으로 변경
- [ ] DB에 복수 위험 JSON/JSONB로 저장
- [ ] 기존 단일 risk 필드 참조 코드 찾아 수정
- 끝나면 보여야 할 결과: Swagger 응답과 DB 양쪽에서 같은 risks[] 확인

## 블록 6 (25~30분) — POST /audit/batch · 🧠 직접 작성
- [ ] 여러 건 입력 Request 구조 정의 + `/audit/batch` Endpoint 생성
- [ ] 여러 행 DataFrame 생성 → 비교형 규칙 실행 → 건별 결과 반환
- [ ] 테스트: 중복 신청 / 이상 비용 / 정상 여러 건
- 끝나면 보여야 할 결과: 단건에서 못 잡던 비교형 위험이 batch에서 탐지됨

## 블록 7 (25~30분) — 규정 근거 없음 → LLM 호출 금지 · 🧠 직접 작성
- [ ] 규정 검색 실패값("관련 규정 확인 필요"/빈 값) 처리
- [ ] LLM 호출 전 조건 추가 → 근거 없으면 `draft_source = "needs_review"`
- [ ] DB 저장 확인
- 끝나면 보여야 할 결과: 근거 없는 입력에서 LLM 호출 0회, DB에 needs_review

## 블록 8 (25~30분) — PATCH Review API · 🧠 직접 작성
- [ ] `PATCH /audit-results/{id}/review` Request Model 작성
- [ ] 허용 상태 검증 (unreviewed / approved / need_revision / rejected)
- [ ] 기존 `update_review_status()` 연결 + 없는 id 처리
- [ ] Swagger에서 직접 호출
- 끝나면 보여야 할 결과: PATCH → 200 → GET에서 변경 상태 확인

## 블록 9 (25~30분) — Audit Trail + DB 실패 확인 · 🧠 직접 작성
- [ ] `review_note` / `reviewed_at` / `updated_at` 추가
- [ ] review 변경 시 timestamp 기록
- [ ] 서버 재시작 후 상태 유지 확인
- [ ] 가능하면 DB 잠깐 내려 실패 확인 (에러 위치 + 로그)
- 끝나면 보여야 할 결과: 언제/어떤 상태로 검수했는지 최소 기록 가능

## 블록 10 (25~30분) — Day1 통합검증 + Commit/PR · 🔧 세팅
- [ ] 통합 테스트: /audit · /audit/batch · risks[] · needs_review · DB 저장 · GET · PATCH · 재시작 후 유지
- [ ] `git status` → 변경 파일 확인 → commit → push → PR 생성
- 끝나면 보여야 할 결과: Day2 핵심 Backend/DB/Review 흐름 종료

---
## 완료
- [x] (이전) `/audit` → 기존 3함수(detect_risks→find_policy_evidence→make_draft) 연결, 결과 JSON 반환
- [x] (이전) 실제 Gemini LLM 연결 + try/except fallback (성공→`llm`, 실패→`template`)
- [x] (이전) `/audit` → PostgreSQL 저장 + DB id 반환
- [x] (이전) `GET /audit-results` 조회
- [x] (이전) `update_review_status()` DB 함수 추가
