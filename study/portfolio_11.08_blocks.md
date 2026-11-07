# 박람회 포트폴리오 블록 학습노트 (11.08 계획 기준)

> 블록마다 "꼭 알아야 할 개념 · 코드 · 명령어"를 누적 정리.
> 작업은 11.08 블록 순서(B01~B18)를 따르되 10.17 원본에서 빠진 항목을 같이 메운다.

---

## B01 — 시작점 고정 · 실행 환경 점검

### 꼭 알 개념

- **스키마(테이블 생성) ≠ 데이터 적재**
  - 테이블을 만드는 것(`CREATE TABLE`)과 그 안에 값을 넣는 것(`INSERT`)은 완전히 별개다.
  - RAG가 되려면 `policy_chunks` **테이블**도 있어야 하고, 그 안에 규정 **임베딩 데이터**도 있어야 한다. 둘 중 하나만 있으면 검색이 빈 결과.
- **Docker 볼륨(volume) = 컨테이너가 꺼져도 남는 데이터 저장소**
  - `auditflow_data` 볼륨에 DB 데이터가 쌓여 있어서, 지금 DB엔 policy_chunks 61행이 "이미" 있다.
  - 하지만 새 PC에서 새 볼륨으로 `docker compose up` 하면 그 데이터는 없다 → 그래서 `create_tables()`가 테이블 생성까지 책임져야 재현 가능.
- **pgVector 확장**: PostgreSQL이 기본으로 "벡터(숫자 배열)" 타입과 거리 연산(`<=>`)을 모른다. `CREATE EXTENSION vector`를 해야 `embedding vector` 컬럼과 코사인 거리 검색이 가능해진다.
- **멱등성(idempotent)**: `IF NOT EXISTS`를 붙이면 몇 번을 실행해도 결과가 같다(이미 있으면 그냥 넘어감). 그래서 서버가 켜질 때마다 `create_tables()`를 불러도 안전하다.

### 꼭 알 코드

```python
# src/database.py — create_tables() 안에 추가한 핵심
cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")   # 벡터 기능 켜기

cur.execute("""
    CREATE TABLE IF NOT EXISTS policy_chunks (
        id BIGSERIAL PRIMARY KEY,   -- 자동 증가 정수 PK
        text TEXT NOT NULL,         -- 규정 원문 조각
        source TEXT,                -- 출처
        embedding vector            -- 임베딩 벡터 (차원 미고정)
    );
""")
```

### 꼭 알 명령어

```bash
# 떠 있는 컨테이너 확인
docker ps --format "{{.Names}} | {{.Status}} | {{.Ports}}"

# 컨테이너 환경변수 확인 (DB 유저/DB명)
docker exec auditflow_db printenv POSTGRES_USER

# 컨테이너 안에서 psql로 DB 들여다보기
docker exec auditflow_db psql -U audituser -d auditflow -c "\dt"          # 테이블 목록
docker exec auditflow_db psql -U audituser -d auditflow -c "SELECT count(*) FROM policy_chunks;"
docker exec auditflow_db psql -U audituser -d auditflow -c "\d policy_chunks"   # 테이블 구조

# create_tables()만 따로 실행해 확인
python -c "from src.database import create_tables; create_tables(); print('OK')"

# 비통합 테스트 (CI와 동일 범위)
python -m pytest -m "not integration" -q
```

### 이 블록 결과물
- `src/database.py` `create_tables()`에 vector 확장 + policy_chunks 생성 추가 (10.17 Day3 Block1 항목)
- `docs/evidence/01_baseline.md`

---

## B02 — 기존 API 계약 · 복수 위험 재현

### 꼭 알 개념

- **복수 위험 구조 `risks[]`**: 비용 1건에 위험이 여러 개 걸릴 수 있다. 과거엔 `risk_type` 단일 컬럼이라 뒤 규칙이 앞 위험을 덮어썼다. 지금은 각 위험을 dict로 만들어 리스트에 쌓는다 → 0개/1개/여러 개 모두 표현 가능.
- **결정론적(deterministic) 규칙 vs 비결정적(LLM)**: 위험 "판정"은 규칙(if/임계값)으로 → 항상 같은 입력엔 같은 결과(재현 가능). LLM은 "문장 생성"에만 → 재현성이 떨어지므로 판정에 안 쓴다. 면접 단골 질문.
- **단건 `/audit` ≠ 배치 `/audit/batch`**:
  - `/audit`(단건) = 탐지 + RAG + LLM + DB 저장 (전체 파이프라인)
  - `/audit/batch` = 탐지만 (여러 행이 있어야 되는 중복/평균 이상치 규칙용), **RAG·LLM·DB 안 함**
  - → "batch가 1000건 탐지" ≠ "1000건 RAG+LLM 처리". 포트폴리오에서 반드시 구분.
- **대표 위험 단일 필드**: 응답의 top-level `risk_type` 등은 옛 구조 호환용 '대표 1개'. 실제 기준은 `risks[]`(JSONB).

### 꼭 알 코드

```python
# src/audit_rules.py — 위험을 '쌓는' 핵심 패턴
df["risks"] = [[] for _ in range(len(df))]   # 행마다 빈 리스트
def add_risk(mask, risk_type, risk_reason):  # 조건(mask)에 맞는 행에만 위험 추가
    for idx in df[mask].index:
        df.at[idx, "risks"].append({"risk_type": risk_type, "risk_reason": risk_reason})

# 규칙 예: 식대 20000 초과
meal_mask = (df["category"] == "식대") & (df["amount"] > 20000)
```

```python
# api/main.py — 위험별로 규정검색→초안을 따로 붙여 누적 (뭉치지 않게)
processed_risks = []
for risk in risks:
    evidence = find_similar_policies(risk["risk_reason"])   # 위험마다 따로 검색
    if not evidence:
        draft_source = "needs_review"                       # 근거 없으면 LLM 호출 X
    ...
    processed_risks.append(processed_risk)                  # 리스트에 누적
# 마지막에 risks JSONB로 '한 번' 저장
```

### 꼭 알 명령어

```bash
# src 패키지를 import하는 스크립트는 프로젝트 루트를 PYTHONPATH로
PYTHONPATH=. PYTHONIOENCODING=utf-8 python 스크립트.py
#   PYTHONPATH=.        → 'No module named src' 방지
#   PYTHONIOENCODING=utf-8 → 윈도우 콘솔 한글 깨짐(cp949) 방지
```

### 이 블록 결과물
- `docs/evidence/02_api_contract.md` (입출력 필드표, 복수위험 실제 출력, 단건/배치 차이표)

---

## B03~B05 — LangGraph 전체 위험 처리 + API 연결 결정

### 꼭 알 개념

- **LangGraph 핵심 3개어**
  - **State(상태)**: 노드 사이를 돌아다니는 "가방". 여기선 `AuditState`(expense, risks, processed_risks, run_id, error...).
  - **Node(노드)**: 한 가지 일만 하는 함수. State를 받아 **바뀔 부분만 dict로 return**하면 LangGraph가 State에 합쳐준다.
  - **Conditional Edge(조건 분기)**: 라우터 함수가 State를 보고 다음 노드 이름을 문자열로 반환 → 분기.
- **노드는 "바뀐 값만" 반환한다**: `return {"processed_risks": [...]}` 처럼 바뀐 키만 주면 됨. State 전체를 들고 수정해 반환할 필요 없음.
- **이번 버그의 교훈 (중요)**: 라우터(`route_after_retrieve`)가 `processed_risks`를 보고 분기하는데, 앞 노드(`retrieve_node`)가 그걸 안 채우면 → **분기가 항상 엉뚱한 길로 가서 뒤 노드가 통째로 안 돌아간다.** "노드가 다음 라우터가 보는 값을 반드시 써줘야 한다"가 핵심.
- **루프 안 덮어쓰기 함정**: `for risk in risks: x = f(risk)` 하면 `x`엔 **마지막 것만** 남는다. 위험마다 결과를 보존하려면 매번 `list.append(...)` 해야 한다.
- **상태값 언어 통일**: Graph 내부 `"미검토"` 같은 한글과 API `"unreviewed"` 영문을 섞으면 안 됨 → 한쪽으로 통일.
- **"코드가 있다" ≠ "실행 경로다"**: 모듈에 Graph가 있어도 API가 그걸 호출하지 않으면 사용자 입장에선 안 쓰이는 것. 포트폴리오엔 "독립 구현/API 미연동"으로 정직 표기.

### 꼭 알 코드

```python
# 위험마다 따로 검색해 누적 (덮어쓰기 X)
processed_risks = []
for risk in risks:
    similar = find_similar_policies(risk["risk_reason"], top_k=3)
    evidence = "\n\n".join(p[1] for p in similar) if similar else ""
    processed_risks.append({**risk, "policy_evidence": evidence})
return {"processed_risks": processed_risks}   # 바뀐 값만 반환

# 조건 분기 라우터 = State 보고 다음 노드 '이름'을 반환
def route_after_retrieve(state):
    return "generate" if state.get("processed_risks") else "review"

graph.add_conditional_edges("retrieve", route_after_retrieve,
    {"generate": "generate", "review": "review"})
```

```python
# Mock으로 외부 의존 없이 그래프 검증 (pytest)
from unittest.mock import patch
with patch("src.agent_workflow.find_similar_policies", side_effect=fake), \
     patch("src.agent_workflow.make_llm_draft", return_value=("초안","llm")) as m_llm, \
     patch("src.agent_workflow.save_audit_result", return_value=999) as m_save:
    result = workflow.invoke({"expense": EXPENSE})
m_llm.assert_called_once()                       # 근거 있는 위험에만 호출
assert m_save.call_args.kwargs["risks"] == ...   # 저장 인자 검사
```

- **patch 대상은 "사용되는 위치"**: `agent_workflow.py`가 `from src.policy_retriever import find_similar_policies`로 가져왔으면 `patch("src.agent_workflow.find_similar_policies")`를 patch (원본 모듈이 아니라 쓰는 쪽 이름).
- `side_effect`=함수 → 호출 인자에 따라 다른 값 반환 / `return_value`=항상 같은 값 / `assert_not_called()`, `call_count`, `call_args.kwargs`로 호출 검사.

### 꼭 알 명령어

```bash
PYTHONIOENCODING=utf-8 python -m pytest tests/test_workflow.py -v   # 특정 파일만
python -m pytest -m "not integration" -q                           # 전체 비통합
python -c "from src import agent_workflow as w; print(hasattr(w,'workflow'))"  # 컴파일 확인
```

### 이 블록 결과물
- `src/agent_workflow.py`: retrieve_node가 processed_risks 누적 / review_status 영문 통일 / 레거시 노드 3개 제거
- `tests/test_workflow.py` (Graph Mock 테스트 2개, PASS)
- `docs/evidence/03_architecture_decision.md` (결정 B + 수정 내역 + 증거)

---

## B06~B07 — 저장·검수 E2E + 실패 처리 테스트

### 꼭 알 개념

- **POST→GET→PATCH = Human-in-the-loop을 "기능으로" 증명**: 화면에 "사람이 검토"라고 쓰는 게 아니라, 실제 저장(POST)→조회(GET)→상태변경(PATCH)이 DB에 남는 걸로 증명.
- **pytest 마커(marker)로 테스트 분리**: `@pytest.mark.integration` 붙이면 "DB/외부 필요" 그룹. CI는 `-m "not integration"`로 그 그룹만 빼고 돌린다 → 외부 없이도 CI 초록.
- **"검색 결과 없음" ≠ "DB 고장" (면접 단골)**:
  - 검색 `[]` = **정상 업무 분기** → `needs_review`로 사람에게 넘김, 흐름 계속.
  - DB 저장 예외 = **시스템 장애** → 가짜 성공 id 돌려주면 안 됨 → 500으로 실패를 드러냄.
- **"거짓 성공" 금지**: 저장이 실패했는데 id를 반환하면, 호출한 쪽은 "저장됐다"고 믿는다. 실패는 실패로 보여야 한다.

### 꼭 알 코드

```python
# LLM 실패해도 업무 중단 X → 템플릿으로 (api/main.py)
if not policy_evidence or policy_evidence == "관련 규정 확인 필요":
    draft_source = "needs_review"          # 근거 없음 → LLM 호출 자체 안 함
else:
    try:
        draft_message, draft_source = make_llm_draft(x, policy_evidence)
    except Exception:
        draft_message, draft_source = make_draft(x)   # 템플릿 fallback

# 저장 실패를 '거짓 성공'으로 안 바꾸는 테스트
safe_client = TestClient(app, raise_server_exceptions=False)  # 500을 응답으로 받기
with patch("api.main.save_audit_result", side_effect=Exception("DB down")):
    r = safe_client.post("/audit", json=...)
assert r.status_code == 500          # 200/가짜 id 아님
```

- `TestClient(app, raise_server_exceptions=False)`: 이게 없으면 서버 예외가 테스트로 그대로 튀어 500 응답을 못 받는다.
- 500 응답 본문은 JSON이 아닐 수 있다 → `response.json()` 말고 `response.text`로 검사.

### 꼭 알 명령어

```bash
python -m pytest -m integration -v         # DB 필요한 통합 테스트만 (DB 켜고)
python -m pytest -m "not integration" -q   # CI와 동일 범위
python -m pytest 파일::테스트함수 -v        # 특정 테스트 하나만
```

### 이 블록 결과물
- `tests/test_audit.py`에 B07 실패 테스트 2개 추가(LLM 예외→template / DB 실패→거짓성공 금지)
- `docs/evidence/04_failure_matrix.md`
- integration 3개 실시간 DB PASS로 POST→GET→PATCH 확인(B06)

---

## B08 — 독립 평가 vs 회귀 테스트 (★면접 핵심)

### 꼭 알 개념

- **회귀(regression) 테스트 ≠ 정확도(accuracy) 평가** — 가장 중요.
  - **회귀**: "코드를 바꿔도 **예전과 같은 결과**가 나오나?" 정답(expected)을 **프로그램 출력에서 뽑아** 만든다. → 통과 = "안 깨졌다". 규칙에 버그가 있어도 정답에 같은 버그가 박혀서 통과함. 그래서 **정확도라고 부르면 안 됨**.
  - **정확도**: "코드가 **옳은가(규정 스펙대로인가)?**" 정답을 **사람이 규정 보고 직접** 매긴다. → 코드가 스펙에서 벗어나면 드러남.
- **지표 3개 (위험 "놓침"이 치명적이라 Accuracy 하나만 보면 안 됨)**:
  - **Precision(정밀도)** = TP / (TP+FP) : 탐지한 것 중 진짜 비율 (오탐 적나)
  - **Recall(재현율)** = TP / (TP+FN) : 진짜 중 잡아낸 비율 (**놓침 적나** — 비용검수에선 이게 중요)
  - **F1** = 2·P·R / (P+R) : 둘의 조화평균
  - TP=정답O·탐지O, FP=정답X·탐지O(오탐), FN=정답O·탐지X(놓침)
- **평가 단위**: `expense_id × risk_type` 쌍. 한 비용에 위험이 여러 개라 '건' 단위가 아니라 '위험 라벨' 단위로 센다.
- **경계값(boundary) 테스트**: `>20000`이면 20000은 통과·20001은 걸림. 경계 바로 양쪽을 넣어야 부등호(`>` vs `>=`) 실수를 잡는다.
- **배치 문맥**: 중복/평균 규칙은 여러 행이 있어야 계산됨 → 평가도 전체를 한 번에 `detect_risks()`에 넣어야 맞다.

### 꼭 알 코드

```python
# 집합 연산으로 TP/FP/FN (expense_id별 risk_type 집합 비교)
exp = expected[eid]          # 사람이 정한 정답 집합
act = actual[eid]            # detect_risks 결과 집합
tp += len(exp & act)         # 교집합 = 맞게 탐지
fp += len(act - exp)         # 실제만 = 오탐
fn += len(exp - act)         # 정답만 = 놓침

precision = tp / (tp + fp)
recall    = tp / (tp + fn)
f1        = 2*precision*recall / (precision + recall)
```

```python
# CSV에 JSON 리스트 넣기 — 콤마 포함되니 따옴표로 감싸고 "" 로 이스케이프
# expected_risks
# "[""식대한도 초과"", ""영수증누락""]"
import json
expected = set(json.loads(row["expected_risks"]))
```

### 꼭 알 명령어

```bash
PYTHONPATH=. PYTHONIOENCODING=utf-8 python scripts/evaluate_risks.py   # 독립 평가 실행
python -m pytest tests/test_regression_1000.py -v                     # 1000건 회귀(별개)
```

### 이 블록 결과물 / 실측
- `tests/data/independent_cases.csv`(12건), `independent_expected.csv`(사람 정의 정답)
- `scripts/evaluate_risks.py` (P/R/F1 계산)
- **결과: TP=10, FP=0, FN=0 → Precision/Recall/F1 = 1.000** (소표본·규정 임계값 기준)
- `docs/evidence/05_evaluation.md`

---

## B09 — 로컬 전체 점검 · CI · DAY1 마감

### 꼭 알 개념

- **CI가 초록이어도 DB·RAG 통합을 보장하지 않는다**: CI는 `-m "not integration"`만 돌리므로, 외부 DB/임베딩이 필요한 부분은 CI에서 검증되지 않음. "CI 통과 = 전체 동작"이 아님.
- **런타임 생성물은 git에 안 올린다**: `logs/*.jsonl` 같은 실행 로그, `__pycache__`는 `.gitignore` 대상. 지금 `logs/node_calls.jsonl`이 추적되고 있어 정리 필요.
- **커밋 전 점검 2종**:
  - `git diff --check`: 공백 오류·`<<<<<<<` 같은 **머지 충돌 표식**이 남았는지 검사.
  - `git status`: 올릴 것/빠질 것(비밀키·개인정보) 눈으로 확인 후 선택적으로 add.
- **증거는 "실제 만든 것만" 체크**: 계획서 체크박스는 '할 일'이지 '완료'가 아니다. 실행 로그/캡처가 있는 것만 완료로 표기.

### 꼭 알 명령어

```bash
git diff --check          # 공백/충돌표식 검사
git status --short        # 변경 요약
git log -1 --oneline      # 현재 커밋 SHA
python -m pytest -m "not integration" -q   # CI 동일 범위 집계
# (커밋은 사용자 승인 후) git add <경로> ; git commit -m "..."
```

### 이 블록 결과물
- `docs/evidence/09_day1_close.md` (마감표: 데모경로/SHA/테스트/CI/미완료/내일자료)
- DAY1 종료 게이트 4/4 달성, 전체 13 passed + integration 3 passed

### DAY1 요약
- 고친 것: create_tables(RAG 재현성), Graph 핵심버그(processed_risks), 실패 테스트·독립 평가 추가.
- 데모 경로 = `/audit`(API) 고정, LangGraph = 독립 구현(정직 표기).
- 남은 것: commit/push+CI, 로그 gitignore, DAY2(README/포트폴리오/데모/면접).

---

## B11~B12 — n8n 자동화 + 배포 준비

### 꼭 알 개념

- **세 역할 구분 (면접 단골)**: FastAPI=실제 검수 로직 API / LangGraph=그 로직의 상태·분기·실패경로 구현 / n8n=외부 업무도구(Google Sheets 등)와 API를 잇는 오케스트레이션.
- **n8n 자격증명은 워크플로 JSON 밖**: OAuth 토큰/API키는 n8n이 따로 저장 → JSON 커밋해도 비밀키는 안 올라감. 단 Google Sheets `documentId`(시트 식별자)는 JSON에 들어가니 공개 저장소면 확인.
- **필드 타입 매핑**: n8n HTTP body에서 `"amount": {{ $json.amount }}` 처럼 **따옴표 없이** 넣어야 숫자로 전송됨 → Pydantic `int` 통과. 따옴표로 감싸면 문자열 → `422`.
- **localhost vs 배포 URL**: `host.docker.internal:8000`은 로컬. 클라우드 배포하면 이 URL을 배포 주소로 바꿔야 E2E가 "클라우드 호출"이 됨.
- **Secret 분리 원칙**: `.env`(실제 값)는 `.gitignore`, `.env.example`(이름만) 추적. compose/배포는 환경변수로 주입. → 코드엔 비밀값 없음.
- **런타임 생성물은 git에서 빼기**: `logs/*.jsonl`이 추적되면 (1) 리포 지저분 (2) 로그에 실데이터 섞이면 유출. `git rm --cached` + `.gitignore`.

### 꼭 알 명령어

```bash
docker compose up -d                 # API+DB 한 번에
python -m uvicorn api.main:app --reload
git ls-files | grep env              # 추적되는 env 파일 확인
git show HEAD:.gitignore             # 커밋된 gitignore 보기
git rm --cached logs/*.jsonl         # (승인 후) 로그 추적 해제
```

### 이 블록 결과물
- `docs/evidence/06_n8n_status.md` (n8n 노드/매핑/비밀키/E2E 상태)
- `docs/evidence/07_runbook.md` (로컬 실행·환경변수·클라우드 배포 절차·정리 항목)
- 확인: `.env` gitignore OK, compose 하드코딩 없음 / ⚠️ logs 추적됨(정리 필요)

---
