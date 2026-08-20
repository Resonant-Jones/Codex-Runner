from __future__ import annotations

import json
from pathlib import Path

from codex_runner import mcp_server


PLUGIN_ROOT = Path(__file__).parents[1] / "plugins" / "codex-runner"


def test_codex_runner_plugin_binds_to_the_dry_run_mcp_server() -> None:
    manifest = json.loads(
        (PLUGIN_ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
    )
    mcp_manifest = json.loads(
        (PLUGIN_ROOT / ".mcp.json").read_text(encoding="utf-8")
    )

    assert manifest["name"] == "codex-runner"
    assert manifest["mcpServers"] == "./.mcp.json"
    assert mcp_manifest["mcpServers"]["codex-runner"]["command"] == "codexrun-mcp"
    assert (
        PLUGIN_ROOT / "skills" / "codex-runner-delegation" / "SKILL.md"
    ).is_file()
    assert mcp_server.TOOL_NAME == "codex_runner_campaign_dry_run"
