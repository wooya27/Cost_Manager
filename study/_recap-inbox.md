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

## [2026-09-13] 미니 RAG 핵심 4단어 의미 구분 (risk_type / RISK_KEYWORDS / keyword / policy_evidence)

- Q(내 질문): risk_type, RISK_KEYWORDS, keyword, policy_evidence가 각각 뭔지 자꾸 헷갈린다.

- A(핵심 답변):
  **네 단어를 "흐름" 순서로 놓으면 헷갈림이 사라진다.** 위반 하나가 규정 근거를 찾아가는 파이프라인이다:

  `risk_type` → (RISK_KEYWORDS로 변환) → `keyword` → (policy.txt에서 검색) → `policy_evidence`

  | 단어 | 정체 | 어디 있나 | 예시 |
  |---|---|---|---|
  | `risk_type` | **지출위반 사유(유형)**. detect_risks가 각 행에 붙인 위험 이름 | df의 컬럼(값) | `"식대한도 초과"` |
  | `RISK_KEYWORDS` | **변환표(딕셔너리)**. 위반유형 → 검색키워드 매핑. 내가 손으로 씀 | policy_retriever.py | `{"식대한도 초과":"식대", ...}` |
  | `keyword` | **검색어 한 개**. RISK_KEYWORDS에서 꺼낸 값 | 함수 안 변수 | `"식대"` |
  | `policy_evidence` | **규정 근거(결과)**. keyword로 policy.txt에서 찾아낸 규정 문단 | df의 새 컬럼 | `"[식대 규정] 일반 식대는..."` |

  - `RISK_KEYWORDS`(전체 표)와 `keyword`(그 표에서 꺼낸 값 1개)는 **다른 것**. `keyword = RISK_KEYWORDS.get(risk_type)` — 표에서 하나 꺼내는 것.
  - `risk_type`(입력, 위반 이름)과 `policy_evidence`(출력, 규정 문단)는 **파이프라인의 양 끝**. 앞은 "무슨 위반?", 뒤는 "무슨 규정 근거?".

## [2026-09-13] find_policy_evidence의 두 실패 경우 (31행 vs 36행) — "키워드 뽑았는데 규정 없을 수 있나?"

- Q(내 질문): 31행과 36행이 둘 다 "관련 규정 확인 필요"를 반환하는데 뭐가 다른가? 키워드를 뽑았는데 규정이 없을 수 있다는 게 이해가 안 간다.

- A(핵심 답변):
  실패가 두 종류인데 지금 코드는 **똑같은 문자열**을 돌려줘서 화면에서 구분이 안 된다. 그래서 헷갈렸던 것.

  ```python
  keyword = RISK_KEYWORDS.get(risk_type)
  if keyword is None:
      return "관련 규정 확인 필요"   # ← 31행 = 경우 A
  for chunk in chunks:
      if keyword in chunk:
          return chunk
  return "관련 규정 확인 필요"       # ← 36행 = 경우 B
  ```

  - **경우 A (31행) = 매핑표에 아예 없음.** `RISK_KEYWORDS.get(risk_type)`가 None. 즉 이 위반유형이 딕셔너리 key에 없어서 **검색어조차 못 만든다.** (7종 중 미매핑 3종이 여기: 이상 비용 후보 / 야근 식대 한도초과 / 사무용품 추가 승인)
  - **경우 B (36행) = 검색어는 만들었는데 규정 문서에 그 글자가 없음.** keyword는 정상으로 뽑혔지만, policy.txt 문단들을 다 뒤져도 `if keyword in chunk`(글자 그대로 포함 검사)가 한 번도 안 걸림.

  **"키워드 뽑았는데 규정 없을 수 있나?" → 있다. 왜냐하면 둘은 서로 다른 파일에서 따로 관리되기 때문:**
  - 키워드는 `RISK_KEYWORDS`(policy_retriever.py에 내가 손으로 씀)에서 나옴
  - 규정은 `policy.txt`(별도 파일)에 있음
  - 이 둘이 어긋나면 경우 B 발생. 두 가지 상황:
    1. **철자 불일치**: 딕셔너리엔 `"택시비"`인데 policy.txt엔 "택시 요금"이라 적으면 → "택시비" 글자가 없어서 못 찾음
    2. **문단 자체가 없음**: 예) `"사무용품 추가 승인":"사무용품"` 매핑만 추가하고 policy.txt에 사무용품 문단은 안 쓰면 → keyword "사무용품"은 뽑히지만 어느 chunk에도 없음 → 경우 B
  - 그래서 매핑을 추가할 땐 **순서가 중요**: ① policy.txt에 규정 문단 먼저 → ② RISK_KEYWORDS에 매핑 추가. (반대로 하면 경우 B로 빠짐)
  - 참고: 지금 데이터 기준으론 4개 키워드(식대·택시비·영수증·중복)가 전부 policy.txt에 있어서 **경우 B는 아직 실제로 발생 안 함**. 현재 "확인 필요"는 전부 경우 A.

  관련: [[미니-RAG-4단어-의미]]

## [2026-09-14] row(한 줄)과 df(표 전체)의 차이 — row["employee"] vs row.duplicated()

- Q(내 질문): `make_draft(row)` 안에서 `name = row["employee"]`로 값 꺼내는 것과 `row.duplicated(subset=[...])`로 쓰는 것의 차이가 뭐야?

- A(핵심 답변):
  **핵심은 `row`가 "한 줄뿐"이라는 것.** `make_draft(row)`의 row는 표 전체가 아니라 표에서 딱 한 건만 뽑아온 것 = 판다스 **Series**(한 사람의 한 지출 건).

  | 코드 | 대상 | 하는 일 | 여기서 맞나 |
  |---|---|---|---|
  | `row["employee"]` | 한 줄(Series) | 그 줄에서 값 하나 꺼내기 → `"김철수"` | ✅ |
  | `row.duplicated(subset=[...])` | (원래) 표 전체(DataFrame) | 여러 줄을 서로 비교해 중복 찾기 | ❌ |

  - `.duplicated()`는 **"여러 줄끼리 비교"** 하는 명령이라 비교 대상이 여러 개 있어야 한다. 그래서 `audit_rules.py`에서는 `df.duplicated(...)`처럼 **표 전체(df)** 에 썼다. row는 한 줄뿐이라 서로 비교할 대상이 없다.
  - **중복 찾기는 이미 Day 5의 `detect_risks`가 끝냈다.** 그 결과가 `risk_type = "중복 신청 의심"`으로 각 행에 이미 들어있다. 그러니 `make_draft`에서는 중복을 다시 찾을 필요 없이 `row["risk_type"]` 값만 읽어서 문구만 만들면 된다.

  **한 줄 정리**: row=한 줄(값 꺼내는 곳) / df=표 전체(.duplicated 같은 줄-비교 연산 쓰는 곳). 이미 계산된 결과는 다시 계산 말고 컬럼에서 읽어 쓴다.
  관련: [[for문-각행-함수-새컬럼]]

## [2026-09-15] 값 2개 리턴 & 언패킹 (return a, b / x, y = f())

- Q(내 질문): `return draft_message, draft_source`처럼 값 2개 돌려주는 거랑 받는 거 잘 모르겠어.

- A(핵심 답변):
  **개념**: 함수가 콤마로 값 2개를 묶어 돌려주면, 받을 때도 변수 2개로 나눠 받는다.
  ```python
  def make_draft(row):
      ...
      return draft_message, draft_source   # 값 2개를 콤마로 묶어 돌려줌

  message, source = make_draft(row)        # 2개로 나눠 받음
  ```
  - **규칙**: 왼쪽 변수 개수 = 오른쪽 값 개수 (2=2). **순서도 그대로** (message가 앞, source가 뒤).
  - 이렇게 "묶여서 온 걸 여러 변수로 푸는 것"을 **언패킹(unpacking)**. (택배 상자 1개 열어 물건 2개 꺼내기)
  - **왜 썼나**: 초안 문장(`draft_message`)과 출처 꼬리표(`draft_source`="template")를 한 함수에서 같이 만들어 같이 돌려주려고.

## [2026-09-15] for _, row in df.iterrows() — `_`의 의미 & 컬럼은 왜 for 밖

- Q(내 질문): `for _, row in df.iterrows()`에서 `_`가 뭔지, 컬럼 붙이는 줄이 왜 for 밖이어야 하는지 모르겠어.

- A(핵심 답변):
  **최종 코드**:
  ```python
  draft_messages = []
  draft_sources = []
  for _, row in df.iterrows():          # iterrows()는 매번 (행번호, 행전체) 2개를 줌
      message, source = make_draft(row) # 행 전체(row)를 함수에 넣고 값 2개 받기
      draft_messages.append(message)    # ← for 안: 매 행마다 하나씩 쌓기
      draft_sources.append(source)
  df["draft_message"] = draft_messages  # ← for 밖: 다 쌓인 뒤 한 번에 컬럼으로
  df["draft_source"] = draft_sources
  ```

  **`_`의 의미**: `df.iterrows()`는 한 줄 돌 때마다 **2개**(`행번호`, `행전체`)를 준다. 우리는 행번호는 안 쓰고 행 전체(`row`)만 필요. **안 쓸 자리에 `_`를 넣어 "이건 버린다"고 표시**하는 관례. (`x`라 써도 돌아가긴 함)
  - ⚠️ `for row in df.iterrows()`처럼 하나로만 받으면 `row`에 `(행번호, 행)` 쌍이 통째로 들어가서 `make_draft`가 터진다. → 반드시 `_, row` 2개로.

  **컬럼은 왜 for 밖?**: `df["draft_message"] = ...`는 리스트가 **다 채워진 뒤 한 번만** 하면 된다. for 안에 넣으면 매 행마다 붙였다 다시 붙였다 낭비. (요리 다 끝내고 접시에 담기, 재료 넣을 때마다 담는 거 아님) → 들여쓰기를 for보다 왼쪽으로 빼서 for 밖으로.

  관련: [[for문-각행-함수-새컬럼]] (policy_evidence 만든 것과 완전 같은 패턴, 값이 2개라 리스트·컬럼이 2개일 뿐)

## [2026-09-15] st.selectbox + .loc로 고른 행 상세 보기 (Day10 상세화면)

- Q(내 질문): selectbox로 고른 값으로 그 행 전체를 어떻게 꺼내는지 모르겠어.

- A(핵심 답변):
  **최종 코드**:
  ```python
  selected = st.selectbox("확인할 위험 건을 선택", risk_df.index)  # 드롭다운 → 고른 값(행번호)이 selected에
  row = risk_df.loc[selected]                                    # 그 번호의 행 전체를 꺼냄
  st.write("신청자:", row["employee"])                           # row["컬럼"]으로 값 하나씩
  ```
  - **`st.selectbox("라벨", 선택지)`**: 화면에 드롭다운을 띄우고, 사용자가 **고른 값 하나**를 돌려준다. 여기선 선택지로 `risk_df.index`(위험 건들의 행번호 목록)를 줬으니 고른 번호가 `selected`에 들어옴.
  - **`.loc[번호]`**: 그 번호 행을 **통째로** 꺼낸다. 결과는 한 줄(Series) → `row["employee"]`처럼 값 하나씩 꺼내 쓴다. (make_draft 안에서 row 쓰던 거랑 같음)
  - `df.loc[selected]`도 `risk_df.loc[selected]`도 둘 다 동작 (index가 공유되므로). selected가 risk_df에서 나왔으니 `risk_df.loc`이 더 자연스러움.

  **한 줄 정리**: selectbox=고른 값 돌려줌 / `.loc[번호]`=그 행 전체 / row["컬럼"]=값 하나. 관련: [[row-vs-df]]
