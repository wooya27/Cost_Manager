# 09 · DAY 1 마감표 (B09)

> 기록일: 2026-11-07 (KST)

| 항목 | 값 |
|---|---|
| 선택한 데모 경로 | **기존 `/audit` (api/main.py)** — LangGraph는 독립 구현/API 미연동 (결정 B, `03_...`) |
| 기준 커밋(작업 전) | `281adbd 작업 보강전` (브랜치 `work_v2/end_to_end`) |
| 로컬 테스트 | `pytest -m "not integration"` → **13 passed, 3 deselected** |
| 통합 테스트(별도) | `pytest -m integration` → **3 passed** (실시간 DB) |
| `git diff --check` | clean (공백/충돌표식 없음) |
| CI | ⚠️ **미반영** — 아직 commit/push 안 함(사용자 승인 대기). 새 커밋 후 CI URL 확인 필요 |

## DAY 1 종료 게이트 (4개 중 3개 이상 → 달성)
- [x] ① POST→GET→PATCH 시연 (integration 테스트 3개 PASS)
- [x] ② 복수 위험 결과 (합성 사례 A: 2개 분리, `02_...`)
- [x] ③ 실패 테스트 ≥1개 (근거없음/LLM실패/DB실패/422, `04_...`)
- [x] ④ 구현/미구현 명세 (Graph 독립구현 표기, `03_...`)

## 변경 파일 (커밋 대기)
```
 M src/agent_workflow.py      # retrieve_node processed_risks 누적, 상태값 통일, 레거시 제거
 M src/database.py            # create_tables에 vector 확장 + policy_chunks
 M tests/test_audit.py        # B07 실패 테스트 2개
?? tests/test_workflow.py     # Graph Mock 테스트 2개
?? scripts/evaluate_risks.py  # 독립 평가 P/R/F1
?? tests/data/independent_cases.csv, independent_expected.csv
?? docs/evidence/             # 01~05, 09 증거
?? study/portfolio_11.08_blocks.md
 M logs/node_calls.jsonl      # ⚠️ 런타임 로그 — .gitignore 대상(정리 필요)
```

## 내일(DAY2) 시연에 쓸 확실한 증거 3개
1. 복수 위험 실제 출력 (`02_api_contract.md`)
2. 독립 평가 P/R/F1=1.000 + 회귀와 구분 (`05_evaluation.md`)
3. 실패 매트릭스 4종 테스트 PASS (`04_failure_matrix.md`)

## 미완료 / 다음
- commit/push + CI 재확인 (사용자 승인 후)
- `logs/*.jsonl` gitignore 처리, 빈 placeholder CSV 정리 (B09 저장소 정리 잔여)
- DAY2: README 갱신, 포트폴리오 2p, 데모 캡처/영상, 면접 Q&A (B10~B18)

## 상태: 완료 (commit/push·CI만 대기)
