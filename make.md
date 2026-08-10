이 프로젝트에 Claude Code 초기 세팅 구조를 만들어줘. 아래 파일들을 정확히 이 구조로 생성해줘.

## 만들 구조

your-project/
├── CLAUDE.md
├── .gitignore
└── .claude/
    ├── settings.json
    ├── settings.local.json
    ├── agents/
    │   └── code-reviewer.md
    ├── commands/
    │   
    ├── skills/
    │   
    │      
    ├── plans/
    │   
    └──

## 각 파일 내용

### .claude/settings.json — 아래 내용 그대로 넣어줘
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [
      "Bash(npm run test:*)",
      "Bash(npm run lint)",
      "Bash(git status)",
      "Bash(git diff:*)",
      "Bash(git log:*)"
    ],
    "ask": [
      "Bash(git push:*)",
      "Bash(npm install:*)"
    ],
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)",
      "Bash(rm -rf:*)",
      "Bash(curl:*)",
      "Bash(git push --force:*)"
    ]
  },
  "defaultMode": "acceptEdits"
}

### CLAUDE.md
프로젝트 개요/스택/명령어/폴더구조/컨벤션/주의사항 섹션을 가진 템플릿으로.
내가 나중에 채울 수 있게 예시 자리표시자를 넣어줘. 200줄 넘지 않게 간결하게.

### .claude/settings.local.json
개인 설정용. permissions에 빈 allow/ask/deny 배열만 넣은 틀로. git에 커밋 안 한다는 주석 포함.

### .claude/agents/

### .claude/commands/
### .claude/skills/

### .claude/hooks/


### .claude/plans/
### .gitignore
.claude/settings.local.json, .env, .env.*, secrets/, node_modules/, 빌드산출물 제외.
단 .env.example은 예외로 포함.

## 마지막
전부 만든 뒤 생성된 파일 목록을 트리 구조로 보여주고,
각 파일이 뭐 하는 건지 한 줄씩 요약해줘.
파일 만들기 전에 계획을 먼저 보여주고 내 확인을 받아줘.