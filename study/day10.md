# Day 10 — Streamlit 상세화면: selectbox로 고른 행 보기

> 2026-09-15. 드롭다운(selectbox)으로 위험 건 하나를 고르면 그 행 전체를 꺼내 상세 정보를 보여주는 화면.

---

## selectbox + `.loc`로 고른 행 상세 보기

### 개념 (최종 코드)
```python
selected = st.selectbox("확인할 위험 건을 선택", risk_df.index)  # 드롭다운 → 고른 값(행번호)이 selected에
row = risk_df.loc[selected]                                    # 그 번호의 행 전체를 꺼냄
st.write("신청자:", row["employee"])                           # row["컬럼"]으로 값 하나씩
```

### 이유 / 각 줄 설명
- **`st.selectbox("라벨", 선택지)`**: 화면에 드롭다운을 띄우고 사용자가 **고른 값 하나**를 돌려준다. 선택지로 `risk_df.index`(위험 건들의 행번호 목록)를 줬으니 고른 번호가 `selected`에 들어옴.
- **`.loc[번호]`**: 그 번호 행을 **통째로** 꺼낸다. 결과는 한 줄(Series) → `row["employee"]`처럼 값 하나씩 꺼내 쓴다. (make_draft 안에서 row 쓰던 것과 같음)
- `df.loc[selected]`도 `risk_df.loc[selected]`도 둘 다 동작(인덱스 공유). selected가 risk_df에서 나왔으니 `risk_df.loc`이 더 자연스러움.

**한 줄 정리**: selectbox=고른 값 돌려줌 / `.loc[번호]`=그 행 전체 / `row["컬럼"]`=값 하나.

**관련**: [[day9]] row vs df (고른 행 `row`도 한 줄=Series).
