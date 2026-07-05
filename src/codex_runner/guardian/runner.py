from __future__ import annotations

import argparse
import json
from pathlib import Path

from .plan_pack_validator import render_report, validate_plan_pack
from .receipt import write_receipt
from .session_log import write_session_log

DEFAULT_SESSIONS_DIR = Path(".guardian/sessions")
DEFAULT_RECEIPTS_DIR = Path(".guardian/receipts")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Guardian support tools")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser(
        "validate-plan-pack",
        help="Validate a Guardian plan pack without executing it",
    )
    validate_parser.add_argument(
        "--path",
        type=Path,
        required=True,
        help="Path to the Guardian plan pack directory",
    )
    validate_parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON report output",
    )
    validate_parser.add_argument(
        "--write-session-log",
        action="store_true",
        help="Write a generated session log under .guardian/sessions/",
    )
    validate_parser.add_argument(
        "--write-receipt",
        action="store_true",
        help="Write a generated validation receipt under .guardian/receipts/",
    )
    return parser


def _format_command(args: argparse.Namespace) -> str:
    parts = [
        "codexrun",
        "guardian",
        "validate-plan-pack",
        "--path",
        str(args.path),
    ]
    if args.json:
        parts.append("--json")
    if args.write_session_log:
        parts.append("--write-session-log")
    if args.write_receipt:
        parts.append("--write-receipt")
    return " ".join(parts)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command != "validate-plan-pack":
        raise ValueError(f"unsupported guardian command: {args.command}")

    report = validate_plan_pack(args.path)
    if args.write_session_log:
        write_session_log(
            report,
            command=_format_command(args),
            sessions_dir=DEFAULT_SESSIONS_DIR,
        )
    if args.write_receipt:
        write_receipt(
            report,
            command=_format_command(args),
            receipts_dir=DEFAULT_RECEIPTS_DIR,
        )
    if args.json:
        print(json.dumps(report.to_json_dict(), indent=2))
    else:
        print(render_report(report), end="")
    return 0 if report.valid else 1
