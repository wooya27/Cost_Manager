# Cost_Manager — AuditFlow AI

## 1. 프로젝트 소개

**AuditFlow AI**는 비용정산 데이터를 입력받아 위험 가능성이 있는 비용 건을 자동으로 탐지하고, 관련 사내 규정을 RAG로 검색한 뒤 LLM을 활용해 보완 요청 초안을 생성하는 **비용정산 1차 검수 시스템**입니다.

AI의 결과를 바로 최종 판단으로 사용하지 않고 담당자가 마지막으로 확인하는 **Human-in-the-loop** 구조를 적용했습니다.

주요 목표는 다음과 같습니다.

- 반복적인 비용정산 1차 검수 자동화
- 위험 비용 후보 조기 탐지
- 관련 사내 규정 자동 검색
- 규정 근거 기반 보완 요청 초안 생성
- 담당자 검수 및 검수 상태 저장
- RAG 검색 성능의 정량적 평가

---

## 2. 해결하려는 업무 문제

비용정산 업무에서는 담당자가 많은 신청 건을 직접 확인하면서 다음과 같은 문제를 찾아야 합니다.

- 영수증 누락
- 중복 신청
- 비용 한도 초과
- 사용 사유 누락
- 추가 승인 필요 비용
- 이상 비용 후보

문제가 발견된 후에도 담당자는 다시 사내 규정을 확인하고 신청자에게 보낼 보완 요청 문구를 직접 작성해야 합니다.

이 과정은 반복적이며 신청 건수가 증가할수록 검수 시간이 크게 늘어납니다.

AuditFlow AI는 다음 흐름을 자동화하여 담당자가 **위험 건과 근거를 중심으로 검수**할 수 있도록 하는 것을 목표로 합니다.

```text
비용 신청
↓
위험 후보 탐지
↓
관련 규정 검색
↓
규정 근거 확인
↓
보완 요청 초안 생성
↓
담당자 검수
↓
결과 저장
```

---

## 3. 전체 시스템 흐름

### 3.1 비용정산 처리 흐름

```text
비용 데이터 입력
↓
Pandas / FastAPI
↓
위험 후보 탐지
↓
risk_reason 생성
↓
Embedding
↓
PostgreSQL + pgVector
↓
관련 규정 Top-K 검색
↓
policy_evidence
↓
LLM Prompt
↓
보완 요청 초안
↓
Human Review
↓
PostgreSQL 저장
```

### 3.2 RAG Indexing 흐름

RAG 검색을 위해 사내 규정 문서를 미리 Vector DB에 저장합니다.

```text
policy.txt
↓
규정 문단 분리
↓
Chunk 생성
↓
Gemini Embedding
↓
768차원 Vector
↓
PostgreSQL + pgVector 저장
```

현재 RAG v2 기준으로 **61개의 비용 규정**을 Vector DB에 저장했습니다.

### 3.3 RAG Retrieval 흐름

비용 위험이 탐지되면 위험 사유를 검색 Query로 사용합니다.

```text
risk_reason
↓
Query Embedding
↓
pgVector Similarity Search
↓
Top-K 규정
↓
policy_evidence
```

검색된 규정 근거는 LLM의 Context로 전달됩니다.

---

## 4. 주요 기능

### 4.1 비용정산 데이터 처리

비용정산 CSV 데이터를 Pandas DataFrame으로 읽어 위험 탐지와 분석에 사용합니다.

Streamlit에서는 CSV 업로드 및 검수 결과 확인 기능을 제공합니다.

---

### 4.2 위험 후보 자동 탐지

업무 규칙을 기반으로 비용 데이터를 검사하여 위험 후보를 탐지합니다.

현재 주요 위험 유형은 다음과 같습니다.

- 영수증 누락
- 식대 한도 초과
- 택시비 사유 부족
- 사무용품 추가 승인
- 중복 신청 의심
- 교통비 한도 초과
- 이상 비용 후보

위험 탐지 결과는 다음 단계인 규정 검색에 전달됩니다.

```text
비용 데이터
↓
detect_risks()
↓
risks[]
↓
risk_type
risk_reason
```

---

### 4.3 Vector 기반 규정 검색

탐지된 위험의 `risk_reason`을 Embedding으로 변환하고 PostgreSQL pgVector에 저장된 규정 Vector와 유사도를 비교합니다.

```text
risk_reason
↓
Embedding
↓
pgVector
↓
Vector Similarity Search
↓
Top-K 규정
```

검색 결과 중 관련 규정을 `policy_evidence`로 사용합니다.

기존 Keyword Search는 삭제하지 않고 **Baseline**으로 유지하여 Vector Search와 검색 성능을 비교했습니다.

---

### 4.4 LLM 기반 보완 요청 초안 생성

비용 정보, 위험 사유, 검색된 규정 근거를 LLM Prompt에 전달하여 신청자에게 보낼 보완 요청 초안을 생성합니다.

```text
비용 정보
+
risk_reason
+
policy_evidence
↓
LLM
↓
draft_message
```

검색 근거가 부족하거나 LLM 호출 과정에 문제가 발생하면 자동 결과를 최종 판단으로 사용하지 않고 **fallback 또는 Human Review 경로**로 전달하도록 설계했습니다.

---

### 4.5 Human Review

AI가 생성한 결과는 최종 결정이 아닙니다.

담당자는 다음 정보를 확인합니다.

- 위험 유형
- 위험 사유
- 관련 규정 근거
- 보완 요청 초안
- 초안 출처
- 검수 상태

검수 상태는 `review_status`로 관리합니다.

---

### 4.6 PostgreSQL 저장

Audit 결과와 검수 정보를 PostgreSQL에 저장합니다.

주요 저장 정보:

- 신청자 정보
- 비용 정보
- risks
- risk_type
- risk_reason
- policy_evidence
- draft_message
- draft_source
- review_status
- review_note
- 생성 및 수정 시간

이를 통해 API 호출이 끝난 이후에도 검수 상태와 결과를 다시 조회할 수 있습니다.

---

### 4.7 FastAPI Audit API

FastAPI를 이용해 비용 신청을 Backend API로 처리합니다.

주요 흐름:

```text
POST /audit
↓
위험 탐지
↓
Vector Search
↓
규정 근거 연결
↓
LLM 초안 생성
↓
DB 저장
```

저장된 Audit 결과는 조회 API를 통해 다시 확인할 수 있습니다.

---

### 4.8 Dashboard

Streamlit Dashboard에서 다음 정보를 확인할 수 있습니다.

- 전체 신청 건수
- 위험 건수
- 총 신청 금액
- 위험 유형별 현황

---

### 4.9 검수 결과 CSV 다운로드

위험 탐지 결과, 규정 근거, 초안, 검수 상태가 포함된 최종 DataFrame을 CSV 파일로 다운로드할 수 있습니다.

---

## 5. Agent 역할 구조

AuditFlow AI는 하나의 기능이 모든 업무를 처리하지 않고 역할별로 책임을 분리했습니다.

### AuditRuleAgent

비용 데이터를 검사하고 위험 후보를 탐지합니다.

```text
비용 데이터
↓
업무 규칙 검사
↓
risks[]
```

### PolicySearchAgent

위험 사유를 이용해 관련 사내 규정을 검색합니다.

현재는 pgVector 기반 Vector Search를 사용합니다.

```text
risk_reason
↓
Embedding
↓
Vector Search
↓
policy_evidence
```

### DraftMessageAgent

비용 정보와 규정 근거를 바탕으로 LLM을 호출하여 보완 요청 초안을 생성합니다.

### ReviewSupportAgent

위험 사유, 규정 근거, 보완 요청 초안을 담당자가 확인할 수 있도록 지원합니다.

역할을 분리한 이유는 다음과 같습니다.

- 각 기능의 책임을 명확하게 분리
- 오류 발생 위치 확인 용이
- 기능별 수정 및 테스트 용이
- Agent Workflow로 확장하기 쉬운 구조
- 추후 LangGraph Node로 재사용 가능

---

## 6. 현재 Agent Workflow

현재는 기존 Python 함수를 이용해 함수형 Workflow를 구성했습니다.

```text
위험 건
↓
State 생성
↓
위험 확인
↓
규정 검색
↓
초안 생성
↓
Human Review
↓
결과 저장
```

State는 Workflow가 처리 중인 한 건의 정보를 저장하는 작업 상태입니다.

예:

```text
expense
↓
risks 추가
↓
policy_evidence 추가
↓
draft_message 추가
↓
review_status 추가
```

현재 단계에서는 Python 함수형 Workflow를 사용하고 있으며, 다음 단계에서 **LangGraph 기반 State / Node / Conditional Edge 구조**로 확장할 예정입니다.

---

## 7. 프로젝트 구조

```text
Cost_Manager/
│
├── app.py
│   └── Streamlit UI 및 Dashboard
│
├── policy.txt
│   └── RAG v2 비용정산 규정 61개
│
├── policy_v1.txt
│   └── RAG v1 규정 백업
│
├── rag_eval_set_v1.csv
│   └── RAG v1 평가 질의 50개
│
├── rag_eval_set_v2.csv
│   └── RAG v2 평가 질의 1,037개
│
├── sample_expenses_500.csv
│   └── 테스트용 비용정산 데이터
│
├── api/
│   └── main.py
│       └── FastAPI Audit / Review API
│
├── src/
│   ├── audit_rules.py
│   │   └── 위험 후보 탐지 규칙
│   │
│   ├── policy_retriever.py
│   │   └── Keyword / Vector 기반 규정 검색
│   │
│   ├── llm_generator.py
│   │   └── Gemini LLM 기반 보완 요청 초안 생성
│   │
│   ├── draft_generator.py
│   │   └── 규칙 기반 템플릿 초안 생성 (LLM 실패 시 Fallback)
│   │
│   ├── database.py
│   │   └── PostgreSQL / pgVector 연결 및 저장
│   │
│   ├── agent_workflow.py
│   │   └── 현재 Python 함수형 Workflow
│   │
│   ├── observability.py
│   │   └── Workflow 실행 로그
│   │
│   ├── generate_rag_eval_set.py
│   │   └── RAG 평가 질의 자동 생성
│   │
│   ├── validate_rag_eval_set.py
│   │   └── 평가 데이터 품질 검증
│   │
│   ├── rag_evaluator.py
│   │   └── RAG v1 검색 성능 평가
│   │
│   └── rag_evaluator_v2.py
│       └── RAG v2 Hit@1 / Hit@3 / Hit@5 평가
│
├── logs/
│   └── llm_calls.jsonl
│       └── Workflow 실행 로그
│
└── README.md
```

### 왜 파일을 분리했는가?

모든 기능을 `app.py` 하나에 작성하면 UI, 업무 규칙, DB, RAG, LLM 로직이 서로 섞여 수정과 테스트가 어려워집니다.

따라서 역할별로 파일을 분리했습니다.

```text
app.py
= UI

api/main.py
= Backend API

audit_rules.py
= 위험 판단

policy_retriever.py
= 규정 검색

llm_generator.py
= Gemini LLM 초안 생성

draft_generator.py
= 규칙 기반 템플릿 초안 (Fallback)

database.py
= PostgreSQL / pgVector

agent_workflow.py
= 업무 처리 순서

observability.py
= 실행 기록

rag_evaluator*.py
= RAG 성능 평가
```

---

## 8. 기술 스택

### Python

프로젝트의 주요 업무 로직, RAG, API 및 평가 코드를 구현했습니다.

### Pandas

CSV 데이터를 DataFrame으로 불러오고 위험 탐지, 필터링, 집계 및 평가 데이터 처리에 사용했습니다.

### Streamlit

비용 데이터 업로드, 위험 결과 확인, 상세 검수, Dashboard 및 CSV 다운로드 UI 구현에 사용했습니다.

### FastAPI

비용정산 Audit API 및 검수 관련 Backend API 구현에 사용했습니다.

### PostgreSQL

Audit 결과, 검수 상태 및 규정 데이터를 저장합니다.

### pgVector

규정 Embedding을 PostgreSQL에 저장하고 Vector Similarity Search를 수행합니다.

### Gemini API

다음 기능에 사용합니다.

- 규정 Embedding 생성
- Query Embedding 생성
- LLM 기반 보완 요청 초안 생성
- RAG 평가 질의 생성

### Docker

PostgreSQL 및 개발 실행 환경 구성에 사용합니다.

### JSONL

Workflow 및 LLM 실행 이력을 한 줄 단위로 기록합니다.

### Git / GitHub

소스 코드 버전 관리와 개발 이력 관리에 사용합니다.

---

## 9. 안전 설계

AuditFlow AI는 자동 탐지 및 LLM 결과를 바로 최종 판단으로 사용하지 않습니다.

```text
위험 탐지
↓
관련 규정 검색
↓
규정 근거 확인
↓
보완 요청 초안 생성
↓
담당자 검수
```

즉 시스템의 역할은 **판단 보조**입니다.

최종 결정은 담당자가 수행합니다.

### Human-in-the-loop

```text
AI / 자동화 결과
↓
사람 확인
↓
최종 판단
```

### 근거 기반 생성

LLM에 비용 정보만 전달하지 않고 검색된 `policy_evidence`를 함께 전달합니다.

```text
위험 정보
+
검색된 규정 근거
↓
LLM
```

### 근거 부족

관련 규정을 확보하지 못한 경우 임의의 규정을 만들어내는 대신 Human Review 경로로 전달합니다.

### LLM 실패

LLM 호출 과정에서 문제가 발생하더라도 전체 Workflow가 중단되지 않도록 fallback 구조를 사용합니다.

---

## 10. 실행 방법

### 10.1 프로젝트 폴더 이동

Cost_Manager 프로젝트 폴더에서 실행합니다.

### 10.2 필요한 패키지 설치

```text
pip install -r requirements.txt
```

### 10.3 PostgreSQL 실행

```text
docker compose up -d
```

### 10.4 FastAPI 실행

```text
python -m uvicorn api.main:app --reload
```

실행 후 Swagger에서 API를 테스트할 수 있습니다.

```text
POST /audit
GET /audit-results
```

### 10.5 Streamlit 실행

```text
streamlit run app.py
```

Streamlit에서는 다음 기능을 확인할 수 있습니다.

- 비용 CSV 업로드
- 위험 후보 탐지
- 위험 사유
- 관련 규정 근거
- 보완 요청 초안
- 검수 상태
- Dashboard
- 검수 결과 CSV 다운로드

### 10.6 Agent Workflow 테스트

```text
python -m src.agent_workflow
```

### 10.7 RAG v2 평가

```text
python -m src.rag_evaluator_v2
```

---

## 11. 현재 한계

- 위험 탐지는 현재 업무 규칙 기반으로 동작합니다.
- 현재 RAG 지식베이스는 포트폴리오용으로 구성한 61개의 가상 비용 규정을 사용합니다.
- RAG v2 평가 질의 1,037개는 자동 생성된 평가 데이터이므로 실제 운영 사용자 질의와 차이가 있을 수 있습니다.
- Vector Search에는 별도의 Reranking을 아직 적용하지 않았습니다.
- Keyword Search와 Vector Search를 함께 사용하는 Hybrid Search는 아직 적용하지 않았습니다.
- 현재 Agent Workflow는 Python 함수형 구조이며 실제 LangGraph 적용은 다음 단계에서 진행합니다.
- Langfuse 기반 Observability는 아직 적용하지 않았습니다.
- 사용자 인증 및 사용자별 검수 이력 관리 기능은 아직 구현하지 않았습니다.
- 실제 기업 ERP 또는 비용정산 시스템과는 아직 연동하지 않았습니다.

---

## 12. 향후 확장

- LangGraph 기반 State / Node / Conditional Edge Workflow 적용
- LLM 성공 / 실패 분기
- Timeout 및 Retry 처리
- 최종 실패 시 Template Fallback 강화
- Langfuse 기반 Observability 적용
- RAG 실패 사례 분석
- Reranking 적용 및 성능 비교
- Keyword + Vector Hybrid Search 비교
- pytest 기반 자동 테스트
- CI 파이프라인 구축
- 사용자별 검수 이력 관리
- 실제 사내 비용 규정 및 ERP 시스템 연동

---

## 13. RAG Retrieval Evaluation

### v1 — 소규모 Baseline 비교

평가 환경:

- Policies: 6
- Evaluation queries: 50
- Metric: Hit@3

결과:

- Keyword Search Hit@3: **15 / 50 = 30.0%**
- Vector Search Hit@3: **50 / 50 = 100.0%**

Keyword Search는 질문에 규정 키워드가 직접 포함되지 않는 경우 관련 규정을 놓치는 사례가 발생했습니다.

반면 Vector Search는 표현이 달라도 의미 기반으로 관련 규정을 검색할 수 있었습니다.

다만 v1은 전체 검색 후보가 6개이고 Top-3를 평가하는 소규모 실험이므로 검색 난이도가 낮다는 한계가 있습니다.

---

### v2 — 규정 및 평가셋 확장

검색 후보를 61개의 규정으로 확장했습니다.

각 규정별로 17개의 평가 질의를 구성하여 총 1,037개의 평가 질의를 생성했습니다.

평가 환경:

- Policies: **61**
- Evaluation queries: **1,037**
- Questions per policy: **17**

평가 데이터 검증 결과:

- 전체 데이터: **1,037**
- 빈 query: **0**
- 중복 query: **0**
- 평가 대상 규정: **61**
- 규정별 평가 질의: **17**

Vector Search 평가 결과:

- Hit@1: **946 / 1,037 = 91.2%**
- Hit@3: **1,025 / 1,037 = 98.8%**
- Hit@5: **1,033 / 1,037 = 99.6%**

### 결과 해석

Hit@1 91.2%는 1,037개의 평가 질의 중 946개에서 정답 규정을 검색 결과 1위로 반환했다는 의미입니다.

Hit@3 98.8%는 1,025개의 질의에서 정답 규정이 검색 결과 상위 3개 안에 포함되었다는 의미입니다.

Hit@5 99.6%는 1,033개의 질의에서 정답 규정이 상위 5개 안에 포함되었다는 의미입니다.

v1보다 규정 후보 수를 크게 늘렸음에도 높은 Top-K 검색 성공률을 유지했습니다.

다만 평가 질의는 자동 생성한 포트폴리오용 데이터이므로 이 결과를 실제 운영 환경의 검색 정확도와 동일하게 해석하지 않습니다.

향후 실제 사용자 질의 및 실패 사례를 추가하고 Reranking과 Hybrid Search를 적용하여 검색 성능을 추가 검증할 예정입니다.

---

## 14. 현재까지 구현한 RAG 구조

```text
사내 비용 규정
↓
Chunking
↓
Embedding
↓
PostgreSQL + pgVector
↓
Vector Search
↓
관련 규정 Top-K
↓
policy_evidence
↓
LLM Prompt
↓
draft_message
↓
Human Review
```

RAG를 단순히 연결하는 것에서 끝내지 않고 다음 과정을 통해 검색 성능을 검증했습니다.

```text
RAG 구현
↓
Keyword Baseline 구성
↓
평가셋 생성
↓
Hit@K 측정
↓
규정 및 평가 데이터 확장
↓
재평가
```

---

## 15. 프로젝트 핵심 정리

AuditFlow AI는 단순한 비용정산 CSV 조회 프로그램이 아니라 다음 과정을 연결한 **비용정산 검수 지원 시스템**입니다.

```text
업무 데이터
↓
업무 규칙 기반 위험 탐지
↓
Vector RAG 기반 규정 검색
↓
LLM 기반 보완 요청 초안
↓
Human Review
↓
PostgreSQL 저장
↓
검색 성능 평가
```

현재까지 FastAPI, PostgreSQL, pgVector, Gemini API를 실제 업무 흐름 안에서 연결했으며, 다음 단계에서는 LangGraph를 이용해 Workflow의 상태와 조건 분기, 실패 및 복구 경로를 명시적으로 관리하는 구조로 확장할 예정입니다.