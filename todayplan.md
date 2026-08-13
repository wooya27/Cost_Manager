# 오늘 할 일 (Day 1 · 4블록) — 환경 + 첫 화면 + CSV 업로드

> 🎯 오늘의 목표: **CSV를 올리면 표로 보여주는 Streamlit 화면 하나 띄우기.**
> 오늘 블록 다 적어놨다. 순서대로 위에서부터. 지금 집중할 건 👉 표시된 1개. 나머지는 그거 끝나고 보면 돼.


---
## 오늘 배우는 개념 (3개, 블록 하면서 필요할 때만)
- Streamlit이 뭐고 왜 쓰나 (파이썬만으로 웹 화면)
- `st.file_uploader` / `st.dataframe` 기본
- `pd.read_csv`로 CSV → 표(DataFrame)

## 막혔을 때 최소선
업로드가 끝까지 안 되면, `pd.read_csv("sample_expenses.csv")` 고정 경로로 표만 띄워도 오늘 성공.

## 30초 설명 (오늘 끝나면 이렇게 말하기)
"파이썬 Streamlit으로 CSV를 업로드하면 바로 표로 보여주는 화면을 만들었습니다."

---
## 완료
- [x] (8/13) 블록 1 — 개발 환경 세팅: venv에 streamlit·pandas 설치, requirements.txt·app.py 생성
- [x] (8/13) 블록 2 — Streamlit 첫 실행: `st.title`/`st.write`로 제목+문구 표시, `streamlit run app.py`로 브라우저 확인
- [x] (8/13) 블록 3 — CSV 업로드+표 출력: `st.file_uploader`로 파일 받고 `if uploaded:` 조건 안에서 `pd.read_csv`→`st.dataframe`
- [x] (8/13) 블록 4 — 샘플 데이터: `sample_expenses.csv` 15행 (검수 함정 케이스 포함), Claude가 생성
