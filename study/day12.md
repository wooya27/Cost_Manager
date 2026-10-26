# Day 12 — import 시점·`__main__` 가드·실행 순서 (policy_retriever 디버깅)

> 2026-10-26. `src/policy_retriever.py`를 점검하다 "import하면 터지는" 문제를 네 번 고치며 잡은 개념.
> 핵심 한 줄: **"파일을 import하면 그 파일이 위→아래로 한 번 실행된다. 그래서 '직접 실행할 때만' 돌 코드는 `if __name__ == "__main__":` 안에 넣고, 변수·함수는 쓰기 전에 만들어야 한다."**

---

## 1. import하면 무슨 일이 일어나나 (제일 중요)

### 개념
다른 파일에서 `from src.policy_retriever import find_policy_evidence` 라고 쓰면,
파이썬은 함수 하나만 쏙 빼오는 게 아니라 **그 파일 전체를 위에서 아래로 한 번 실행**한다.

### 이유 (왜 크래시가 났나)
그래서 파일 **최상단(들여쓰기 0칸)** 에 이런 코드가 있으면:
```python
with open("policy.txt", "r", encoding="utf-8") as f:   # ← 모듈 최상단
    policy_messages = f.read().split("\n\n")
```
이 `open()`이 **import하는 순간 같이 실행**된다. 만약 실행 위치(cwd)에 `policy.txt`가 없으면
`FileNotFoundError`로 **import 자체가 실패** → 그 파일을 쓰려던 app.py 등 전부 같이 죽는다.

### 해결 = `if __name__ == "__main__":` 가드
```python
if __name__ == "__main__":        # 이 파일을 "직접" 실행할 때만 True
    with open("policy.txt", "r", encoding="utf-8") as f:
        policy_messages = f.read().split("\n\n")
    chunks = make_policy_chunks(policy_messages)
    ...
```
- `__name__`은 파이썬이 자동으로 채워주는 값.
  - 이 파일을 `python src/policy_retriever.py`로 **직접 실행** → `__name__ == "__main__"` → 블록 실행 O
  - 다른 파일이 **import** → `__name__ == "src.policy_retriever"` → 블록 실행 X
- 그래서 "저장 테스트 코드"처럼 직접 돌릴 때만 필요한 건 전부 이 블록 안에 넣는다.

### 확인 방법 (오늘 실제로 함)
```bash
python -c "import src.policy_retriever; print('OK')"
```
→ import만 했는데 `policy.txt`를 안 열고 OK가 뜨면 성공. (파일 열기가 __main__ 안으로 잘 들어간 것)

---

## 2. 실행 순서 — "만드는 줄"이 "쓰는 줄"보다 위

(이건 [2026-09-17] app.py `row` NameError 때 한 거랑 **같은 개념**. 🔁 오늘 두 번 더 밟음)

### 개념
파이썬은 위→아래 순서로 실행한다. 변수는 **만들어진(=값이 대입된) 줄 아래에서만** 쓸 수 있다.

### 오늘 틀렸던 순서 (NameError 2번)
```python
if __name__ == "__main__":
    chunks = make_policy_chunks(policy_messages)   # ← policy_messages를 "쓴다"
    with open("policy.txt") as f:                  # ← policy_messages를 "만든다" (너무 늦음!)
        policy_messages = f.read().split("\n\n")
```
→ 쓰는 줄이 위라서, 실행될 때 `policy_messages`가 아직 없음 → `NameError`.

### 맞는 순서
```python
if __name__ == "__main__":
    with open("policy.txt") as f:                  # ① 먼저 만들고
        policy_messages = f.read().split("\n\n")
    chunks = make_policy_chunks(policy_messages)    # ② 그다음 쓴다
```

### 비유
요리로 치면 "장 보기(재료 만들기) → 요리하기(재료 쓰기)" 순서.
재료도 없이 요리부터 하면 안 된다.

---

## 3. 함수 정의 위치 — `__main__`은 항상 맨 아래

### 개념
`def`로 함수를 "만드는" 것도 위→아래 규칙을 따른다.
`__main__` 블록이 어떤 함수를 부르면, **그 함수는 `__main__`보다 위에** 정의돼 있어야 한다.

### 규칙으로 외우기
```
파일 위쪽:  import → 상수(RISK_KEYWORDS 등) → 함수들(def ...)
파일 맨 밑:  if __name__ == "__main__":   ← 항상 제일 아래
```
- 새 함수(예: 평가용 키워드 리트리버)는 **함수들 끝, `__main__` 바로 위**에 넣는다.
- `__main__` **아래**(파일의 진짜 맨 끝)에 함수를 넣으면, `__main__`이 그 함수를 부를 때 아직 정의 전이라 `NameError`.

---

## 4. 오늘 나온 Q&A

### Q1. 임베딩 모델 이름 어디서 확인해?
- **공식 문서**가 1순위. 도메인이 `ai.google.dev`(Gemini) 인지 꼭 확인 — 블로그·광고사이트 말고.
  - 모델 목록: `ai.google.dev/gemini-api/docs/models`
  - 임베딩 가이드(코드 예시): `ai.google.dev/gemini-api/docs/embeddings`
- 문서 안 `client.models.embed_content(model="...")`의 따옴표 안 문자열이 정답 이름.
- **오늘 결과**: 내가 쓴 `gemini-embedding-2`는 **없는 이름**. 맞는 건 **`gemini-embedding-001`**.
  (옛날 글의 `text-embedding-004`는 2026-01-14 은퇴 예정이라 지금 쓰면 안 됨.)
- `output_dimensionality=768`은 권장값(3072/1536/768) 중 하나라 OK.

### Q2. `open` 블록 어디 들어가야 돼?
- **두 조건 동시 만족**: ① `if __name__ == "__main__":` 안쪽(4칸 들여쓰기) + ② 그걸 쓰는 `make_policy_chunks(...)`보다 위.
- 하나만 맞추면 계속 터진다 (안쪽인데 순서 틀림 → NameError / 순서 맞는데 밖으로 나감 → import 크래시 부활).

### Q3. 평가용 함수 제일 끝에 넣으면 돼?
- "제일 끝"이 **`__main__`보다 아래**면 ❌ (NameError). **함수들 끝 + `__main__` 바로 위**면 ✅.
- 규칙: `if __name__ == "__main__":`은 **언제나 파일 맨 밑**, 함수는 그 위에 다 모은다.

---

## 5. 한 줄 복습 (안 보고 떠올리기)
1. import하면 그 파일이 ( ) 실행된다 → "직접 실행할 때만" 돌 코드는 ( ) 안에.
2. 변수·함수는 ( )보다 ( )에 있어야 한다 (안 그러면 NameError).
3. `__main__` 블록의 위치는 항상 파일의 ( ).

<!-- 답: 1.위→아래 한 번 / if __name__=="__main__": 2.쓰는 줄 / 위 3.맨 아래 -->
