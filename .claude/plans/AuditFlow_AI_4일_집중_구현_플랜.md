# AuditFlow AI — 4일 집중 구현 플랜

> 목표: 기존 AuditFlow AI를 단순 Streamlit 비용관리 앱에서  
> **FastAPI · PostgreSQL · pgVector · LLM · LangGraph · Human-in-the-loop · n8n · Docker · pytest/CI**가 연결된  
> **AX / Workflow Automation 포트폴리오 프로젝트**로 확장한다.

---

## 0. 최종 목표

### 현재 흐름

```text
CSV
 ↓
detect_risks()
 ↓
find_policy_evidence()
 ↓
make_draft()
 ↓
review_status
```

### 최종 흐름

```text
Streamlit / n8n
       ↓
    FastAPI
       ↓
   LangGraph
       ↓
 ┌───────────────┬───────────────┬───────────────┐
 ↓               ↓               ↓
Pandas Rules   pgVector RAG      LLM
 ↓               ↓               ↓
 └────────── Human Review ───────┘
                 ↓
            PostgreSQL

+ JSONL Observability
+ Docker
+ pytest
+ GitHub Actions
```

---

# 운영 원칙

- 총 기간: **4일**
- 하루 블록: **6블록**
- 블록당 시간: **35~50분**
- 하루 순수 구현 시간: 약 **4~5시간**
- 하루 마지막 블록은 가능하면 새 기능 구현보다:
  - 실패 테스트
  - 디버깅
  - 안 보고 설명하기
- 새 기술을 많이 추가하는 것보다 **기존 흐름을 실제로 연결하는 것**이 우선이다.
- 모든 기능은 다음 5단계로 끝낸다.

```text
이해
→ 구현
→ 연결
→ 실패 테스트
→ 설명
```

---

# Day 1 — FastAPI + 실제 LLM + Fallback

## 오늘 목표

기존 AuditFlow의 핵심 함수를 FastAPI 서비스로 노출하고,  
실제 LLM을 연결하되 실패 시 기존 Template으로 안전하게 fallback하도록 만든다.

---

## Block 1 — 현재 코드 흐름 다시 잡기

### 할 일

기존 함수들의 입력과 출력을 직접 확인한다.

```python
detect_risks(df)
→ risk_type
→ risk_reason

find_policy_evidence(risk_type)
→ policy_evidence

make_draft(row)
→ draft_message
```

### 직접 적어보기

```text
비용 데이터
 ↓
위험 탐지
 ↓
규정 검색
 ↓
보완 요청 초안
 ↓
Human Review
```

### 완료 기준

- [ ] `detect_risks()`의 역할 설명 가능
- [ ] `find_policy_evidence()`의 역할 설명 가능
- [ ] `make_draft()`의 역할 설명 가능
- [ ] 전체 기존 흐름을 코드 없이 설명 가능

### 30초 설명

> 비용 데이터를 규칙 엔진으로 검사하고, 위험 건이면 관련 규정을 검색하고, 규정 근거를 이용해 보완 요청 초안을 생성합니다.

---

## Block 2 — FastAPI 기본 API 만들기

### 생성

```text
api/
 └── main.py
```

### API

```http
POST /audit
```

### 예시 입력

```json
{
  "expense_id": 1,
  "employee": "김철수",
  "category": "식대",
  "amount": 50000,
  "receipt": true,
  "reason": "고객 미팅"
}
```

### 목표 응답

```json
{
  "expense_id": 1,
  "risk_type": "limit_exceeded",
  "risk_reason": "식대 한도 초과",
  "policy_evidence": "...",
  "draft_message": "...",
  "draft_source": "template",
  "review_status": "unreviewed"
}
```

### 완료 기준

- [ ] FastAPI 실행
- [ ] `/docs` 접속
- [ ] JSON 직접 입력
- [ ] 응답 정상 반환

---

## Block 3 — 기존 함수와 FastAPI 연결

### 연결 흐름

```text
HTTP Request
 ↓
Pydantic Model
 ↓
detect_risks()
 ↓
find_policy_evidence()
 ↓
make_draft()
 ↓
Response
```

### 핵심 개념

```text
HTTP request
→ Pydantic Model
→ Python 함수
→ Response
```

### 완료 기준

- [ ] `/audit`에서 기존 `detect_risks()` 호출
- [ ] 규정 검색 호출
- [ ] 초안 생성 함수 호출
- [ ] 기존 Streamlit 로직과 API 로직이 중복되지 않도록 분리

---

## Block 4 — 실제 LLM API 연결

### LLM 입력

```text
employee
category
amount
risk_reason
policy_evidence
```

### Prompt 예시

```text
다음 비용 신청에 대해 직원에게 전달할 보완 요청 메시지를 작성하라.

위험 이유:
{risk_reason}

관련 사내 규정:
{policy_evidence}

규정에 없는 내용을 임의로 만들지 말고,
담당자가 검토하기 쉬운 짧고 명확한 문장으로 작성하라.
```

### 설계 원칙

```text
위험 판정 → Pandas Rule
문장 생성 → LLM
최종 판단 → Human
```

### 완료 기준

- [ ] 실제 LLM 호출 성공
- [ ] `risk_reason` 전달
- [ ] `policy_evidence` 전달
- [ ] 결과가 `draft_message`에 저장

---

## Block 5 — LLM Fallback 구현

### 목표

```python
try:
    draft = call_llm(...)
    draft_source = "llm"

except Exception:
    draft = make_template(...)
    draft_source = "template"
```

### 실패 테스트

일부러 다음 중 하나를 발생시킨다.

- 잘못된 API Key
- 강제 Exception
- timeout 상황

### 완료 기준

- [ ] LLM 성공 시 `draft_source = llm`
- [ ] LLM 실패 시 `draft_source = template`
- [ ] LLM 실패에도 `/audit` API는 죽지 않음

---

## Block 6 — Day 1 디버깅 + 설명

### 테스트 케이스

```text
① 정상 비용
② 한도 초과
③ 영수증 누락
④ LLM 강제 실패
```

### 최종 흐름

```text
POST /audit
→ 위험 탐지
→ 규정 검색
→ LLM Draft
→ 실패 시 Template
```

### Day 1 완료 체크

- [ ] `/audit` 동작
- [ ] 기존 위험탐지 연결
- [ ] 기존 규정검색 연결
- [ ] 실제 LLM 연결
- [ ] Template fallback 동작
- [ ] 안 보고 전체 흐름 설명 가능

### 면접 설명

> 위험 판단은 LLM에게 맡기지 않고 Pandas 기반 업무 규칙으로 처리했습니다.  
> LLM은 확인된 규정 근거를 바탕으로 보완 요청 문장만 생성하며, 호출 실패 시 기존 Template으로 fallback하도록 설계했습니다.

---

# Day 2 — PostgreSQL + pgVector RAG

## 오늘 목표

검수 결과를 DB에 지속 저장하고,  
기존 키워드 규정 검색을 pgVector 기반 의미 검색으로 확장한다.

---

## Block 1 — PostgreSQL 환경 구성

### 구성

```text
Docker
 ├─ FastAPI
 └─ PostgreSQL + pgVector
```

### docker-compose 목표

```text
docker compose up
```

실행 후 PostgreSQL이 정상 기동되는 수준까지.

### 완료 기준

- [ ] PostgreSQL 실행
- [ ] FastAPI에서 DB 연결 성공
- [ ] DB 연결 문자열 환경변수 처리

---

## Block 2 — audit_results 테이블

### 테이블 예시

```text
audit_results
────────────────────
id
expense_id
employee
risk_type
risk_reason
policy_evidence
draft_message
draft_source
review_status
created_at
updated_at
```

### 목표

`POST /audit` 결과를 DB에 INSERT한다.

### 완료 기준

- [ ] `/audit` 실행 후 DB row 생성
- [ ] FastAPI 종료
- [ ] FastAPI 재실행
- [ ] 기존 결과가 DB에 그대로 존재

---

## Block 3 — Human Review API

### 추가 API

```http
GET /audit-results

PATCH /audit-results/{id}/review
```

### 상태

```text
unreviewed
approved
need_revision
rejected
```

### 예시

```json
{
  "review_status": "approved"
}
```

### 완료 기준

- [ ] 전체 결과 조회
- [ ] 특정 결과 상태 수정
- [ ] 앱 재실행 후 수정 상태 유지

---

## Block 4 — pgVector 설정

### PostgreSQL

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### policy_chunks 테이블

```text
policy_chunks
──────────────────
id
text
source
embedding
```

### 완료 기준

- [ ] pgVector extension 활성화
- [ ] 규정 문서를 Chunk 단위로 저장
- [ ] Embedding vector 저장 확인

---

## Block 5 — Embedding + Top-K Vector Search

### 기존

```text
risk_type
 ↓
keyword
 ↓
policy.txt 검색
```

### 개선

```text
risk_reason
 ↓
Embedding
 ↓
pgVector
 ↓
Cosine Similarity
 ↓
Top 3
```

### SQL 예시

```sql
SELECT
    id,
    text,
    1 - (embedding <=> :query_vector) AS similarity
FROM policy_chunks
ORDER BY embedding <=> :query_vector
LIMIT 3;
```

### 완료 기준

- [ ] Query Embedding 생성
- [ ] pgVector 검색
- [ ] Top-3 반환
- [ ] `policy_evidence`에 검색 결과 연결

---

## Block 6 — Keyword vs Vector 비교

### 테스트 예시

질문:

```text
식사 비용이 기준보다 너무 큼
```

규정:

```text
식대 1인당 최대 30,000원
```

### 비교

```text
Keyword Search
→ 특정 단어 일치 중심

Vector Search
→ 의미 유사도 중심
```

### 중요한 원칙

기존 keyword 검색은 삭제하지 않는다.

```text
keyword retriever
vector retriever
```

둘 다 유지한다.

### Day 2 완료 체크

- [ ] PostgreSQL 결과 저장
- [ ] Review 상태 DB 저장
- [ ] pgVector 적용
- [ ] Top-K 검색
- [ ] Keyword vs Vector 검색 비교 가능
- [ ] DB 재실행 테스트 완료

### 면접 설명

> 초기에는 위험 유형을 키워드로 변환해 규정을 검색했습니다.  
> 이후 표현이 달라도 의미가 유사한 규정을 찾을 수 있도록 pgVector 기반 의미 검색으로 확장했고, 기존 방식과 결과를 비교할 수 있도록 두 검색 방식을 모두 유지했습니다.

---

# Day 3 — LangGraph + Human Review + Observability

## 오늘 목표

기존 함수형 Workflow를 실제 상태 기반 조건 분기 Workflow로 바꾼다.

---

## Block 1 — AuditState 정의

### 예시

```python
class AuditState(TypedDict):
    expense: dict
    risk_type: str | None
    risk_reason: str | None
    policy_evidence: list
    draft_message: str | None
    draft_source: str | None
    review_status: str
    error: str | None
```

### 핵심 개념

```text
State = 전체 Workflow Node가 공유하는 현재 상태
```

### 완료 기준

- [ ] State 필드 직접 설명 가능
- [ ] 각 Node가 어떤 값을 읽고 쓰는지 설명 가능

---

## Block 2 — 기존 함수를 Node로 변환

### 기존

```python
detect_risks()
search_policy()
make_draft()
```

### LangGraph

```text
audit_node
retrieve_node
generate_node
save_node
human_review_node
```

### 원칙

새로운 알고리즘을 만드는 것이 아니다.

```text
기존 함수
→ LangGraph Node로 감싸기
```

### 완료 기준

- [ ] audit_node 실행
- [ ] retrieve_node 실행
- [ ] generate_node 실행
- [ ] State 값이 Node 사이에서 전달

---

## Block 3 — 위험 여부 조건 분기

### 흐름

```text
audit
 ↓
위험인가?
```

```text
NO  → save
YES → retrieve
```

### 완료 기준

- [ ] 정상 건은 retrieve로 가지 않음
- [ ] 위험 건만 retrieve로 이동
- [ ] `graph.invoke()` 실행 성공

---

## Block 4 — 규정 / LLM 조건 분기 추가

### 전체 Workflow

```text
START
  ↓
audit
  ↓
risk?
 ├─ no → save
 └─ yes
      ↓
   retrieve
      ↓
 evidence?
 ├─ no → human_review
 └─ yes
      ↓
   generate
      ↓
 LLM success?
 ├─ yes → human_review
 └─ no → fallback
             ↓
        human_review
             ↓
            save
```

### 완료 기준

- [ ] risk 분기
- [ ] evidence 분기
- [ ] LLM success/failure 분기
- [ ] fallback 후 Human Review 이동

---

## Block 5 — Observability

### 로그 항목

```text
run_id
node
started_at
latency_ms
success
error
llm_success
fallback_used
```

### 예시

```json
{
  "run_id": "abc123",
  "node": "generate",
  "latency_ms": 843,
  "success": false,
  "fallback_used": true,
  "error": "timeout"
}
```

### 저장

기존 JSONL 로그 구조를 최대한 재사용한다.

### 완료 기준

- [ ] Node 이름 기록
- [ ] 실행 시간 기록
- [ ] 오류 기록
- [ ] LLM 성공 여부 기록
- [ ] fallback 사용 여부 기록

---

## Block 6 — 의도적 장애 테스트

### 일부러 실패시킬 것

```text
① Vector 검색 결과 0개
② LLM Exception
③ DB 저장 오류
```

### 확인할 것

```text
어디서 실패했나?
Workflow가 완전히 멈췄나?
Fallback 되었나?
Human Review로 이동했나?
로그에 남았나?
```

### Day 3 완료 체크

- [ ] LangGraph State
- [ ] Node
- [ ] Conditional Edge
- [ ] Human Review 분기
- [ ] LLM fallback 분기
- [ ] JSONL Logging
- [ ] 실패 위치 추적 가능

### 면접 설명

> 처음에는 Python 함수들을 순차 호출하는 구조였습니다.  
> 하지만 규정 근거 없음, LLM 실패, Human Review 같은 조건 분기가 늘어나면서 상태와 분기 관리가 필요해졌고, 이를 명확하게 관리하기 위해 LangGraph를 도입했습니다.

---

# Day 4 — n8n + Docker + Test/CI + 포트폴리오

## 오늘 목표

AuditFlow를 외부 Workflow와 연결하고,  
테스트 및 CI를 추가해 실제 운영 가능한 형태의 포트폴리오로 정리한다.

---

## Block 1 — n8n Webhook

### 흐름

```text
Webhook
 ↓
FastAPI /audit
```

### 입력 JSON

```json
{
  "expense_id": 101,
  "employee": "홍길동",
  "category": "식대",
  "amount": 45000,
  "receipt": true,
  "reason": "외부 미팅"
}
```

### 완료 기준

- [ ] n8n Webhook 실행
- [ ] FastAPI `/audit` 호출
- [ ] 결과 정상 반환

---

## Block 2 — HTTP Request + IF

### Workflow

```text
Webhook
 ↓
HTTP Request
 ↓
IF
```

### IF 조건

```text
risk_type != null
```

### 분기

```text
위험 있음
→ 위험 처리

위험 없음
→ 정상 처리
```

### 완료 기준

- [ ] 정상 건과 위험 건이 서로 다른 경로로 이동

---

## Block 3 — n8n 후속 처리

### 하나만 선택

#### 선택 A

```text
위험 비용
→ Google Sheets 기록
```

#### 선택 B

```text
위험 비용
→ Slack / 메신저 알림
```

### 원칙

여러 서비스를 붙이는 것이 목표가 아니다.

```text
Webhook
→ API
→ IF
→ 후속 처리
```

이 E2E Workflow 자체가 핵심이다.

### 완료 기준

- [ ] 실제 후속 작업 1개 연결

---

## Block 4 — Docker 정리

### 최종 목표

```text
docker compose up
```

으로 최소 다음 서비스가 실행된다.

```text
FastAPI
PostgreSQL + pgVector
```

### 체크

- [ ] 환경변수 `.env`
- [ ] DB 접속
- [ ] FastAPI 접속
- [ ] pgVector extension 확인

---

## Block 5 — pytest + GitHub Actions

### 최소 테스트

```text
test_normal_expense
test_limit_exceeded
test_missing_policy
test_llm_fallback
test_review_status_update
```

### CI 흐름

```text
Git Push
 ↓
GitHub Actions
 ↓
pytest
 ↓
PASS
```

### 완료 기준

- [ ] pytest local pass
- [ ] GitHub Actions workflow 작성
- [ ] CI Green

---

## Block 6 — README + 면접 설명

### README 구조

```text
1. 문제
2. 기존 업무 방식
3. AuditFlow가 해결하는 방식
4. Architecture
5. Workflow
6. 기술 선택 이유
7. 실패 대응
8. Demo
9. Before / After
```

### 최종 3분 설명

> 비용정산 담당자가 모든 신청 건을 동일한 깊이로 수작업 검수하는 문제를 해결하기 위해 AuditFlow AI를 만들었습니다.
>
> 위험 판단 자체는 Pandas 기반 업무 규칙으로 처리해 결정론적으로 유지했습니다.
>
> 위험 건은 pgVector를 통해 관련 규정을 검색하고, 검색된 규정 근거를 바탕으로 LLM이 보완 요청 초안을 생성합니다.
>
> 규정이 없거나 LLM 호출이 실패하거나 담당자 최종 검수가 필요한 상황처럼 조건 분기가 증가하면서 LangGraph로 상태와 Workflow를 관리했습니다.
>
> 결과와 검수 상태는 PostgreSQL에 저장하고, 외부 업무 시스템에서는 n8n Webhook을 통해 `/audit` API를 호출할 수 있게 했습니다.
>
> LLM 실패 시 Template fallback을 적용하고 각 Workflow 단계의 실행 결과와 오류를 로그로 남겨 실패 지점을 추적할 수 있도록 구성했습니다.
>
> pytest와 GitHub Actions를 통해 핵심 규칙과 API 동작의 회귀를 방지했습니다.

---

# 최종 파일 구조

```text
Cost_Manager/
│
├─ app.py
│
├─ api/
│   └─ main.py
│
├─ src/
│   ├─ audit_rules.py
│   ├─ policy_retriever.py
│   ├─ draft_generator.py
│   ├─ database.py
│   └─ workflow.py
│
├─ tests/
│   └─ test_audit.py
│
├─ docker-compose.yml
├─ requirements.txt
│
├─ .github/
│   └─ workflows/
│       └─ test.yml
│
└─ README.md
```

---

# 최종 완료 체크리스트

## Backend

- [ ] FastAPI `/audit`
- [ ] 기존 Pandas 위험탐지 연결
- [ ] Pydantic Request/Response
- [ ] PostgreSQL 연결
- [ ] audit_results 저장
- [ ] Review 상태 변경 API

## AI / RAG

- [ ] 실제 LLM 호출
- [ ] risk_reason + policy_evidence Prompt 연결
- [ ] Template fallback
- [ ] pgVector extension
- [ ] policy_chunks 저장
- [ ] Query Embedding
- [ ] Vector Top-K 검색
- [ ] Keyword vs Vector 비교

## Workflow

- [ ] LangGraph State
- [ ] audit_node
- [ ] retrieve_node
- [ ] generate_node
- [ ] human_review_node
- [ ] save_node
- [ ] Conditional Edge
- [ ] LLM 실패 분기

## Automation

- [ ] n8n Webhook
- [ ] HTTP Request
- [ ] IF
- [ ] 후속 처리 1개

## Operations

- [ ] JSONL Log
- [ ] latency 기록
- [ ] error 기록
- [ ] fallback 기록
- [ ] Docker Compose
- [ ] pytest
- [ ] GitHub Actions Green

## Portfolio

- [ ] Architecture Diagram
- [ ] Workflow Diagram
- [ ] Keyword vs Vector 비교
- [ ] LLM fallback 사례
- [ ] Before / After
- [ ] README
- [ ] 3분 설명
- [ ] 코드 일부를 직접 수정하며 설명 가능

---

# 4일 이후 시간이 남으면 추가할 것

우선순위:

```text
1. API 테스트 강화
        ↓
2. Langfuse
        ↓
3. Redis / 비동기 처리
        ↓
4. Cloud 배포
```

---

# 이번 4일에는 제외할 것

```text
MCP Server
과도한 Multi-Agent
Airflow
BigQuery
Kubernetes
복잡한 AWS 인프라
```

이 기술들이 중요하지 않아서가 아니라, 현재 AuditFlow의 문제 규모에서는  
**Pandas → API → DB → RAG → LLM → LangGraph → Human Review → n8n → Logging → Test**  
흐름을 완성하는 것이 우선이다.

---

# 최종 기술 스택

```text
Python
Pandas
FastAPI
Pydantic
PostgreSQL
pgVector
Embedding
RAG
LLM API
LangGraph
Human-in-the-loop
n8n
Webhook
Docker
Logging
pytest
GitHub Actions
```

---

# 최종 목표 수준

| 기술 | 목표 |
|---|---|
| Pandas | 기존 규칙 직접 수정 가능 |
| FastAPI | 기본 API 직접 추가·수정 가능 |
| PostgreSQL | CRUD/상태 저장 설명 가능 |
| SQL | INSERT/SELECT/UPDATE/Vector Search 이해 |
| pgVector | Embedding 저장·검색 구조 설명 가능 |
| RAG | Retrieval → Context → Generation 설명 가능 |
| LLM | Prompt/Fallback 직접 수정 가능 |
| LangGraph | State/Node/Edge/분기 수정 가능 |
| Human-in-the-loop | AI와 사람의 책임 구분 설명 가능 |
| n8n | Webhook/HTTP/IF 직접 구성 가능 |
| Docker | 서비스 실행 구조 설명 가능 |
| Logging | 실패 위치 추적 가능 |
| pytest/CI | 핵심 테스트와 자동 실행 설명 가능 |

---

## 최종 한 문장

> 기존 Pandas 기반 비용검수 프로그램을 FastAPI 서비스로 분리하고 PostgreSQL에 검수 상태를 저장했으며, 규정 검색을 pgVector 기반 의미 검색으로 확장했습니다. 규정 없음·LLM 실패·Human Review 같은 조건 분기를 LangGraph로 관리하고, n8n Webhook을 통해 외부 업무 Workflow와 연결했으며, fallback·로그·pytest·CI까지 포함해 운영 관점의 AX Workflow Automation 프로젝트로 발전시켰습니다.
