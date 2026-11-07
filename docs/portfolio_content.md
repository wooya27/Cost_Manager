# AuditFlow AI — 포트폴리오 2페이지 내용 초안 (B14 / B15)

> 이 문서는 **텍스트 내용**이다. 이걸 기존 포트폴리오 디자인/PDF에 넣고, 캡처 이미지만 본인이 붙이면 된다.
> **원칙:** 실측·미검증·구현예정을 구분. 추정 수치 금지.

---

## [1페이지] 문제 · 제품 · 기술

### 제목
**AuditFlow AI | 규정 근거 기반 비용정산 1차 검수 자동화**
— 최종 승인은 사람이 (Human-in-the-loop)

### 업무 문제 (3줄)
- 비용정산 검수는 영수증 누락·한도 초과·중복 신청을 **매 건 사람이 확인**해야 한다.
- 문제를 찾은 뒤엔 **관련 규정을 직접 검색**하고 **보완 요청 문구를 반복 작성**한다.
- 건수가 늘수록 검수 시간이 선형으로 증가하고, 정상 건과 위험 건이 구분되지 않는다.

### 실제 구현 처리 흐름 (현재 동작하는 경로만)
```
POST /audit
  → detect_risks()        규칙 기반 복수 위험 탐지 risks[]
  → pgVector 규정 검색      위험별 근거(policy_evidence)
  → LLM / Template 초안      근거 없으면 needs_review (LLM 미호출)
  → PostgreSQL 저장          risks(JSONB) + 대표필드
  → PATCH /review           담당자 승인/보완/반려 (Human-in-the-loop)
```

### 핵심 화면 (캡처 자리 — 본인이 붙이기)
- 합성 비용 1건 → **위험 2개(식대한도 초과 + 영수증누락)가 개별 항목**으로 분리된 응답.
- "왜 이 설계인가?" 2~3문장:
  - 위험 판정은 **규칙(결정론적)** → 같은 입력에 같은 결과, 재현·설명 가능.
  - LLM은 **문장 생성에만** → 근거 없으면 호출하지 않아 환각(없는 규정 인용)을 막음.
  - 여러 위험을 하나로 뭉치지 않고 `risks[]`로 분리 → 위험별 근거·상태를 따로 관리.

### 기술 스택 (역할별)
- **API:** FastAPI (Pydantic 입력 검증, `/audit`, `/audit/batch`, `/audit-results`, `/review`)
- **데이터:** PostgreSQL (일반 컬럼 + `risks` JSONB), pgVector(규정 벡터 검색)
- **RAG/LLM:** Gemini Embedding + LLM, Template Fallback
- **워크플로:** LangGraph(State/Node/Conditional Edge) — **독립 구현**
- **테스트·운영:** pytest + GitHub Actions, Docker/Compose, JSONL 로깅

---

## [2페이지] 검증 · 기술 의사결정 · 한계

### 직접 구현한 증거 3개 (실행/테스트로 확인된 것만)
1. **복수 위험 분리 + 위험별 근거/초안** — `docs/evidence/02_api_contract.md` (실제 탐지 출력)
2. **Human-in-the-loop E2E** — POST→GET→PATCH 통합 테스트 3개 실DB PASS (`04`, `09`)
3. **실패 처리 매트릭스** — 근거없음→needs_review / LLM예외→template / DB실패→거짓성공 금지(500) / 422 (`04`)

### 측정 수치 (한계 표기 포함)
- **비통합 테스트 13 PASS / 통합 3 PASS** (CI는 비통합 범위).
- **독립 평가(규정 기준 수기 정답) 12건: Precision/Recall/F1 = 1.000** — *소표본·경계값 검증이며 실사용 전반 정확도는 아님.*
- **RAG Hit@3** (13절): 당시 측정 기록. *검색 성공률 지표이며 평가 질의는 자동 생성 — 실사용 질의와 다름.*
- ⚠️ **1,000건 테스트는 "회귀"** (기대값=코드 출력) — "정확도 100%"로 표현하지 않음.

### 기술 의사결정 3개
1. **규칙 기반 위험 판정** — 재현성·설명가능성 (금액/영수증은 LLM이 아니라 임계값으로).
2. **RAG 근거 제시** — 담당자가 "왜 위험인가"를 규정으로 확인 → 검수 지원.
3. **Human Review + Fallback** — AI가 최종 결정하지 않음, 외부 실패에도 업무 중단 없음.

### 명확한 미완료 (정직)
- LangGraph **API 실연결** 미완(독립 구현 상태).
- Sheets→n8n→API E2E, **클라우드 배포** 미검증(설계/Runbook 보유).
- 사용자 **인증/권한** 미구현. 실사용 정확도·ERP 연동 미검증.

### 링크
- GitHub: https://github.com/wooya27/Cost_Manager  (QR 삽입 자리)
- 실행 방법: README 10절 / 데모: Swagger `/docs`

---

### A4 2페이지 내보내기 체크 (본인)
- [ ] 캡처 4컷(입력→위험2개→저장 id→PATCH 결과) 붙이기
- [ ] 글자 잘림 없음, QR 스캔됨, URL 접근됨
- [ ] 숫자·문구가 코드/README와 일치 (실측만)
