# Day 10~11 (2026-09-17) — 검수 상태 + Dashboard + Agent 역할 (DAY1 마무리)

> 🎯 오늘의 목표: ①검수 상태를 화면에 표시 ②전체 현황 숫자 카드(Dashboard) ③만든 기능을 Agent 역할로 정리.
> 이 문서는 오늘 **내가 헷갈렸던 것 + 새로 배운 것**을 안 보고 떠올릴 수 있게 정리한 것.

---

## 1. ⭐ 변수는 "태어난 줄보다 아래"에서만 쓸 수 있다 (오늘 제일 헷갈림) 🆕

`review_status` 표시 줄을 어디에 둘지에서 **NameError**를 두 번 겪었다.

### 개념
파이썬은 코드를 **위에서 아래로 한 줄씩 순서대로** 읽고 실행한다.
그래서 어떤 변수는 **그 변수가 만들어진(정의된) 줄보다 아래**에서만 쓸 수 있다.
만들어지기 전 줄에서 쓰면 → **`NameError: name 'row' is not defined`** 로 멈춘다.

```python
st.write("검수상태:", row["review_status"])   # ❌ 여기서 row 씀 (60번, 69번)
...
row = risk_df.loc[selected]                    # row 는 여기서 '태어남' (72번)
```
- `row`는 72번 줄에서 처음 만들어진다.
- 그보다 **위**(60·69번)에서 쓰면 그 시점엔 `row`가 아직 없다 → NameError.
- 60→69로 옮겨도 여전히 72번보다 위라서 똑같이 실패. **"72번보다 아래"** 로 내려야 함.

### 정답 위치
`row`를 쓰는 다른 `st.write`들과 **같은 무리, 맨 밑**:
```python
    st.write("보완 요청 초안:", row["draft_message"])
    st.write("검수상태:", row["review_status"])   # ✅ row 태어난 뒤 + 다른 row 줄들과 함께
```
**판단법:** "이미 `row`를 잘 쓰는 줄들이 되는 자리면, 이것도 된다."

**비유:** 사람을 소개(정의)하기도 전에 이름을 부르면 아무도 못 알아듣는다. 소개 먼저, 이름 부르기는 그 뒤.

**한 줄 암기:** 코드는 위→아래 실행 / 변수는 "태어난 줄보다 아래"에서만 사용 / 어기면 NameError.

---

## 2. `st.metric` — 숫자 하나를 큰 카드로 🆕

Dashboard(전체 현황)를 만들 때 씀. **표(table)가 아니다.**

| 위젯 | 뭘 보여주나 | 예시 |
|---|---|---|
| `st.metric` | 숫자 **한 개**를 큰 카드로 | `전체 신청 건수: 15` |
| `st.dataframe` | 여러 줄·칸이 있는 **표** | 위험 건 목록 전체 |

```python
st.metric("라벨(제목)", 값)          # st.write랑 순서 같음, 이름만 metric
st.metric("전체 신청 건수", 15)
```

오늘 넣은 값 3개는 전부 **이미 구해본 것**:
```python
total_count  = df.shape[0]         # 전체 신청 건수 (행 개수)
risk_count   = risk_df.shape[0]    # 위험 건수
total_amount = df["amount"].sum()  # 총 신청 금액
```

**한 줄 암기:** metric = 숫자 1개 카드(≠ dataframe 표).

---

## 3. `st.columns` — 카드를 가로로 나란히 (배치, 잡일) 🆕

세로로 쌓이는 걸 옆으로 나란히 놓는 꾸미기. 실무에서 핵심은 아님.

```python
col1, col2, col3 = st.columns(3)   # 화면을 3칸으로 쪼갬
col1.metric("전체 신청 건수", total_count)
col2.metric("위험 건수", risk_count)
col3.metric("총 신청 금액", f"{total_amount}원")
```
- `st.columns(3)` → 3칸을 만들어 `col1, col2, col3`로 받는다(언패킹, Day9에 배운 값 여러 개 받기와 같은 원리).
- `st.metric(...)` 대신 `col1.metric(...)`처럼 앞에 칸 이름을 붙이면 그 칸 안에 들어간다.

---

## 4. 숫자 + 글자 합치기 = f-string 🔁 (Day9 f-string 재활용)

`총 신청 금액`에 `"원"`을 붙이려다 막힘.

```python
col3.metric("총 신청 금액", (df["amount"].sum())"원")   # ❌ SyntaxError
```
- **숫자와 글자는 그냥 나란히 둔다고 안 붙는다.** `+`로도 안 됨(`숫자 + "원"` → 종류 달라 에러).
- 붙이려면 **둘 다 글자로 만들어** 합쳐야 함 → **f-string**이 딱 그 용도.

```python
col3.metric("총 신청 금액", f"{total_amount}원")   # ✅ "1250000원"
```
- ⚠️ 참고: `f"{ df["amount"].sum() }원"` 처럼 **f-string 큰따옴표 안에서 또 큰따옴표**를 쓴 건 원래 옛날 파이썬에선 에러였는데, 내 파이썬이 **3.14**라 허용돼서 돌아간다(살짝 아슬아슬). → **만들어둔 변수 `total_amount`를 쓰는 게 안전하고 깔끔.**

---

## 5. Agent 역할 정리 (코드 X, 개념) 🆕

내가 만든 기능 4개에 **역할 이름**을 붙이고, 왜 나눴는지 설명하는 연습.

| 단계 | 이미 만든 기능 | Agent 이름 |
|---|---|---|
| ① 위험 탐지 | `detect_risks` (7종 위험) | **AuditRule** |
| ② 규정 검색 | `find_policy_evidence` | **PolicySearch** |
| ③ 보완 요청 초안 | `make_draft` | **DraftMessage** |
| ④ 사람 검수 | `review_status` | **ReviewSupport** |

**왜 역할을 나눴나?** 한 함수에 다 넣으면 복잡해서 못 다룬다 → 나누면
① 한 군데만 고치면 됨 ② 각각 따로 이해·테스트 ③ 나중에 갈아끼우기 쉬움(템플릿→진짜 LLM 등).

**왜 ④ 사람 검수를 넣나?** AI가 틀릴 수 있어서 **최종 판단은 사람**이 한다 = **Human-in-the-loop**.

### 30초 발표 스크립트
> AuditFlow AI는 비용 CSV를 받아 4단계를 거칩니다. ①위험 탐지(AuditRule) → ②규정 검색(PolicySearch) → ③보완 요청 초안(DraftMessage) → ④사람 검수(ReviewSupport). 한 함수에 다 넣으면 복잡해서 역할을 나눴고, 그래야 각 단계를 따로 고치고 교체하기 쉽습니다. 마지막은 AI가 틀릴 수 있어 사람이 최종 확인하도록(Human-in-the-loop) 했습니다.

---

## 6. 30초 셀프 체크 (안 보고 말할 수 있으면 합격)
1. `row`를 쓰는 줄은 어디에 있어야 해? → (`row =` 로 태어난 줄보다 **아래**. 안 그러면 NameError)
2. `st.metric`은 뭘 보여줘? → (숫자 **한 개**를 큰 카드로. 표 아님)
3. 숫자에 "원"을 붙이려면? → (`f"{값}원"` — f-string으로 글자로 만들어 합침)
4. 4개 Agent 역할과 순서는? → (AuditRule → PolicySearch → DraftMessage → ReviewSupport)
5. 왜 사람 검수를 넣었어? → (AI가 틀릴 수 있어 최종은 사람 = Human-in-the-loop)
