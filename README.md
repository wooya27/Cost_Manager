# Cost_Manager 

## 1. 프로젝트 소개

AuditFlow AI는 비용정산 CSV를 업로드하면
위험 가능성이 있는 비용 건을 자동으로 탐지하고,
관련 사내 규정을 찾아 보완 요청 초안을 제공하는
비용정산 1차 검수 어시스턴트입니다.

AI 또는 자동화 결과를 바로 최종 결정으로 사용하지 않고,
담당자가 마지막으로 확인하는 Human-in-the-loop 구조로 설계했습니다.

## 2. 해결하려는 업무 문제

비용정산 업무에서는 담당자가 많은 신청 건을 직접 확인하면서
영수증 누락, 중복 신청, 한도 초과 등의 위험 건을 찾아야 합니다.

또한 문제가 발견되면 관련 사내 규정을 다시 확인하고,
신청자에게 보낼 보완 요청 문구도 작성해야 합니다.

AuditFlow AI는 이러한 반복적인 1차 검수 작업을 자동화하여
담당자가 위험 건과 근거를 빠르게 확인할 수 있도록 돕는 것을 목표로 합니다.


## 3. 전체 흐름

### 실제 Streamlit 앱 전체 업무 흐름

AuditFlow AI의 기본 처리 흐름은 다음과 같습니다.

```text
사용자 비용 CSV 업로드
↓
Pandas DataFrame으로 변환
↓
위험 후보 탐지
↓
관련 사내 규정 검색
↓
보완 요청 초안 생성
↓
담당자 검수
↓
Dashboard 확인
↓
검수 결과 CSV 다운로드
```

### Day13에 만든 Agent Workflow 구조를 보여주는 흐름

추가로 위험 건 1건을 대상으로
Python 함수형 Agent Workflow를 구성했습니다.

```text
위험 건 1건
↓
State 생성
↓
위험 확인 Node
↓
규정 검색 Node
↓
초안 생성 Node
↓
최종 State 반환
↓
JSONL 실행 로그 기록
```


## 4. 주요 기능

### 1 비용정산 CSV 업로드
Streamlit을 통해 비용정산 CSV 파일을 업로드하고
Pandas DataFrame으로 변환합니다.

### 2 위험 후보 자동 탐지
비용 데이터를 검사하여 위험 가능성이 있는 건을 탐지합니다.

예:
- 영수증 누락
- 중복 신청 의심
- 이상 비용 후보
- 식대 한도 초과
- 택시비 사유 부족
- 사무용품 추가 승인

### 3 관련 규정 근거 검색
탐지된 risk_type에 따라 검색 키워드를 정하고,
policy.txt에서 관련 규정 문단을 찾습니다.

규정을 찾지 못한 경우
"관련 규정 확인 필요"를 반환합니다.

### 4 보완 요청 초안 생성
직원, 금액, 카테고리, 위험 유형 등의 정보를 이용해
신청자에게 전달할 보완 요청 초안을 생성합니다.

현재 MVP에서는 규칙 기반 템플릿 방식을 사용합니다.

### 5 사람 검수 지원
위험 사유, 규정 근거, 보완 요청 초안을
담당자가 화면에서 확인할 수 있도록 제공합니다.

검수 상태는 review_status로 관리합니다.

### 6 Dashboard
전체 신청 건수, 위험 건수, 총 신청 금액을
한 화면에서 확인할 수 있습니다.

### 7 검수 결과 CSV 다운로드
위험 탐지 결과, 규정 근거, 초안, 검수 상태가 포함된
최종 DataFrame을 CSV 파일로 다운로드할 수 있습니다.

### 8 Agent Workflow
위험 건 1건을 State에 담아
위험 확인 → 규정 검색 → 초안 생성 순서로 처리합니다.

### 9 실행 로그
Workflow 실행 결과를 JSONL 형식으로 기록하여
위험 유형, 초안 출처, 오류 여부 등을 확인할 수 있습니다.


## 5. Agent 구조

AuditFlow AI는 하나의 기능이 모든 작업을 처리하지 않고,
업무 역할을 다음과 같이 분리했습니다.

### AuditRuleAgent
비용 데이터를 검사하여 위험 후보를 탐지합니다.

예:
- 영수증 누락
- 중복 신청 의심
- 식대 한도 초과
- 택시비 사유 부족

### PolicySearchAgent
탐지된 위험 유형을 기준으로
관련 사내 규정 근거를 검색합니다.

### DraftMessageAgent
비용 정보와 위험 유형을 바탕으로
신청자에게 보낼 보완 요청 초안을 생성합니다.

### ReviewSupportAgent
위험 사유, 규정 근거, 보완 요청 초안을
담당자가 직접 확인할 수 있도록 지원합니다.

역할을 분리한 이유는
각 기능의 책임을 명확하게 하고,
문제가 발생했을 때 어느 단계에서 문제가 생겼는지
확인하기 쉽게 하기 위해서입니다.

또한 이후 Agent Workflow로
각 역할을 단계별로 연결하기 쉽게 만들 수 있습니다.


## 6. Agent Workflow

위험 건 1건을 대상으로 Python 함수형 Workflow를 구성했습니다.

처리 순서는 다음과 같습니다.

```text
위험 건 1건
↓
State 생성
↓
위험 확인 Node
↓
규정 검색 Node
↓
초안 생성 Node
↓
최종 State 반환
```

State는 Workflow가 처리 중인 한 건의 정보를 담는 작업 상태입니다.

각 Node는 State를 받아 하나의 작업을 수행하고,
처리 결과를 다시 State에 추가한 뒤 다음 Node로 전달합니다.

예:

```text
risk_type
↓
policy_search_node
↓
policy_evidence 추가
↓
draft_message_node
↓
draft_message / draft_source 추가
```

현재 MVP에서는 실제 LangGraph 대신
Python 함수형 Workflow로 구현했습니다.

## 7. 프로젝트 구조

```text
Cost_Manager/
│
├── app.py
│   └── Streamlit 화면과 전체 기능 연결
│
├── policy.txt
│   └── 비용정산 사내 규정 문서
│
├── sample_expenses.csv
│   └── 테스트용 비용정산 데이터
│
├── src/
│   ├── audit_rules.py
│   │   └── 위험 후보 탐지 규칙
│   │
│   ├── policy_retriever.py
│   │   └── 위험 유형에 맞는 규정 근거 검색
│   │
│   ├── draft_generator.py
│   │   └── 보완 요청 초안 생성
│   │
│   ├── agent_workflow.py
│   │   └── State / Node / Workflow 처리
│   │
│   └── observability.py
│       └── Workflow 실행 로그 기록
│
└── logs/
    └── llm_calls.jsonl
        └── 실행 이력 저장

```


### 왜 파일을 나눴어?

만약 모든 기능을 `app.py` 하나에 다 넣으면:

```text
위험탐지
규정검색
초안생성
Workflow
로그
UI

app.py
= 화면/전체 연결

audit_rules.py
= 위험 판단

policy_retriever.py
= 규정 검색

draft_generator.py
= 초안 생성

agent_workflow.py
= 처리 순서 연결

observability.py
= 실행 기록
```


## 8. 기술 스택

- Python
  - 프로젝트의 주요 로직 구현

- Pandas
  - CSV 데이터를 DataFrame으로 불러오고
    위험 탐지, 필터링, 집계 등에 사용

- Streamlit
  - CSV 업로드, 결과 표, Dashboard,
    상세 검수 화면, 다운로드 UI 구현

- CSV
  - 비용정산 입력 데이터와 검수 결과 파일 형식

- JSONL
  - Workflow 실행 로그를 한 줄씩 저장

- Git / GitHub
  - 소스 코드 버전 관리와 프로젝트 관리


## 9. 안전 설계

AuditFlow AI는 자동 탐지 결과를
바로 최종 판단으로 사용하지 않도록 설계했습니다.

처리 흐름은 다음과 같습니다.

```text
위험 탐지
↓
규정 근거 확인
↓
보완 요청 초안 생성
↓
담당자 검수
```

즉, 시스템은 위험 후보와 규정 근거,
보완 요청 초안을 제공하지만
최종 판단은 사람이 수행합니다.

이러한 Human-in-the-loop 구조를 통해
자동화 결과를 사람이 다시 확인할 수 있도록 했습니다.

또한 관련 규정을 찾지 못한 경우
임의의 근거를 만들어내지 않고
"관련 규정 확인 필요"를 반환하도록 했습니다.

```text
Human-in-the-loop
= 자동화 중간에 사람이 최종 확인하는 구조

fallback
= 원하는 결과를 못 만들었을 때
  대신 사용할 안전한 기본 처리


규정 찾음
→ 근거 제공

규정 못 찾음
→ "관련 규정 확인 필요"
→ 사람이 확인
```



## 10. 실행 방법

### 1. 프로젝트 폴더로 이동

터미널에서 Cost_Manager 프로젝트 폴더로 이동합니다.

### 2. 필요한 패키지 설치

```bash
pip install -r requirements.txt
```
### 3. Streamlit 앱 실행

```bash
streamlit run app.py
```

### 4. 비용 데이터 업로드

실행된 Streamlit 화면에서
sample_expenses.csv 또는 동일한 형식의 비용정산 CSV를 업로드합니다.

업로드 후 다음 결과를 확인할 수 있습니다.

위험 후보 탐지 결과
위험 사유
관련 규정 근거
보완 요청 초안
검수 상태
Dashboard
검수 결과 CSV 다운로드

### 5. Agent Workflow 테스트

터미널에서 다음 명령어를 실행합니다.

```bash
python -m src.agent_workflow
```


### 🧒 여기서 명령어 역할만 구분하자

```text
pip install -r requirements.txt
= 필요한 도구들을 설치

streamlit run app.py
= 실제 웹 화면 실행

python -m src.agent_workflow
= Agent Workflow만 따로 테스트
```
## 11. 현재 한계

- 위험 탐지는 현재 규칙 기반으로 동작합니다.
- 규정 검색은 키워드 기반으로 동작합니다.
- 보완 요청 초안은 현재 템플릿 방식으로 생성합니다.
- 실제 LLM API는 아직 연결하지 않았습니다.
- 실제 LangGraph 기반 Workflow는 아직 적용하지 않았습니다.
- 실제 Langfuse 기반 Observability는 아직 적용하지 않았습니다.
- 검수 상태는 MVP 수준으로 관리되며, 사용자별 저장 기능은 아직 없습니다.


## 12. 향후 확장

- LangGraph 기반 Agent Workflow 적용
- Langfuse 기반 Observability 적용
- LLM을 활용한 보완 요청 초안 생성
- Vector DB를 활용한 규정 검색 고도화
- 검수 상태 및 사용자별 이력 저장
- 테스트 자동화
- 실제 사내 비용 규정 및 업무 시스템 연동