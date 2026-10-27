# 오늘 할 일 (10/27 · DAY 2 — RAG, 블록 18~20 남음)

> 기준 로드맵: **`.claude/plans/10.17 계획 v5일분할.md`** DAY 2 (Block 11~20)
> DAY 1(Backend/DB/Review)은 끝났고, 지금은 **DAY 2 = pgVector RAG + 평가**.
> Block 11~17은 됐고(벡터검색은 이미 `/audit`에 연결됨), 남은 건 **평가 파트(B18~B20)**.
> **지금 집중할 건 👉 표시된 1개뿐.** 나머지는 그거 끝나고 보면 돼.
> 세션 사이 10분 휴식. 에러 15분 넘게 막히면 질문.
>
> **DAY 2 끝나면 보여야 할 최종 결과:** `/audit`에서 벡터검색이 실제로 돌고 + Keyword Hit@3 vs Vector Hit@3 숫자 비교표가 나온다.

> ✅ DAY 2(RAG) 전체 완료. 다음은 **DAY 3 (LangGraph + 장애복구 + Logging, Block 21~30)**.
> "다음 뭐해?" 라고 하면 DAY 3 블록 뽑아줄게.

---
## 완료
- [x] (DAY 2) B19 Hit@3 계산 — Keyword vs Vector (`src/rag_evaluator.py`, 실측값)
- [x] (DAY 2) B20 DAY 2 통합검증 + 결과 기록 + commit/PR (RAG 평가 v1/v2 README 반영)
- [x] (DAY 2) B11 pgVector extension + `policy_chunks` 테이블 (save/search 함수 `database.py`)
- [x] (DAY 2) B12 policy.txt → Chunk 분리 (`make_policy_chunks`)
- [x] (DAY 2) B13 Chunk Embedding 생성 (`make_embedding`, Gemini 768차원)
- [x] (DAY 2) B14 Embedding → pgVector 저장 (`save_policy_chunk`)
- [x] (DAY 2) B15 Query Vector Search (`find_similar_policies`)
- [x] (DAY 2) B16 `/audit`에 Vector Search 연결 (`api/main.py:149`)
- [x] (DAY 2) B17 Keyword Retriever baseline 유지 (`find_keyword_policies`)
- [x] (DAY 2) B18 RAG 평가셋 50개 작성 — 내용 완성(단 위치 이동은 B19 첫 줄에서 처리)
- [x] (DAY 1 전체) Backend/DB/Review 흐름 종료: /audit · /audit/batch · risks[] · needs_review · PATCH review · Audit Trail · DB 저장/조회
