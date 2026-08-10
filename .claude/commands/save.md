---
description: 작업 중 변경사항을 add → commit으로 중간 저장하는 커맨드 (push는 안 함)
allowed-tools: Bash, Read, Glob, Grep
---

# /save

작업 중 변경사항을 빠르게 중간 저장합니다. push는 하지 않습니다 (push는 `/push`).
AuditFlow AI는 1인 개발 · 브랜치 `main` 하나 전제입니다.

사용법:
- `/save` — 변경사항 확인 후 커밋 메시지 제안
- `/save wip: 우선순위 규칙 엔진 작성 중` — 커밋 메시지 직접 지정

## 실행 순서

### Step 1: 현재 상태 파악

```bash
git branch --show-current   # main 인지 확인
git status
git diff --stat
```

- 변경된 파일 목록을 확인한다
- 민감한 파일(`.env`, 시크릿 포함 파일)이 있으면 사용자에게 알리고 제외한다

### Step 2: git add

관련 파일만 스테이징한다.

```bash
git add <관련 파일들>
# git add -A 는 사용하지 않음 — 민감 파일 방지
```

### Step 3: git commit

ARGUMENTS에 커밋 메시지가 있으면 그대로 사용한다.
없으면 변경 내용을 분석해서 적절한 커밋 메시지를 제안하고 확인 후 커밋한다.

커밋 메시지 규칙 (Conventional Commits):
- `feat:` 새 기능
- `fix:` 버그 수정
- `test:` 테스트 추가·수정
- `docs:` 문서
- `refactor:` 리팩터링
- `chore:` 빌드·설정
- `wip:` 작업 중 (Work In Progress)

```bash
git commit -m "<커밋 메시지>"
```

## 완료 메시지

```
💾 중간 저장 완료
브랜치: main
커밋:   <커밋 메시지>
(push는 /push 커맨드로 별도 실행)
```
