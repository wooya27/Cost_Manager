# 내가(본인) 직접 해야 할 일 — 11/09 박람회

> Claude가 할 수 없는 부분만 모음. 코드·문서·테스트는 이미 완료(커밋/push됨).
> 참고 파일: `docs/portfolio_content.md`, `docs/interview_prep.md`, `docs/evidence/`

## 🔴 필수 (이것만 되면 최소 합격)

- [ ] **CI 결과 확인** — GitHub 저장소 → **Actions 탭** → 최신 커밋 `d766496`이 ✅ 초록인지 확인. (이 URL을 포트폴리오에 넣기)
- [ ] **데모 캡처 4컷** (Swagger `/docs`에서. 먼저 `docker compose up -d`로 DB·API 켜기)
  - ① `POST /audit` 합성 1건 입력 → ② 위험 2개+근거+초안 응답 → ③ 저장된 `id` → ④ `PATCH /audit-results/{id}/review` 후 상태 바뀐 결과
  - 요청 JSON: `docs/portfolio_content.md` / 11.08 계획 2절
- [ ] **포트폴리오 2페이지 PDF** — `docs/portfolio_content.md` 내용 + 캡처 4컷 → A4 2p PDF. (글자 잘림·QR 스캔·URL 접근 확인)
- [ ] **30초 자기소개 / 60초 프로젝트 설명** 녹음 2회씩

## 🟡 여유 되면 (가산점)

- [ ] **면접 질문 10개 구술 연습** — `docs/interview_prep.md` 보고 종이 없이. 막힌 3개를 `docs/evidence/08_interview_weakness.md`에 채우기
- [ ] **30~60초 데모 영상** (캡처로 대체 가능, 15분 넘으면 캡처 선택)
- [ ] **회사별 20초 멘트** 입에 붙이기 — `docs/interview_prep.md` 하단

## 🟢 행사 이후 (지금 안 해도 됨)

- [ ] n8n 실제 E2E 연동 — 절차 `docs/evidence/06_n8n_status.md`
- [ ] 클라우드 배포 (Render/Neon 등) — 절차 `docs/evidence/07_runbook.md`
- [ ] Streamlit UI를 `risks[]` 구조로 재작업 (현재 Swagger가 공식 데모)

## ⚠️ 영상/캡처 올리기 전 보안 체크
- `GEMINI_API_KEY`, DB 비밀번호, 토큰, 실명, Slack Webhook 화면에 안 보이게
- **합성 데이터만** 사용
