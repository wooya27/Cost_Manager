---
description: 원격 main 브랜치의 최신 변경사항을 로컬로 가져옵니다
allowed-tools: Bash
---

# /pull

원격 `origin/main`의 최신 변경사항을 로컬 `main`으로 가져옵니다.
AuditFlow AI는 1인 개발 · 브랜치 `main` 하나 전제입니다. (여러 기기에서 작업하거나
원격에서 직접 수정한 경우 로컬을 최신화할 때 사용)

## 실행 순서

1. **현재 브랜치 확인**
   ```bash
   git branch --show-current
   ```

2. **로컬 미커밋 변경사항 확인** — 변경사항이 있으면 stash를 권장하고 진행 여부를 물어보세요.
   ```bash
   git status
   git diff
   ```

3. **원격 최신화**
   ```bash
   git fetch origin main
   ```

4. **차이 미리 확인** (머지 전)
   ```bash
   git diff HEAD origin/main
   ```

5. 충돌이 예상되면 충돌 파일 목록을 보여주고 진행 여부를 사용자에게 물어보세요.
   충돌이 없으면 바로 가져옵니다 (선형 히스토리 우선).
   ```bash
   git pull --ff-only origin main
   ```
   - `--ff-only`가 거부되면(로컬에 별도 커밋 존재) 사용자에게 알리고
     `git pull origin main`(머지) 진행 여부를 확인한다.

6. **충돌 발생 시** 충돌 파일 목록과 해결 방법을 안내하세요.
   ```bash
   git status
   ```

7. **성공 시 변경 요약** — 어떤 파일이 추가/수정/삭제됐는지 출력하세요.
   ```bash
   git diff --stat HEAD@{1} HEAD
   ```
