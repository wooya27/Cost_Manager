# 06 · n8n 자동화 상태 (DAY2 B11)

> 기록일: 2026-11-07 (KST) · 11.08 계획 B11 + 10.17 Day5

## 저장된 워크플로 파일

### `n8n/AuditFlow - Expense Workflow.json` (5노드)
`manualTrigger → Google Sheets(행 읽기) → HTTP Request → IF → Google Sheets(행 추가)`

### `n8n/AuditFlow Error Handler.json` (2노드)
`Error Trigger → Google Sheets(행 추가)` — 실패 시 시트에 기록

## 점검 결과

| 항목 | 상태 | 비고 |
|---|---|---|
| HTTP Request 메서드/URL | POST `http://host.docker.internal:8000/audit` | **로컬 URL** (클라우드 아님) |
| 필드 매핑 (Pydantic 8필드) | ✅ 정확 | employee/department/category/amount/date/vendor/reason/has_receipt 전부 매핑 |
| amount 타입 | ✅ | `{{ $json.amount }}` 따옴표 없이 숫자 전송 → `int` OK (422 안 남) |
| 비밀키/토큰 하드코딩 | ✅ 없음 | n8n 자격증명은 JSON 밖에 저장. Bearer/apiKey/token/webhook 미검출 |
| IF 분기 | ✅ | `risk_type` notEmpty → 위험/정상 분기 |
| Error 워크플로 | △ 설계 있음 | 실패→시트 기록. Retry On Fail 노드 옵션은 별도 확인 필요 |
| 민감정보 | ⚠️ | Google Sheets `documentId` 2곳 포함 — 공개 저장소면 본인 시트 id 노출 여부 확인 |

## 현재 상태 표기 (정직)
> **"워크플로 설계/설정 파일 보유, Pydantic 필드 매핑 정확. 단 HTTP URL이 로컬(host.docker.internal)이고,
> 실제 Sheets→n8n→API→Sheets E2E는 본인 n8n 인스턴스·구글 자격증명이 있어야 재현 가능 → 현재 세션에서 E2E 미검증."**

## 본인이 해야 하는 것 (E2E 성공시키려면)
1. n8n 인스턴스에서 두 JSON import.
2. Google Sheets 자격증명 연결(OAuth) + 대상 시트 지정.
3. API가 클라우드면 HTTP URL을 `host.docker.internal` → 배포 URL로 변경.
4. 합성 비용 1건을 시트에 넣고 수동 실행 → 응답 행이 추가되는지 확인.
5. 성공한 **마지막 노드까지만** 증거로 기록(전체 E2E 성공을 추정하지 않음).

## 30초 설명
> "FastAPI는 실제 검수 로직을 수행하는 API, LangGraph는 그 로직의 상태·분기·실패 경로를 관리하는 구현,
> n8n은 Google Sheets 같은 외부 업무도구와 API를 잇는 오케스트레이션이다. 지금 n8n은 로컬 API를 향한
> 설계가 완성돼 있고, 클라우드 URL 교체와 자격증명 연결이 E2E 재현의 남은 조건이다."

## 상태: 부분 완료 (설계·매핑 검증 / E2E는 본인 환경 필요)
