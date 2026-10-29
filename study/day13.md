# Day 13 — LangGraph StateGraph·노드·조건부 엣지 (심사 워크플로 재구성)

> 2026-10-29. `src/agent_workflow.py`에서 심사 과정을 LangGraph `StateGraph`로 다시 짜며 잡은 개념.
> 핵심 한 줄: **"LangGraph는 코드를 위→아래로 실행하는 게 아니라, 내가 선언한 '엣지(연결)' 관계대로 돈다. 그래서 add_node/add_edge를 쓴 순서는 상관없고, 대신 모든 노드가 '나가는 길(출구 엣지)'을 가져야 한다."**

---

## 1. StateGraph가 뭔가 (큰 그림)

### 개념
- **state(상태 가방)**: 작업 정보를 담아 노드 사이를 넘어다니는 dict. 여기선 `AuditState`(TypedDict)로 어떤 칸이 있는지 미리 정의했다. (expense, risks, policy_evidence, draft_message, draft_source, review_status, error ...)
- **node(노드)**: 자기 한 가지 일만 하는 함수. state를 받아서 **바뀐 칸만** dict로 리턴한다.
  ```python
  def audit_node(state: AuditState):
      ...
      return {"risks": risks}   # 바뀐 칸만 돌려주면 LangGraph가 state에 합쳐준다
  ```
- **edge(엣지)**: 노드와 노드를 잇는 화살표. "이 노드 끝나면 저 노드로 가라".
- **graph.compile()**: 선언한 노드+엣지를 실제로 돌릴 수 있는 `workflow`로 굳히는 단계.

### 오늘 만든 노드 7개
`audit`(위험 탐지) → `retrieve`(규정 검색) → `generate`(LLM 초안) → `retry`(재시도) → `fallback`(규칙기반 초안) → `review`(검토 게이트) → `save`(DB 저장)

---

## 2. 제일 중요 — 선언 "순서"는 상관없다

### 오늘 헷갈렸던 것
`graph.add_edge(START, "audit")` 아래부터 "배치 순서가 꼬인 것 같다"고 느꼈는데,
**그게 진짜 문제가 아니었다.**

### 개념 (왜 순서 무관인가)
파이썬 함수는 위→아래로 실행되지만, `add_node`/`add_edge`는 그냥
**"이런 노드가 있다 / 이런 연결이 있다"를 그래프에 등록만** 하는 거다.
실제 실행 흐름은 `workflow.invoke()` 할 때 **등록된 엣지 관계를 따라** 정해진다.

그래서 `add_edge(START, "audit")`를 코드 맨 위에 쓰든 맨 아래에 쓰든 결과가 똑같다.
(1번 개념 day12의 "위→아래 실행"과는 다른 세계 — 거긴 일반 파이썬, 여긴 그래프 선언이다.)

### 비유
지하철 **노선도를 그리는 것**과 **열차가 달리는 것**은 별개다.
노선도에 역/선로를 어떤 순서로 그려넣든, 열차는 "연결된 선로"를 따라 달린다.

---

## 3. 진짜 문제 — "나가는 길(출구 엣지)"이 없는 노드

### 개념
그래프가 제대로 돌려면 **모든 노드에 나가는 엣지가 있어야** 한다.
출구가 없는 노드에 도착하면 더 갈 데가 없어서 거기서 멈추거나 에러가 난다.
흐름이 최종적으로 끝나는 지점은 `END`로 이어줘야 한다.

### 오늘 점검 결과 (출구 체크)
| 노드 | 나가는 엣지 | 상태 |
|---|---|---|
| audit | → retrieve / save (조건부) | ✅ |
| retrieve | → generate / review (조건부) | ✅ |
| generate | → retry / review (조건부) | ✅ |
| retry | → fallback / review (조건부) | ✅ |
| fallback | ❓ 없음 | ⛔ 연결 필요 |
| review | ❓ 없음 | ⛔ 연결 필요 |
| save | ❓ 없음 (→ END) | ⛔ 연결 필요 |

→ `fallback`, `review`, `save`에서 나가는 길이 비어 있다. 이게 "순서가 꼬인 느낌"의 진짜 정체였다.
**(다음에 직접 연결할 숙제. 각 노드가 플로우상 다음에 어디로 가야 하는지 생각 → `add_edge`로 잇고, 마지막은 `END`로.)**

---

## 4. 조건부 엣지 (`add_conditional_edges`)

### 개념
그냥 `add_edge(A, B)`는 "A 끝나면 무조건 B". 하지만 **상태에 따라 갈림길**이 필요할 때가 있다.
그때 쓰는 게 `add_conditional_edges`.

```python
graph.add_conditional_edges(
    "audit",             # ① 이 노드가 끝나면
    route_after_audit,   # ② 이 함수를 불러서 "다음 어디?"를 결정
    {                    # ③ 함수가 리턴한 문자열 → 실제 갈 노드
        "retrieve": "retrieve",
        "save": "save"
    }
)
```

### 라우팅 함수의 규칙
- state를 받아서 **문자열(갈림길 이름)을 리턴**한다. (노드처럼 dict 리턴 X)
```python
def route_after_audit(state: AuditState):
    risks = state.get("risks", [])
    if risks:
        return "retrieve"   # 위험 있으면 규정 검색으로
    return "save"           # 없으면 바로 저장으로
```
- 오늘 만든 라우팅 함수 4개:
  - `route_after_audit`: 위험 있으면 retrieve, 없으면 save
  - `route_after_retrieve`: 규정 근거 있으면 generate, 없으면 review
  - `route_after_generate`: error 있으면 retry, 없으면 review
  - `route_after_retry`: error 있으면 fallback, 없으면 review

---

## 5. 아직 헷갈리는 것 / 다음에 할 것
- `fallback`, `review`, `save`의 출구 엣지 연결 (특히 `save → END`). ← **다음 세션 첫 숙제**
- `generate_node` 안의 `raise Exception("1차 LLM 테스트 실패")`는 지금 **일부러 실패시키는 테스트용** 코드. retry/fallback 경로를 확인하려고 넣은 것 — 실제 동작 땐 빼거나 조건 걸어야 함.

## 6. 30초 설명 (안 보고 말해보기)
- LangGraph StateGraph는 ______ 를 ______ 사이로 넘기며 일을 시킨다.
- add_node/add_edge의 선언 순서는 ______ (상관있다/없다). 흐름은 ______ 대로 돈다.
- 모든 노드는 ______ 가 있어야 하고, 마지막은 ______ 로 간다.
- 조건에 따라 갈림길을 나눌 땐 ______ 를 쓰고, 그 라우팅 함수는 ______ 을 리턴한다.

<!-- 답: state(상태 가방)/노드 · 없다/선언한 엣지 관계 · 나가는 엣지(출구)/END · add_conditional_edges/문자열(다음 노드 이름) -->

## 7. 한 줄 복습
1. 그래프는 코드 순서가 아니라 ( ) 대로 돈다.
2. 출구 없는 노드는 ( ). 흐름의 끝은 ( )로 잇는다.
3. 조건 분기는 ( ), 라우팅 함수는 ( )를 리턴한다.

<!-- 답: 1.선언한 엣지 관계 2.멈추거나 에러 / END 3.add_conditional_edges / 문자열(다음 노드 키) -->
