# Day 1 (2026-08-13) — Streamlit 첫 화면 + CSV 업로드해서 표로 보기

> 🎯 오늘의 목표: CSV를 올리면 표로 보여주는 Streamlit 화면 하나 띄우기.
> 결과물: `app.py` (업로드→표), `sample_expenses.csv` (테스트 데이터)

---

## 1. 오늘 쓴 기술이 뭐고 왜 쓰나

### Streamlit 🆕
- **뭐냐:** 파이썬 코드만으로 웹 화면(버튼, 표, 그래프)을 만들어주는 도구.
  HTML/CSS/JS 몰라도 `st.무언가(...)` 한 줄이면 화면에 요소가 하나 생긴다.
- **왜 쓰나:** 우리는 웹 개발자가 아니니까, 데이터 다루는 화면을 "빠르게" 띄우려고.
- **실행법:** 터미널에서 `streamlit run app.py` → 브라우저가 자동으로 열림.
- **핵심 감각:** 코드를 저장하면 브라우저가 알아서 다시 그려준다(rerun).

### pandas 🆕
- **뭐냐:** 표(엑셀 같은 데이터)를 파이썬에서 다루는 도구.
- **DataFrame(df):** pandas가 표를 담는 그릇. 관례적으로 변수 이름을 `df`라고 쓴다.

---

## 2. 오늘 만든 코드 (app.py)와 한 줄씩 설명

```python
import streamlit as st          # streamlit을 st라는 짧은 이름으로 불러오기
import pandas as pd             # pandas를 pd라는 짧은 이름으로 불러오기

st.title("AuditFlow AI")                    # 제일 큰 제목
st.write("비용정산 1차 검수 어시스턴트")      # 아무 텍스트/데이터나 화면에 출력

uploaded = st.file_uploader("CSV 올리기", type="csv")   # 파일 올리는 칸

if uploaded:                          # 파일이 실제로 올라왔을 때만 아래 실행
    df = pd.read_csv(uploaded)        # 올린 CSV를 표(df)로 읽기
    st.dataframe(df)                  # 그 표를 화면에 그리기
```

### 각 함수 역할
| 코드 | 하는 일 |
|---|---|
| `st.title(...)` | 페이지 맨 위 큰 제목 |
| `st.write(...)` | 텍스트든 데이터든 화면에 뿌려주는 만능 출력 |
| `st.file_uploader("라벨", type="csv")` | "파일 선택" 버튼 생성. csv만 받게 제한 |
| `pd.read_csv(파일)` | CSV를 pandas 표(DataFrame)로 변환 |
| `st.dataframe(df)` | 표를 화면에 그리기(정렬·스크롤 되는 표) |

---

## 3. 오늘 제일 헷갈렸던 것 (❗복습 핵심)

### Q. 왜 `pd.read_csv(uploaded)`만 쓰면 안 되고 `if`가 필요해?
**A.** `st.file_uploader`는 사용자가 **아직 파일을 안 올리면 `uploaded`에 `None`(비어있음)** 을 넣는다.
그 상태에서 `pd.read_csv(None)`을 실행하면 읽을 파일이 없어서 **에러**가 난다.
그래서 "파일이 있을 때만 읽어라"는 조건이 필요하다 → `if uploaded:`.

### Q. 조건을 `pd.read_csv(uploaded > 0)`처럼 괄호 안에 넣으면 왜 틀려?
**A.** `read_csv(...)`의 괄호 안은 **"무엇을 읽을지(=파일)"** 를 넣는 자리다.
거기에 조건(`uploaded > 0`)을 넣으면 "파일을 읽어라"가 아니라 "비교 결과를 읽어라"가 돼버린다.
게다가 `uploaded`는 파일이지 숫자가 아니라서 `> 0` 비교 자체가 안 된다.
→ **조건문은 괄호 안에 넣는 게 아니라, 실행할 줄들을 "위에서 감싸는" 별도의 줄이다.**

```python
# ❌ 틀림: 조건을 괄호 안에
df = pd.read_csv(uploaded > 0)

# ✅ 맞음: if로 감싸고, 안쪽 줄은 들여쓰기
if uploaded:
    df = pd.read_csv(uploaded)
    st.dataframe(df)
```

### 파이썬 `if`의 3가지 규칙 (오늘 배운 것)
1. `if 조건:` — 끝에 **콜론 `:`** 꼭 붙인다.
2. 조건이 참일 때 실행할 줄들은 **스페이스 4칸 들여쓰기**로 "if에 속한 줄"임을 표시한다.
3. `if uploaded:` 처럼 값 자체를 조건으로 쓰면, **값이 있으면 참 / 비어있으면(None) 거짓** 으로 판단된다. (`> 0` 같은 비교 안 붙여도 됨)

---

## 4. 샘플 데이터 (sample_expenses.csv)
- 컬럼: `expense_id, employee, department, category, amount, date, vendor, reason, has_receipt`
- 나중 검수 로직에 걸리게 **함정 케이스**를 일부러 섞음:
  - 영수증 없음(`has_receipt=N`): E005, E006, E011, E015
  - 식대 2만원 초과: E003, E009, E015
  - vendor 비어있음: E012
  - 고액 접대 + 영수증 없음(이중 위반): E006

---

## 5. 30초 설명 (안 보고 말할 수 있으면 오늘 합격)
"파이썬 Streamlit으로 CSV를 업로드하면 바로 표로 보여주는 화면을 만들었습니다.
`st.file_uploader`로 파일을 받고, 파일이 올라왔을 때만(`if`) `pd.read_csv`로 읽어서
`st.dataframe`으로 표를 그렸습니다."
