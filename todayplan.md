# 오늘 할 일 (Day 1 · 4블록) — 환경 + 첫 화면 + CSV 업로드

> 🎯 오늘의 목표: **CSV를 올리면 표로 보여주는 Streamlit 화면 하나 띄우기.**
> 오늘 블록 다 적어놨다. 순서대로 위에서부터. 지금 집중할 건 👉 표시된 1개. 나머지는 그거 끝나고 보면 돼.

## 블록 1 (25분) — 개발 환경 세팅 · 🔧 세팅  👉 지금 이거
> 이건 배울 대상이 아니라 그냥 깔아주는 부분이야. 내가 세팅해줄게.
- [ ] 가상환경 만들기 + `streamlit`, `pandas` 설치
- [ ] `requirements.txt` 생성
- [ ] 빈 `app.py` 생성
- 끝나면 보여야 할 결과: `streamlit` 설치 완료 메시지 + `app.py` 파일 존재

## 블록 2 (30분) — Streamlit 첫 실행 · 🧠 직접 작성
- [ ] `app.py`에 제목 한 줄 + "Hello" 텍스트 쓰기 (`st.title`, `st.write`)
- [ ] `streamlit run app.py` 실행해서 브라우저에 뜨는지 확인
- 끝나면 보여야 할 결과: 브라우저에 제목과 Hello가 보인다

## 블록 3 (35분) — CSV 업로드 + 표 출력 · 🧠 직접 작성
- [ ] `st.file_uploader`로 CSV 받기
- [ ] `pd.read_csv`로 읽어서 `st.dataframe`으로 표 출력
- 끝나면 보여야 할 결과: CSV 업로드 → 화면에 표가 뜬다

## 블록 4 (30분) — 샘플 데이터 만들기 · 🧠 직접 작성
- [ ] `sample_expenses.csv`를 손으로 12~15행 작성
- [ ] 컬럼: expense_id, employee, department, category, amount, date, vendor, reason, has_receipt
- [ ] 나중 검수에 걸릴 케이스 몇 개 일부러 섞기 (영수증 없음, 식대 2만원 초과 등)
- 끝나면 보여야 할 결과: 업로드하면 내가 만든 데이터가 표로 뜬다

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
(아직 없음 — 블록 끝낼 때마다 여기로 옮기기)
