# 오늘 할 일 (10/27 · DAY 2 — RAG, 블록 18~20 남음)

> 기준 로드맵: **`.claude/plans/10.17 계획 v5일분할.md`** DAY 2 (Block 11~20)
> DAY 1(Backend/DB/Review)은 끝났고, 지금은 **DAY 2 = pgVector RAG + 평가**.
> Block 11~17은 됐고(벡터검색은 이미 `/audit`에 연결됨), 남은 건 **평가 파트(B18~B20)**.
> **지금 집중할 건 👉 표시된 1개뿐.** 나머지는 그거 끝나고 보면 돼.
> 세션 사이 10분 휴식. 에러 15분 넘게 막히면 질문.
>
> **DAY 2 끝나면 보여야 할 최종 결과:** `/audit`에서 벡터검색이 실제로 돌고 + Keyword Hit@3 vs Vector Hit@3 숫자 비교표가 나온다.

## 블록 19 (25~30분) — Hit@3 계산 (Keyword vs Vector) · 🧠 직접 작성  👉 지금 이거
- [x] (정리 완료) 평가셋 `rag_eval_set.csv`를 `venv/Scripts/` → **프로젝트 루트로 이동 완료**
- [ ] 평가셋 50줄을 한 줄씩 읽어서 `query`로 Keyword Top3 / Vector Top3 각각 검색
- [ ] 각 줄의 `expected_policy`가 Top3 안에 들어있는지 판정 (= hit / miss)
- [ ] 성공 개수 세서 Hit@3 계산: `Keyword Hit@3 = __/50`, `Vector Hit@3 = __/50`
- 끝나면 보여야 할 결과: 실제 실행값으로 채운 비교표 (추정값 금지, 돌린 숫자만)

## 블록 20 (25~30분) — DAY 2 통합검증 + 결과 기록 + commit/PR · 🔧 세팅
- [ ] `/audit` 호출해서 RAG(벡터검색)가 실제로 도는지 확인 + 근거 없음 케이스 확인
- [ ] Keyword/Vector Hit@3 비교 결과를 README(또는 메모)에 기록
- [ ] `git status` → 변경 파일 확인 → commit → push → PR 생성
- 끝나면 보여야 할 결과: DAY 2 종료 — pgVector RAG 실제 연결 + Keyword vs Vector 숫자 비교 완료

---
## 완료
- [x] (DAY 2) B11 pgVector extension + `policy_chunks` 테이블 (save/search 함수 `database.py`)
- [x] (DAY 2) B12 policy.txt → Chunk 분리 (`make_policy_chunks`)
- [x] (DAY 2) B13 Chunk Embedding 생성 (`make_embedding`, Gemini 768차원)
- [x] (DAY 2) B14 Embedding → pgVector 저장 (`save_policy_chunk`)
- [x] (DAY 2) B15 Query Vector Search (`find_similar_policies`)
- [x] (DAY 2) B16 `/audit`에 Vector Search 연결 (`api/main.py:149`)
- [x] (DAY 2) B17 Keyword Retriever baseline 유지 (`find_keyword_policies`)
- [x] (DAY 2) B18 RAG 평가셋 50개 작성 — 내용 완성(단 위치 이동은 B19 첫 줄에서 처리)
- [x] (DAY 1 전체) Backend/DB/Review 흐름 종료: /audit · /audit/batch · risks[] · needs_review · PATCH review · Audit Trail · DB 저장/조회
