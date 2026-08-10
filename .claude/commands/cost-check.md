---
description: LLM(주간 리포트 개선 제안) 호출의 토큰·JSON/fallback 품질을 점검합니다.
allowed-tools: Bash, Read, Grep, Glob
---

# /cost-check

AuditFlow AI의 LLM 호출을 점검합니다.

AuditFlow AI에서 LLM은 **주간 리포트 개선 제안(F-08 / SR-07)** 한 곳에서만 쓰이고,
**주 1회** 호출됩니다. 그래서 비용 자체는 이미 매우 낮고, 진짜로 볼 것은
**출력 품질(JSON 고정 + fallback)** 과 **호출 로그(llm_logs)** 입니다.
계산은 규칙 엔진이 하고 LLM은 해석·제안만 하므로, 프롬프트에는 KPI '근거'만 넣습니다.

## 사용법

`/cost-check` — LLM 서비스(`backend/app/services/llm_service.py`, 아직 미구현 시 계획 기준) 작성·수정 후 실행.

## 실행 순서

### Step 1 — LLM 호출 지점 확인

```bash
# 프로젝트에서 LLM을 호출하는 위치 찾기
grep -rn "anthropic\|messages.create\|llm_service" backend/app 2>/dev/null
```

호출이 리포트 생성 경로(F-07→F-08) 한 곳에만 있는지 확인한다. 계산 로직(우선순위·집계)에
LLM이 끼어 있으면 안 된다 — 수치 환각 방지 원칙 위반.

### Step 2 — 품질 체크리스트

- [ ] **JSON schema 고정** — 개선 제안 응답을 정해진 JSON 스키마로 파싱하는가?
- [ ] **fallback 경로** — 파싱 실패·timeout 시 규칙 기반 문장으로 대체하는가? (1경로)
- [ ] **프롬프트 최소화** — KPI 수치·지연 원인 TOP3 등 '근거'만 넣고, 원본 로그를 통째로 넣지 않는가?
- [ ] **timeout 설정** — LLM 호출에 timeout 값이 지정돼 있는가?
- [ ] **llm_logs 기록** — 매 호출마다 input/output 토큰·성공여부·fallback여부를 `llm_logs` 테이블에 남기는가?

### Step 3 — 호출 로그 확인 (llm_logs)

```bash
# 최근 LLM 호출 기록 (컨테이너의 PostgreSQL 조회)
docker exec cost_manager-db psql -U cost_manager -d cost_manager -c \
  "SELECT created_at, input_tokens, output_tokens, is_fallback FROM llm_logs ORDER BY created_at DESC LIMIT 10;"
```

> `llm_logs` 테이블이 아직 없으면 이 단계는 건너뛴다 (LLM 단계는 상세계획 8/18 블록).

### Step 4 — AI 품질 KPI 기록

| 지표 | 값 | 목표 |
|---|---|---|
| JSON 파싱 성공률 | ?% | 높을수록 좋음 |
| fallback 발생률 | ?% | 낮을수록 좋음 |
| 호출당 평균 input 토큰 | ? | 리포트 1건이라 과도하지 않게 |

---

## 참고: AuditFlow AI의 비용 판단

- **주 1회 호출** 규모라 토큰 절감·캐싱·모니터링은 **최소 적용**(기획서 §2.8, §6.11).
- 따라서 이 커맨드의 핵심은 "비용 절감"보다 **"환각 없는 안정적 JSON 출력"** 검증이다.
- 대규모 RAG/캐시/토큰 최적화 역량은 AuditFlow AI가 아니라 Dev2 트랙에서 다룬다.
