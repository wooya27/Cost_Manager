# 프로그램의 작업 일지를 남기는 것.
import json
from datetime import datetime
from pathlib import Path


def log_workflow(state, error_message=None):
    # logs 폴더가 없으면 자동 생성
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / "llm_calls.jsonl"

    log_data = { # 로그 파일에 어떤 내용을 적을지 하나의 묶음으로 정리한다.
        "timestamp": datetime.now().isoformat(), # = 2026-09-22T22:10:00
        "risk_type": state.get("risk_type"), 
        "risk_reason": state.get("risk_reason"),
        "has_policy_evidence": bool(state.get("policy_evidence")),
        "draft_message": state.get("draft_message"),
        "draft_source": state.get("draft_source"),
        "llm_success": None,
        "fallback_used": False,
        "error_message": error_message
    }

    with open(log_file, "a", encoding="utf-8") as f: # "a"는 append야. 기존 내용을 지우지 말고 맨 밑에 추가해라. 로그기록이 아래로 계속 쌓이게
        f.write(
            json.dumps(log_data, ensure_ascii=False)
            + "\n"
        )