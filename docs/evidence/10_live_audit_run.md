# 10 · 라이브 /audit 전체 파이프라인 실행 (단서① 해소)

> 기록일: 2026-11-07 (KST) · mock 없음 — 실제 pgVector + Gemini LLM + PostgreSQL

## 실행
- 경로: FastAPI TestClient → `POST /audit` (실 DB `localhost:5433`, 실 Gemini)
- 입력(합성): `{category:식대, amount:35000, has_receipt:N, reason:점심 식사, ...}`

## 결과
```
POST /audit → status 200, 저장 id = 91
위험 2개 (각각 다른 규정·초안으로 분리):
  위험1 영수증누락    → policy_evidence=[영수증 규정]  draft_source=llm
  위험2 식대한도 초과  → policy_evidence=[식대 규정]    draft_source=llm
GET /audit-results → id=91 저장 확인 True
```

- LLM 초안 예(식대한도 초과): "신청해 주신 식대(35,000원)는 규정상 1인 한도(20,000원)를 초과하여 확인이 필요합니다. 초과 금액에 대한 별도 승인 내역을 첨부…"

## 의미
- `detect_risks → pgVector 규정검색 → Gemini LLM 초안 → PostgreSQL 저장` **전체가 라이브로 1회 완주**.
- 복수 위험이 하나로 뭉치지 않고 **위험별로 다른 규정·다른 초안**을 유지(핵심 설계 목표 라이브 증명).
- 앞서 "제가 라이브 /audit를 실행한 적 없음(단서①)" 상태를 해소.

## 재현
```bash
docker compose up -d
PYTHONPATH=. PYTHONIOENCODING=utf-8 python -c "from fastapi.testclient import TestClient; from api.main import app; print(TestClient(app).post('/audit', json={'employee':'테스트직원','department':'개발팀','category':'식대','amount':35000,'date':'2026-11-06','vendor':'가상식당','reason':'점심 식사','has_receipt':'N'}).json())"
```

## 상태: 완료
