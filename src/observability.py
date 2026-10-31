# 프로그램의 작업 일지를 남기는 것.
import json
from datetime import datetime
from pathlib import Path


def log_workflow(state, error_message=None):

    # logs 폴더가 없으면 자동 생성
    log_dir = Path("logs")
    log_dir.mkdir(
        exist_ok=True
    )

    log_file = log_dir / "llm_calls.jsonl"

    risks = state.get(
        "risks",
        []
    )

    if risks:
        risk = risks[0]
        risk_type = risk.get("risk_type")
        risk_reason = risk.get("risk_reason")

    else:
        risk_type = None
        risk_reason = None

    error = (
        error_message
        or state.get("error")
        or None
    )

    draft_source = state.get(
        "draft_source"
    )

    log_data = {
        "timestamp": datetime.now().isoformat(),
        "run_id": state.get("run_id"),
        "audit_id": state.get("audit_id"),
        "risk_type": risk_type,
        "risk_reason": risk_reason,
        "has_policy_evidence": bool(
            state.get("policy_evidence")
        ),
        "draft_message": state.get(
            "draft_message"
        ),
        "draft_source": draft_source,
        "retry_count": state.get(
            "retry_count",
            0
        ),
        "llm_success": (
            draft_source == "llm"
        ),
        "fallback_used": (
            draft_source == "template"
        ),
        "error_message": error
    }

    with open(
        log_file,
        "a",
        encoding="utf-8"
    ) as f:

        f.write(
            json.dumps(
                log_data,
                ensure_ascii=False
            )
            + "\n"
        )

def log_node(state, node_name,latency_ms=None):

    log_dir = Path("logs")
    log_dir.mkdir(
        exist_ok=True
    )

    log_file = log_dir / "node_calls.jsonl"

    log_data = {
        "timestamp": datetime.now().isoformat(),
        "run_id": state.get("run_id"),
        "node": node_name,
        "latency_ms": latency_ms
    }

    with open(
        log_file,
        "a",
        encoding="utf-8"
    ) as f:

        f.write(
            json.dumps(
                log_data,
                ensure_ascii=False
            )
            + "\n"
        )        