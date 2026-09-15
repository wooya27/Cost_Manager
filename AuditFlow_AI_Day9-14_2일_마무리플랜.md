# AuditFlow AI — Day9~14 2일 마무리 플랜

> 현재 상태: **Day8 완료 / Day9부터 시작**  
> 기간: **오늘 + 내일, 2일**  
> 목표: Day9~14를 끝내고 **작동하는 AuditFlow AI MVP + Agent 구조 + 로그 + README**까지 완성  
> 핵심 원칙:
> - 오늘 = 초안 생성 + 사람 검수 화면 + Dashboard
> - 내일 = 다운로드 + Agent Workflow + 로그 + README
> - LangGraph가 오래 막히면 Python 함수형 workflow
> - Langfuse가 오래 막히면 로컬 JSONL 로그

---

# 0. 현재 위치

```text
✅ Day1~5   비용 데이터 + 위험 탐지
✅ Day6~8   규정 문서 → 검색 → 근거 연결

▶ 오늘
Day9       보완 요청 초안 생성
Day10      위험 건 상세 화면 + 검수 상태
Day11      Dashboard + Agent 역할 정리

▶ 내일
Day12      결과 다운로드 + 입력 검증
Day13      Agent Workflow
Day14      Observability + README

⬜ 이후
Day15      발표 / 캡처 / 최종 포트폴리오화
```

---

# 1. 2일 전체 일정

## 오늘 — Day9~11

| 블록 | 시간 | 작업 | 완료 기준 |
|---|---:|---|---|
| 1 | 50분 | Day9 템플릿 초안 | 위험 건마다 초안 생성 |
| 2 | 50분 | Day9 위험유형별 문구 + fallback | `draft_message`, `draft_source` 생성 |
| 3 | 50분 | Day10 상세 화면 | 위험 건 1개 선택 후 사유/근거/초안 표시 |
| 4 | 40분 | Day10 검수 상태 | 미검토/보완요청/승인 표시 |
| 5 | 50분 | Day11 Dashboard | 전체/위험/총액 + 위험유형 집계 |
| 6 | 30분 | Agent 역할 정리 + 복습 | 4개 Agent 역할 설명 가능 |

**순수 작업 약 4시간 30분**  
휴식 포함 약 **5~6시간**

## 내일 — Day12~14

| 블록 | 시간 | 작업 | 완료 기준 |
|---|---:|---|---|
| 1 | 50분 | Day12 CSV 다운로드 | 검수 결과 다운로드 가능 |
| 2 | 40분 | Day12 입력 검증 | 필수 컬럼 누락 시 앱이 죽지 않음 |
| 3 | 60분 | Day13 State + Node | workflow 구조 이해 및 파일 생성 |
| 4 | 60분 | Day13 1건 workflow 실행 | 근거 + 초안 반환 |
| 5 | 50분 | Day14 로컬 로그 | JSONL 로그 1줄 이상 |
| 6 | 60분 | Day14 README + 전체 점검 | GitHub 설명 가능한 상태 |

**순수 작업 약 5시간**  
휴식 포함 약 **5.5~6시간**

---

# DAY 1 — 오늘
# 목표: 초안 생성 → 사람 검수 → 전체 현황 확인

## 블록 1 — Day9 보완 요청 초안 생성
예상: 50분

### 📍 지금 무엇을 하는가

Day8까지는:

```text
위험 탐지
↓
규정 근거 연결
```

Day9에서는:

```text
위험 건
↓
위험 유형 확인
↓
규정 근거 확인
↓
보완 요청 문구 생성
```

### 입력 → 처리 → 출력

```text
입력
employee
amount
category
risk_type
policy_evidence

↓

처리
위험 유형별 안내 문구 선택
+
f-string 조립

↓

출력
draft_message
```

### 할 일

- [ ] `src/draft_generator.py` 확인
- [ ] `make_draft(row)` 함수 만들기
- [ ] row에서 필요한 값 꺼내기
- [ ] `risk_type` 확인
- [ ] 위험 유형별 문구 분기
- [ ] f-string으로 최종 메시지 조립
- [ ] `return draft_message`

### 완료 기준

위험 건 하나를 넣었을 때 보완 요청 문장이 나오면 성공.

---

## 블록 2 — Day9 위험유형별 문구 + fallback
예상: 50분

### 위험 유형별 문구 예시

```text
영수증 누락
→ 영수증 제출 요청

식대 한도 초과
→ 초과 사유 확인 요청

택시 사유 부족
→ 이용 사유 작성 요청
```

### fallback

예상하지 못한 상황에서도 앱이 멈추지 않도록 기본 답을 준비한다.

```text
알려진 risk_type
→ 해당 문구

모르는 risk_type
→ "추가 확인이 필요합니다."
```

### 할 일

- [ ] 7종 위험 유형 문구 분기
- [ ] 모르는 유형 기본 문구
- [ ] `draft_message` 생성
- [ ] `draft_source = "template"` 생성

### 완료 기준

```text
draft_message
draft_source
```

두 값이 생성되면 성공.

> LLM 연결은 시간이 남으면 한다. 오늘 핵심은 템플릿이 항상 작동하는 것.

---

## 블록 3 — Day10 위험 건 상세 화면
예상: 50분

### 흐름

```text
위험 건 목록
↓
한 건 선택
↓
신청자
금액
카테고리
위험 사유
규정 근거
보완 요청 초안
```

### 할 일

- [ ] `st.selectbox`로 위험 건 선택
- [ ] 선택한 행 가져오기
- [ ] 신청자 표시
- [ ] 금액 표시
- [ ] 카테고리 표시
- [ ] 위험 유형/사유 표시
- [ ] `policy_evidence` 표시
- [ ] `draft_message` 표시

### 완료 기준

위험 건 하나를 고르면 사유 + 규정 + 초안이 한 화면에 보이면 성공.

---

## 블록 4 — Day10 검수 상태
예상: 40분

### Human-in-the-loop

```text
AI 위험 탐지
↓
규정 근거
↓
보완 요청 초안
↓
👤 담당자 확인
↓
미검토 / 보완요청 / 승인
```

### 할 일

- [ ] `review_status` 추가
- [ ] 기본값 `미검토`
- [ ] 상세 화면에서 상태 확인
- [ ] 가능하면 상태 선택 UI

### 최소 상태

```text
미검토
보완요청
승인
```

---

## 블록 5 — Day11 Dashboard
예상: 50분

### 최소 지표 3개

```text
전체 신청 건수
위험 후보 건수
총 신청 금액
```

### 사용할 개념

```text
st.metric
value_counts()
st.bar_chart
```

### 할 일

- [ ] 전체 신청 건수
- [ ] 위험 건수
- [ ] 총 신청 금액
- [ ] 위험 유형별 `value_counts()`
- [ ] 가능하면 bar chart

### 완료 기준

숫자 카드 3개가 뜨면 최소 성공.

---

## 블록 6 — Day11 Agent 역할 정리
예상: 30분

| 현재 기능 | Agent 역할 |
|---|---|
| 위험 탐지 | AuditRuleAgent |
| 규정 검색 | PolicySearchAgent |
| 보완 요청 초안 | DraftMessageAgent |
| 담당자 검수 | ReviewSupportAgent |

```text
AuditRuleAgent
↓
PolicySearchAgent
↓
DraftMessageAgent
↓
ReviewSupportAgent
```

### 오늘 끝날 때 설명할 수 있어야 함

> 위험 탐지, 규정 검색, 초안 생성, 사람 검수 역할을 각각 분리했고, 이후 이 흐름을 Agent Workflow로 연결할 계획입니다.

---

# 오늘 END 체크

```text
[ ] Day9 템플릿 초안 생성
[ ] 위험 유형별 문구 분기
[ ] fallback 있음
[ ] draft_message 생성

[ ] 위험 건 하나 선택 가능
[ ] 사유 / 규정 / 초안 표시
[ ] review_status 표시

[ ] 전체 신청 건수
[ ] 위험 건수
[ ] 총액
[ ] 위험 유형별 집계

[ ] 4개 Agent 역할 설명 가능
```

---

# DAY 2 — 내일
# 목표: 업무 산출물 → Agent Workflow → 로그 → README

## 블록 1 — Day12 결과 CSV 다운로드
예상: 50분

### 흐름

```text
검수 결과
↓
CSV 변환
↓
다운로드
```

### 할 일

- [ ] 최종 결과 DataFrame 확인
- [ ] `to_csv()`
- [ ] `st.download_button`
- [ ] 실제 파일 열어 확인

### 완료 기준

검수 결과 CSV가 실제로 내려받아지면 성공.

---

## 블록 2 — Day12 입력 검증
예상: 40분

### 흐름

```text
CSV 업로드
↓
필수 컬럼 검사
↓
누락 있음?
↓
오류 메시지
```

### 할 일

- [ ] 필수 컬럼 목록
- [ ] 누락 컬럼 확인
- [ ] 사용자에게 오류 메시지
- [ ] 앱이 멈추지 않는지 확인

---

## 블록 3 — Day13 State + Node
예상: 60분

### 지금 반드시 이해할 것

**State** = 현재 작업 정보를 들고 다니는 가방

```text
risk_type
risk_reason
policy_evidence
draft_message
```

**Node** = 한 단계의 작업

```text
위험 확인
규정 검색
초안 생성
```

**Graph** = Node가 움직이는 순서

```text
Node A
↓
Node B
↓
Node C
```

### 할 일

- [ ] `src/agent_workflow.py`
- [ ] State 구조 정하기
- [ ] 위험 확인 node
- [ ] 규정 검색 node
- [ ] 초안 생성 node

---

## 블록 4 — Day13 workflow 실행
예상: 60분

### 목표

**위험 건 1개만 workflow에 넣는다.**

```text
위험 건 1개
↓
위험 확인
↓
규정 검색
↓
초안 생성
↓
최종 결과
```

### 완료 기준

최종 결과에

```text
policy_evidence
draft_message
```

가 있으면 성공.

### 막혔을 때

LangGraph 실제 문법이 30분 이상 막히면 Python 함수형 workflow로 대체.

---

## 블록 5 — Day14 Observability / 로그
예상: 50분

### 목표 파일

```text
logs/
└── llm_calls.jsonl
```

### 기록할 내용

```text
timestamp
risk_type
risk_reason
has_policy_evidence
prompt
draft_message
draft_source
llm_success
fallback_used
error_message
```

### 할 일

- [ ] `src/observability.py`
- [ ] logs 폴더 생성
- [ ] 로그 함수
- [ ] 성공/실패 기록
- [ ] fallback 기록
- [ ] JSONL 파일 확인

### 완료 기준

로그 파일 안에 최소 1줄 존재.

---

## 블록 6 — Day14 README + 전체 점검
예상: 60분

### README 최소 구조

```md
# AuditFlow AI

## 프로젝트 소개
## 해결하려는 업무 문제
## 전체 흐름
## 주요 기능
## 기술 스택
## Agent 구조
## 안전 설계
## 실행 방법
## 한계
## 향후 확장
```

### 전체 프로젝트 구조

```text
사용자
↓
비용 CSV 업로드
↓
Pandas 데이터 처리
↓
AuditRuleAgent
위험 후보 탐지
↓
PolicySearchAgent
규정 근거 검색
↓
DraftMessageAgent
보완 요청 초안
↓
ReviewSupportAgent
사람 검수
↓
Dashboard
↓
CSV 결과 다운로드

+
Agent Workflow
+
Observability Log
```

---

# 2일 시간 부족 시 우선순위

## 무조건 완료

```text
1. Day9 템플릿 초안
2. Day10 상세 화면
3. Day12 CSV 다운로드
4. Day13 workflow 1건
5. Day14 로컬 로그
6. README
```

## 줄여도 됨

```text
LLM 실제 연결
Dashboard 차트
review_status 고도화
실제 LangGraph
실제 Langfuse
테스트 여러 개
UI 디자인
```

---

# 2일 후 최종 설명 문장

> AuditFlow AI는 비용정산 CSV에서 위험 후보를 자동 탐지하고, 사내 비용 규정에서 관련 근거를 찾아 보완 요청 초안을 제공하는 업무 검수 어시스턴트입니다. 위험 탐지, 규정 검색, 초안 생성, 사람 검수 역할을 분리하고 Agent Workflow 관점에서 단계별로 연결했습니다. LLM은 규정 근거가 있는 초안 생성에 제한적으로 사용하며 실패 시 템플릿으로 fallback하고, 실행 로그를 남겨 품질 개선이 가능하도록 설계했습니다.

---

# 이해 확인

## 오늘 끝나고

1. Day9에서 초안 생성 기능은 왜 필요한가?
2. fallback은 왜 필요한가?
3. Human-in-the-loop는 왜 필요한가?
4. Agent 역할을 왜 나눴는가?

## 내일 끝나고

1. State란 무엇인가?
2. Node란 무엇인가?
3. Agent Workflow를 왜 사용하는가?
4. Observability를 왜 남기는가?
5. 결과 CSV는 실무에서 왜 필요한가?
