# Day 9 — DraftMessage: 한 행 처리 + 값 2개 리턴 + iterrows

> 2026-09-14~15. 각 지출 건(한 행)마다 보완요청 초안을 만드는 `make_draft`를 작성하며 잡은 개념들.

---

## 1. row(한 줄)와 df(표 전체)의 차이

### 개념
`make_draft(row)`의 `row`는 표 전체가 아니라 표에서 딱 한 건 = 판다스 **Series**(한 사람의 한 지출 건).

| 코드 | 대상 | 하는 일 | 맞나 |
|---|---|---|---|
| `row["employee"]` | 한 줄(Series) | 그 줄에서 값 하나 꺼내기 → `"김철수"` | ✅ |
| `row.duplicated(subset=[...])` | (원래) 표 전체(DataFrame) | 여러 줄 비교해 중복 찾기 | ❌ |

### 이유
- `.duplicated()`는 "여러 줄끼리 비교"라 대상이 여러 개 있어야 함 → `df.duplicated(...)`처럼 **표 전체**에 쓴다. row는 한 줄뿐이라 비교 대상이 없음.
- **중복 찾기는 이미 Day5 `detect_risks`가 끝냈다.** 결과가 `risk_type="중복 신청 의심"`으로 각 행에 들어있음 → `make_draft`에선 `row["risk_type"]`만 읽어 문구만 만들면 됨 (다시 계산 X).

**한 줄 정리**: row=한 줄(값 꺼내는 곳) / df=표 전체(.duplicated 같은 줄-비교 연산 쓰는 곳). 이미 계산된 건 다시 말고 컬럼에서 읽어 쓴다.

---

## 2. 값 2개 리턴 & 언패킹

### 개념
함수가 콤마로 값 2개를 묶어 돌려주면, 받을 때도 변수 2개로 나눠 받는다.
```python
def make_draft(row):
    ...
    return draft_message, draft_source   # 값 2개를 콤마로 묶어 돌려줌

message, source = make_draft(row)        # 2개로 나눠 받음 (언패킹)
```
- **규칙**: 왼쪽 변수 개수 = 오른쪽 값 개수 (2=2). **순서도 그대로**(message 앞, source 뒤).
- "묶여 온 걸 여러 변수로 푸는 것" = **언패킹(unpacking)**. (상자 1개 열어 물건 2개 꺼내기)
- **왜**: 초안 문장과 출처 꼬리표(`"template"`)를 한 함수에서 같이 만들어 같이 돌려주려고.

---

## 3. `for _, row in df.iterrows()` — `_`의 의미 & 컬럼은 왜 for 밖

### 개념 (최종 코드)
```python
draft_messages = []
draft_sources = []
for _, row in df.iterrows():          # iterrows()는 매번 (행번호, 행전체) 2개를 줌
    message, source = make_draft(row) # 행 전체를 함수에 넣고 값 2개 받기
    draft_messages.append(message)    # ← for 안: 매 행마다 하나씩 쌓기
    draft_sources.append(source)
df["draft_message"] = draft_messages  # ← for 밖: 다 쌓인 뒤 한 번에 컬럼으로
df["draft_source"] = draft_sources
```

### 이유
- **`_`의 의미**: `iterrows()`는 한 줄마다 **2개**(행번호, 행전체)를 줌. 행번호는 안 쓰고 행 전체만 필요 → 안 쓸 자리에 `_`를 넣어 "버린다"고 표시하는 관례.
  - ⚠️ `for row in df.iterrows()`처럼 하나로만 받으면 `row`에 `(행번호, 행)` 쌍이 통째로 들어가 `make_draft`가 터짐 → 반드시 `_, row` 2개로.
- **컬럼은 왜 for 밖?**: 리스트가 다 채워진 뒤 한 번만 하면 됨. for 안에 두면 매 행마다 붙였다 다시 붙였다 낭비 → 들여쓰기를 for보다 왼쪽으로.

**관련**: Day7 `policy_evidence` 만든 것과 완전 같은 패턴(각 행 처리→새 컬럼). 값이 2개라 리스트·컬럼이 2개일 뿐.
