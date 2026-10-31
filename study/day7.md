# Day 7 — 다른 파일 함수 가져오기 + 각 행에 함수 돌려 새 컬럼 만들기

> 2026-09-12. `app.py`에서 `policy_retriever.py`의 함수를 가져다 쓰고, 표(df)의 각 행마다 규정 검색을 돌려 `policy_evidence` 컬럼을 만든 날.

---

## 1. `from ... import ...` 구조와 `as` 별칭

### 개념
`from ... import ...`는 두 칸으로 나뉜다.
```
from  <어느 파일에서>       import  <그 안에 든 뭘>
from  src.policy_retriever  import  find_policy_evidence, chunks
```
- `from` 뒤 = **모듈(파일 위치)**. `src/policy_retriever.py` → `src.policy_retriever` (슬래시 아니고 점, `.py` 안 붙임)
- `import` 뒤 = **그 파일 안에 실제로 만들어진 이름들**. 콤마로 여러 개 나열.

### 이유 (내가 틀렸던 3가지)
1. `import A as B` → `as`는 **별칭(다른 이름)**. `find_policy_evidence as risk_type`는 "함수를 risk_type이라 부르겠다"가 돼서 원래 이름이 사라짐. 두 이름 나란히 가져올 땐 `as` 빼고 콤마만.
2. `from find_policy_evidence import ...` → `from` 뒤엔 **파일**이 와야 하는데 함수 이름을 넣음. 두 칸이 서로 바뀐 것.
3. `import risk_type` → `risk_type`은 그 파일에 없는 이름. 함수 정의 `def find_policy_evidence(risk_type, chunks)`의 **매개변수(괄호 안 입력칸)**일 뿐, 파일 밖으로 꺼낼 수 있는 물건이 아님 → ImportError.

### 정답
```python
from src.policy_retriever import find_policy_evidence, chunks
```
import 할 수 있는 건 그 파일에 진짜 정의된 것들(함수, 변수 `chunks`, 딕셔너리 `RISK_KEYWORDS`)뿐.

**한 줄 정리**: from=어느 파일 / import=그 안의 실제 이름들 / as=별칭 / 함수 매개변수는 import 대상 아님.

---

## 2. for문으로 각 행에 함수 돌려 새 컬럼 만들기

### 개념 (패턴)
"빈 리스트 → for로 하나씩 꺼내 → 함수 돌려 결과 얻어 → append → 루프 끝나고 컬럼에 넣기"
```python
risk_explanation = []                       # ① 빈 리스트 준비
for rt in df["risk_type"]:                  # ② risk_type 컬럼 값을 한 개씩 rt로 꺼냄
    ev = find_policy_evidence(rt, chunks)   # ③ rt를 함수에 넣고, 결과는 새 변수 ev에
    risk_explanation.append(ev)             # ④ 리스트에 ev 한 개만 담음
df["policy_evidence"] = risk_explanation    # ⑤ for 밖에서, 다 모은 리스트를 새 컬럼으로
```

### 이유 (내가 틀렸던 3가지 — 진짜 복습 포인트)
1. **함수에 뭘 넣나** — `find_policy_evidence(RISK_KEYWORDS, chunks)`로 딕셔너리 전체를 넣었음 ❌.
   함수가 원하는 첫 인자는 "위험유형 하나" = for가 꺼내준 `rt` → `find_policy_evidence(rt, chunks)`.
   (RISK_KEYWORDS는 함수가 내부에서 알아서 씀. 내가 넘길 게 아님.)
2. **결과를 어디 담나** — `rt = 함수(...)`로 **루프 변수 rt를 덮어씀** ❌. 원본 값이 사라짐. 결과는 **새 변수 ev**에.
3. **append는 한 개만** — `.append(A, B)`는 에러 ❌. append()는 인자 딱 1개.
4. **들여쓰기**: `df["policy_evidence"] = ...`를 for 안에 두면 매 반복마다 실행됨. 리스트 다 모은 뒤 한 번만 → **for 밖**(for보다 왼쪽)으로.

**관련**: 이건 `detect_risks`가 컬럼 만든 것과 같은 계열. 나중에 Day9 `make_draft`(값 2개)도 같은 패턴.
