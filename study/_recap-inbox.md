# 복습 인박스 (daily-recap 때 study/ 문서로 옮기고 여기선 지움)

## [2026-09-12] from ... import ... 구조와 as 별칭

- Q(내 질문): `app.py`에서 다른 파일(`policy_retriever.py`)에 만든 함수랑 변수를 어떻게 가져와? 자꾸 오류남.

- A(핵심 답변):
  **개념**: `from ... import ...` 문장은 두 칸으로 나뉜다.
  ```
  from  <어느 파일에서>       import  <그 안에 든 뭘>
  from  src.policy_retriever  import  find_policy_evidence, chunks
  ```
  - `from` 뒤 = **모듈(파일 위치)**. `src/policy_retriever.py` → `src.policy_retriever` (슬래시 아니고 점, .py 안 붙임)
  - `import` 뒤 = **그 파일 안에 실제로 만들어진 이름들**. 콤마로 여러 개 나열.

  **이유(왜 오류가 났나) — 내가 한 실수 3가지**:
  1. `import A as B` → `as`는 **별칭(다른 이름)**. `find_policy_evidence as risk_type`는 "함수를 앞으로 risk_type이라 부르겠다"가 돼서 원래 이름이 사라짐. 우리가 원한 건 별칭이 아니라 두 이름 나란히 가져오기 → `as` 빼고 콤마만.
  2. `from find_policy_evidence import ...` → **from 뒤엔 파일**이 와야 하는데 함수 이름을 넣음. 두 칸이 서로 바뀐 것.
  3. `import risk_type` → `risk_type`은 그 파일에 실제로 없는 이름. 함수 정의 `def find_policy_evidence(risk_type, chunks)`의 **매개변수(괄호 안 입력칸)**일 뿐, 파일 밖으로 꺼낼 수 있는 물건이 아님 → ImportError.

  **정답**:
  ```python
  from src.policy_retriever import find_policy_evidence, chunks
  ```
  import 할 수 있는 건 그 파일에 진짜 정의된 것들(함수 `find_policy_evidence`, 변수 `chunks`, 딕셔너리 `RISK_KEYWORDS`)뿐이다.

  **한 줄 정리**: from=어느 파일 / import=그 안의 실제 이름들 / as=별칭 / 함수 매개변수는 import 대상이 아니다.

## [2026-09-12] for문으로 각 행에 함수 돌려 새 컬럼 만들기 (내가 틀린 3가지)

- Q(내 질문): df의 각 행에 `find_policy_evidence()`를 돌려서 `policy_evidence` 컬럼을 만들려는데 계속 헷갈림.

- A(핵심 답변):
  **최종 정답 코드**:
  ```python
  risk_explanation = []                       # ① 빈 리스트 준비
  for rt in df["risk_type"]:                  # ② risk_type 컬럼 값을 한 개씩 rt로 꺼냄
      ev = find_policy_evidence(rt, chunks)   # ③ rt를 함수에 넣고, 결과는 새 변수 ev에
      risk_explanation.append(ev)             # ④ 리스트에 ev 한 개만 담음
  df["policy_evidence"] = risk_explanation    # ⑤ for 밖에서, 다 모은 리스트를 새 컬럼으로
  ```

  **내가 틀렸던 3가지 (이게 진짜 복습 포인트)**:
  1. **함수에 뭘 넣나** — `find_policy_evidence(RISK_KEYWORDS, chunks)`로 딕셔너리 전체를 넣었음 ❌.
     함수가 원하는 첫 인자는 "위험유형 하나"인데, 그건 for문이 꺼내준 `rt`다 → `find_policy_evidence(rt, chunks)`.
     (딕셔너리 RISK_KEYWORDS는 함수가 내부에서 알아서 씀. 내가 넘길 게 아님.)
  2. **결과를 어디 담나** — `rt = 함수(...)`로 **루프 변수 rt를 덮어씀** ❌.
     그러면 방금 꺼낸 원본 값이 사라진다. 결과는 **새 변수 ev**에 담아야 함.
  3. **append는 한 개만** — `.append(A, B)`처럼 두 개 넣으면 에러 ❌. append()는 인자 딱 1개. 담을 건 결과 ev 하나.
  + **들여쓰기 위치**: `df["policy_evidence"] = ...`를 for문 안에 두면 매 반복마다 실행됨. 리스트 다 모은 뒤 한 번만 하면 되니 **for 밖(같은 들여쓰기 높이 아님, for보다 왼쪽)** 으로 뺀다.

  **패턴으로 기억**: "빈 리스트 → for로 하나씩 꺼내 → 함수 돌려 결과 얻어 → append → 루프 끝나고 컬럼에 넣기". 이건 `detect_risks`가 컬럼 만든 것과 같은 계열(각 행 처리해서 새 컬럼 만들기). 관련: [[from-import-구조]]
