---
description: main 브랜치에 add → commit → push 하고 코드 리뷰까지 한 번에 처리하는 커맨드
allowed-tools: Bash, Read, Glob, Grep, Task
---

# /push

변경된 코드를 리뷰하고 커밋한 뒤 원격(main)에 푸시합니다.
AuditFlow AI는 1인 개발 · 브랜치 `main` 하나 전제입니다 (dev 브랜치·PR 없음).

사용법:
- `/push` — 변경사항 확인 후 커밋 메시지 제안
- `/push feat: 우선순위 규칙 엔진 추가` — 커밋 메시지 직접 지정

## 실행 순서

### Step 1: 최신 코드 동기화 (pull)

```bash
git branch --show-current   # main 인지 확인
git pull origin main
```

- 충돌(conflict)이 발생하면 사용자에게 알리고 중단한다
- 충돌 없이 성공하면 다음 단계로 진행한다

### Step 2: 현재 상태 파악

```bash
git status
git diff --stat
git log --oneline -5
```

- 변경된 파일 목록과 diff를 확인한다

### Step 3: 코드 리뷰 (커밋 전)

`code-reviewer` 서브에이전트로 변경사항을 검토한다. 심각도 기준:
- **CRITICAL** — 보안 취약점, 데이터 손실 위험
- **HIGH** — 버그, 잘못된 로직
- **MEDIUM** — 성능, 가독성
- **LOW** — 스타일, 네이밍

CRITICAL/HIGH 이슈가 있으면 수정을 권고하고, 계속 진행할지 사용자에게 확인한다.

### Step 4: 중간 보고서 작성 (선택)

변경이 큰 경우 `docs/reports/YYYY-MM-DD.md` 에 보고서를 저장한다. 작은 변경이면 건너뛴다.

```markdown
# 중간 보고서 — <날짜>

## 변경 요약
- 변경된 파일 목록과 각 파일의 변경 목적

## 중간 평가
| 항목 | 상태 | 비고 |
|------|------|------|
| 기능 구현 완성도 | 🟢 완료 / 🟡 부분 / 🔴 미완 | |
| 테스트 작성 여부 | 🟢 / 🟡 / 🔴 | |
| 문서 업데이트 여부 | 🟢 / 🟡 / 🔴 | |
| 보안 이슈 없음 | 🟢 / 🔴 | |

## 잘 된 점 / 개선 필요 / 다음 작업
- (상세계획의 다음 블록과 연결)
```

### Step 5: git add

변경 파일을 확인하고 관련 파일만 스테이징한다.
민감한 파일(`.env`, 시크릿 포함 파일)은 절대 포함하지 않는다.

```bash
git add <관련 파일들>
# git add -A 는 사용하지 않음 — 민감 파일 방지
```

### Step 6: git commit

커밋 메시지 규칙 (Conventional Commits):
- `feat:` 새 기능
- `fix:` 버그 수정
- `test:` 테스트 추가·수정
- `docs:` 문서
- `refactor:` 리팩터링
- `chore:` 빌드·설정

ARGUMENTS에 커밋 메시지가 있으면 그대로 사용한다.
없으면 변경 내용을 분석해서 적절한 커밋 메시지를 제안하고 확인 후 커밋한다.

```bash
git commit -m "<커밋 메시지>"
```

### Step 7: git push

```bash
git push origin main
```

## 완료 메시지

```
✅ Push 완료
브랜치: main
커밋:   feat: xxx
리뷰:   CRITICAL 0 / HIGH 0 / MEDIUM N / LOW N
원격:   https://github.com/wooya27/Cost_Manager
```
