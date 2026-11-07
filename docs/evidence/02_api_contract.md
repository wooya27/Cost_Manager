# 02 · API 계약 · 복수 위험 재현 (DAY1 B02)

> 기록일: 2026-11-07 (KST) · 11.08 계획 B02 + 10.17 Day2 (risks[]/batch)

## 1. `POST /audit` 입력 필드 (ExpenseRequest / Pydantic)

| 필드 | 타입 | 필수 | 비고 |
|---|---|---|---|
| employee | str | ✅ | |
| department | str | ✅ | |
| category | str | ✅ | |
| amount | int | ✅ | 정수. 문자열이면 `422` |
| date | str | ✅ | |
| vendor | str | ✅ | |
| reason | str \| None | ❌ | 기본 None |
| has_receipt | str | ✅ | "Y"/"N" |

## 2. `POST /audit` 출력 필드

```
id              # DB에 저장된 감사 결과 id
employee, category, amount
risks[]         # 위험별 객체 리스트 (핵심)
  └ {risk_type, risk_reason, policy_evidence, draft_message, draft_source}
risk_type, risk_reason, policy_evidence, draft_message, draft_source
                # ↑ 기존 구조 호환용 '대표 위험 1개' 단일 필드
```

## 3. 합성 사례 A — 복수 위험이 개별 항목으로 분리되는지

**입력:** `category=식대, amount=35000, has_receipt=N, reason=점심 식사`

**위험 탐지 결과 (detect_risks, 결정론적·재현 가능):**

```json
탐지된 위험 개수: 2
[
  { "risk_type": "영수증누락",   "risk_reason": "영수증 없음" },
  { "risk_type": "식대한도 초과", "risk_reason": "식대 20,000원 초과" }
]
```

- 규칙1(has_receipt=N) → 영수증누락, 규칙4(식대>20000) → 식대한도 초과.
- **두 위험이 하나의 문자열로 뭉쳐지지 않고 개별 dict로 분리**됨 → 이후 각 위험마다 `policy_evidence`/`draft_message`/`draft_source`가 따로 붙는다.
- 재현: `PYTHONPATH=. PYTHONIOENCODING=utf-8 python <스크립트>` (scratchpad `b02_case.py`)

**각 위험의 RAG 근거 + 초안 생성:** `/audit` 엔드포인트가 `processed_risks` 루프에서 위험마다
① `find_similar_policies(risk_reason)`로 규정 검색 → ② 근거 없으면 `draft_source="needs_review"`(LLM 미호출), 있으면 LLM 초안/실패 시 template →
③ `processed_risks[]`에 누적 → ④ `risks JSONB`로 **한 번** 저장. (코드: `api/main.py:120~266`)

## 4. ⚠️ 단건 `/audit` vs `/audit/batch` — 처리 범위가 다름 (정직 표기 필수)

| | `POST /audit` (단건) | `POST /audit/batch` |
|---|---|---|
| 위험 탐지(detect_risks) | ✅ | ✅ |
| RAG 규정 검색 | ✅ | ❌ |
| LLM 초안 생성 | ✅ | ❌ |
| DB 저장 | ✅ | ❌ (저장 안 함) |
| 응답 | id + risks[] + 대표필드 | count + results[](risks만) |
| 쓰임 | 1건 전체 파이프라인 | 여러 행 필요한 규칙(중복/평균 이상치) 집합 탐지 |

**근거:** `/audit/batch`는 `detect_risks`만 호출하고 결과를 그대로 반환(`api/main.py:295~352`).

## 30초 설명

> "`/audit/batch`가 1,000건의 위험을 탐지했다고 해서 '1,000건을 RAG+LLM으로 처리했다'고 말하면 안 된다.
> batch는 여러 행이 있어야 가능한 규칙(중복/이상치)을 집합으로 탐지하는 용도이고,
> RAG·LLM·DB 저장까지 도는 것은 단건 `/audit`이다. 그래서 둘을 구분해 표기한다."

## 상태: 완료 (탐지 결정론 증명 완료 / LLM·DB 전체응답은 기존 통과 테스트로 확인)
