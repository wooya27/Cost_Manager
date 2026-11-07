# 01 · 시작점 고정 · 실행 환경 점검 (DAY1 B01)

> 기록일: 2026-11-07 (KST) · 작성 기준: 11.08 박람회 계획 B01 + 10.17 원본 Day1 Block1 / Day3 Block1

## 1. 저장소 / 버전

| 항목 | 값 |
|---|---|
| 브랜치 | `work_v2/end_to_end` |
| 최신 커밋 | `281adbd 작업 보강전` |
| 작업 전 변경파일 | `src/agent_workflow.py` (M), `logs/node_calls.jsonl` (M) |

## 2. DB · API · RAG 준비 상태

| 점검 항목 | 상태 | 근거 |
|---|---|---|
| Docker DB 실행 | OK | `auditflow_db` Up 4h (healthy), `0.0.0.0:5433->5432` |
| Docker API 실행 | OK | `auditflow_api` Up 4h, `0.0.0.0:8000->8000` |
| DB 접속 (Python→PostgreSQL) | OK | `create_tables()` 호출 성공 |
| `audit_results` 테이블 | OK | 56행 적재되어 있음 |
| `policy_chunks` 테이블 | OK (실행 중 DB) | 61행 적재 (= README "61규정"과 일치) |
| pgVector 확장 | OK | `pg_extension`에 `vector` 존재 |
| API HTTP 직접 호출 (`GET /`, `POST /audit`) | 미확인 | 이 세션에서 curl 네트워크 호출 권한 제한. 컨테이너는 Up 상태 |

## 3. 이번 블록에서 고친 것 (재현성 구멍)

**문제:** `create_tables()`가 `audit_results`만 만들고 `vector` 확장·`policy_chunks` 테이블은 만들지 않았다.
실행 중인 DB에 `policy_chunks`가 있는 이유는 과거 적재 스크립트가 만들어 **볼륨에 남아 있기 때문**이지,
새 환경에서 `docker compose up` 하면 RAG 테이블이 자동 준비되지 않는다.

**조치:** `src/database.py`의 `create_tables()`에 다음을 추가.
- `CREATE EXTENSION IF NOT EXISTS vector;`
- `CREATE TABLE IF NOT EXISTS policy_chunks (id, text, source, embedding vector);`

`CREATE ... IF NOT EXISTS`라서 기존 DB에는 영향 없음(호출 성공 확인). 단, **embedding 데이터 적재는 여전히 별도 스크립트**로 수행해야 한다.

## 4. 테스트 상태 (참고)

- `python -m pytest -m "not integration" -q` → **9 passed, 3 deselected** (integration 3개 제외)

## 30초 설명

> "Docker로 API가 켜졌다고 RAG까지 준비된 것은 아니다. API 컨테이너가 떠 있어도 `policy_chunks` 테이블과
> 규정 임베딩이 DB에 적재돼 있지 않으면 벡터 검색은 빈 결과를 돌려준다. 그래서 테이블 생성(스키마)과
> 데이터 적재(임베딩)를 분리해서 각각 점검해야 한다."

## 상태: 완료 (API HTTP 직접 호출만 미확인 — 컨테이너 Up으로 대체 확인)
