# 07 · 운영 Runbook + 배포 준비 (DAY2 B12 / 10.17 Day6)

> 기록일: 2026-11-07 (KST)

## A. 로컬 실행 절차 (재현)

```bash
# 1) DB + API 컨테이너
docker compose up -d            # db(5433), api(8000)
# 또는 API만 로컬에서:
python -m uvicorn api.main:app --reload   # http://localhost:8000/docs

# 2) RAG 규정 임베딩 적재 (새 환경에서 1회) — 테이블은 create_tables가 생성, 데이터는 별도
#    (규정 임베딩 적재 스크립트 실행 — policy_chunks가 비어 있으면 벡터 검색이 빈 결과)

# 3) 동작 확인
python -m pytest -m "not integration" -q   # 13 passed
python -m pytest -m integration -v          # DB 켜진 상태에서 3 passed
```

## B. 환경변수 (값은 비워둠 / `.env`는 git 제외)

| 이름 | 용도 |
|---|---|
| `DATABASE_URL` | PostgreSQL 접속 (로컬 예: `...@localhost:5433/...`) |
| `GEMINI_API_KEY` | LLM/임베딩 호출 |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | docker-compose DB 초기화 |

- ✅ `.env`는 `.gitignore`로 제외, `.env.example`만 추적(값 없음).
- ✅ `docker-compose.yml`에 비밀번호 하드코딩 없음(모두 `${...}` 변수).
- ✅ `__pycache__/` 무시.

## C. 클라우드 배포 (본인이 해야 하는 단계 — 계정 필요)

```text
1) 관리형 PostgreSQL 생성 (Neon 또는 Supabase 중 1개) → DATABASE_URL 확보
   - pgvector 확장 지원 확인 (Neon/Supabase 지원). 접속 후 create_tables() 1회 → policy_chunks 생성
2) API 배포 (Render 또는 Google Cloud Run 중 1개)
   - 이 저장소 Dockerfile 그대로 사용 가능 (uvicorn 0.0.0.0:8000)
   - 환경변수에 DATABASE_URL, GEMINI_API_KEY 설정 (Production Secret)
3) 공개 URL/docs 접속 확인
4) n8n HTTP Request URL을 host.docker.internal → 배포 URL로 변경 (06 참고)
```

- 목표: localhost가 아니라 **외부에서 호출 가능한 `/docs`** 1개.
- 처음부터 복잡한 AWS 인프라는 범위 밖.

## D. ⚠️ 저장소 정리 필요 (커밋 전 확인)

```bash
# 런타임 로그가 git에 추적되고 있음 → 제거 + 무시 (실데이터 유출 방지)
git rm --cached logs/llm_calls.jsonl logs/node_calls.jsonl
echo "logs/" >> .gitignore
# 빈 placeholder: tests/data/synthetic_audit_cases.csv, expected_risks.csv (0바이트) 정리 검토
```
> ※ 위 정리는 **사용자 승인 후** 실행 (커밋된 파일 추적 해제 + 로그 내용 점검).

## 30초 설명
> "로컬에선 docker compose로 API+DB가 뜨고, 배포는 같은 Dockerfile을 관리형 DB·API 서비스에 올리고
> 환경변수로 Secret을 주입하면 된다. 비밀값은 .env로 분리돼 git에 올라가지 않는다.
> 다만 런타임 로그가 추적되고 있어 공개 전 제거가 필요하다."

## 상태: 부분 완료 (로컬 재현·시크릿 분리 확인 / 클라우드 배포는 본인 계정 필요)
