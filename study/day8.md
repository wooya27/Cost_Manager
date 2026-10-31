# Day 8 — 미니 RAG 개념 정리 (단어 구분 + 두 실패 경우)

> 2026-09-13. 규정 검색(mini RAG) 파이프라인에서 헷갈리던 단어 4개를 정리하고, `find_policy_evidence`가 "관련 규정 확인 필요"를 돌려주는 두 가지 경우를 구분한 날.

---

## 1. 핵심 4단어 (risk_type / RISK_KEYWORDS / keyword / policy_evidence)

### 개념 — "흐름" 순서로 놓으면 안 헷갈린다
위반 하나가 규정 근거를 찾아가는 파이프라인:

`risk_type` → (RISK_KEYWORDS로 변환) → `keyword` → (policy.txt에서 검색) → `policy_evidence`

| 단어 | 정체 | 어디 있나 | 예시 |
|---|---|---|---|
| `risk_type` | **지출위반 유형**. detect_risks가 각 행에 붙인 위험 이름 | df 컬럼(값) | `"식대한도 초과"` |
| `RISK_KEYWORDS` | **변환표(딕셔너리)**. 위반유형→검색키워드. 손으로 씀 | policy_retriever.py | `{"식대한도 초과":"식대", ...}` |
| `keyword` | **검색어 한 개**. 표에서 꺼낸 값 | 함수 안 변수 | `"식대"` |
| `policy_evidence` | **규정 근거(결과)**. keyword로 찾아낸 규정 문단 | df 새 컬럼 | `"[식대 규정] 일반 식대는..."` |

### 이유 (헷갈린 지점)
- `RISK_KEYWORDS`(전체 표) ≠ `keyword`(표에서 꺼낸 값 1개). `keyword = RISK_KEYWORDS.get(risk_type)`.
- `risk_type`(입력=무슨 위반?)과 `policy_evidence`(출력=무슨 규정 근거?)는 **파이프라인의 양 끝**.

---

## 2. find_policy_evidence의 두 실패 경우

### 개념
실패가 두 종류인데 지금 코드는 **똑같은 문자열**("관련 규정 확인 필요")을 돌려줘서 화면에선 구분이 안 됨.
```python
keyword = RISK_KEYWORDS.get(risk_type)
if keyword is None:
    return "관련 규정 확인 필요"   # ← 경우 A
for chunk in chunks:
    if keyword in chunk:
        return chunk
return "관련 규정 확인 필요"       # ← 경우 B
```
- **경우 A = 매핑표에 아예 없음.** `.get(risk_type)`가 None → 검색어조차 못 만듦.
- **경우 B = 검색어는 만들었는데 규정 문서에 그 글자가 없음.** `if keyword in chunk`가 한 번도 안 걸림.

### 이유 — "키워드 뽑았는데 규정 없을 수 있나?" → 있다
키워드(`RISK_KEYWORDS`, 내가 손으로 씀)와 규정(`policy.txt`, 별도 파일)이 **따로 관리**되기 때문. 어긋나면 경우 B:
1. **철자 불일치**: 딕셔너리엔 `"택시비"`인데 policy.txt엔 "택시 요금"이라 쓰면 못 찾음.
2. **문단 자체가 없음**: 매핑만 추가하고 policy.txt에 그 문단을 안 쓰면 keyword는 뽑히지만 어느 chunk에도 없음.

### 그래서 매핑 추가 순서가 중요
① policy.txt에 규정 문단 먼저 → ② RISK_KEYWORDS에 매핑 추가. (반대로 하면 경우 B로 빠짐)
- 참고: 현재 데이터 기준 4개 키워드(식대·택시비·영수증·중복)는 전부 policy.txt에 있어 **경우 B는 아직 실제로 발생 안 함**. 지금 "확인 필요"는 전부 경우 A.
