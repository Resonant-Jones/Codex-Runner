from __future__ import annotations

import datetime as _dt
import json
import re
from pathlib import Path
from typing import Any

from .plan_pack_validator import AUTHORITY_LOCKS, GuardianPlanPackReport

SESSION_SCHEMA_VERSION = "v0"
SESSION_TYPE = "guardian_plan_pack_validation"


def timestamp_utc() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def safe_slug(text: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", text.strip().lower()).strip("-")
    return slug or "session"


def build_session_log_payload(
    report: GuardianPlanPackReport,
    *,
    command: str,
    created_at: str,
    notes: str = "",
) -> dict[str, Any]:
    return {
        "session_type": SESSION_TYPE,
        "schema_version": SESSION_SCHEMA_VERSION,
        "created_at": created_at,
        "plan_pack_path": str(report.plan_pack_path),
        "command": command,
        "validation": {
            "valid": report.valid,
            "result": report.result,
            "reason": report.reason,
        },
        "authority": dict(AUTHORITY_LOCKS),
        "notes": notes,
    }


def write_session_log(
    report: GuardianPlanPackReport,
    *,
    command: str,
    sessions_dir: Path,
    notes: str = "",
) -> Path:
    created_at = timestamp_utc()
    payload = build_session_log_payload(
        report, command=command, created_at=created_at, notes=notes
    )
    slug = safe_slug(report.plan_pack_path.name)
    filename = f"{created_at}-validate-plan-pack-{slug}.json"
    sessions_dir.mkdir(parents=True, exist_ok=True)
    path = sessions_dir / filename
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path
