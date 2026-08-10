---
description: 현재 변경사항을 code-reviewer 에이전트로 리뷰합니다
argument-hint: "[대상 브랜치 또는 파일 경로 (선택)]"
allowed-tools: Read, Grep, Glob, Bash(git diff:*), Bash(git status:*), Task
---

현재 작업 중인 변경사항을 리뷰해줘.

대상: $ARGUMENTS (비어 있으면 워킹 트리 전체)

`code-reviewer` 서브에이전트를 사용해 리뷰를 수행하고,
심각도별로 정리된 결과를 보여줘.
