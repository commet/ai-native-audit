"""정적 스캔 — ~/.claude + 프로젝트 .claude 인벤토리 → D4/D7 즉시 신호.

워크플로를 직접 instrument 했는가 = AI-native의 강한 선행지표(자산 복리 D7,
오케스트레이션 D4). 제품 설치 행위 자체가 이 축의 증거가 되는 재귀 구조.
파일 *존재·개수·구조*만 봄 — 내용(민감)은 안 읽음.
"""
import json
import os
from pathlib import Path


def _count_files(d, suffixes=None):
    d = Path(d)
    if not d.exists():
        return 0
    out = 0
    for p in d.rglob("*"):
        if p.is_file() and (suffixes is None or p.suffix in suffixes):
            out += 1
    return out


def _hooks_count(settings_path):
    p = Path(settings_path)
    if not p.exists():
        return 0
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return 0
    hooks = data.get("hooks") or {}
    return sum(len(v) for v in hooks.values() if isinstance(v, list))


def _mcp_count(settings_paths):
    total = 0
    for sp in settings_paths:
        p = Path(sp)
        if not p.exists():
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        servers = data.get("mcpServers") or {}
        total += len(servers)
    return total


def scan(home=None, project=None):
    """home=~/.claude 부모, project=현재 프로젝트 루트. 인벤토리 dict."""
    home = Path(home or Path.home())
    claude = home / ".claude"
    proj = Path(project or os.getcwd())

    inv = {
        "skills": _count_files(claude / "skills") + _count_files(claude / "plugins"),
        "commands": _count_files(claude / "commands", {".md"}),
        "agents": _count_files(claude / "agents", {".md"}),
        "global_hooks": _hooks_count(claude / "settings.json"),
        "project_hooks": _hooks_count(proj / ".claude" / "settings.json")
        + _hooks_count(proj / ".claude" / "settings.local.json"),
        "mcp_servers": _mcp_count([
            claude / "settings.json", proj / ".mcp.json",
            proj / ".claude" / "settings.json",
        ]),
        "has_global_claude_md": (claude / "CLAUDE.md").exists(),
        "has_project_claude_md": (proj / "CLAUDE.md").exists()
        or (proj / ".claude" / "CLAUDE.md").exists(),
        "memory_files": _count_files(claude / "memory", {".md"}),
        "has_memory_index": (claude / "memory" / "MEMORY.md").exists()
        or any((claude / "projects").rglob("MEMORY.md")) if (claude / "projects").exists() else False,
    }
    # "build" 자산 총량 (D7 복리 핵심)
    inv["build_assets"] = (
        inv["skills"] + inv["commands"] + inv["agents"]
        + inv["global_hooks"] + inv["project_hooks"] + inv["mcp_servers"]
    )
    return inv


if __name__ == "__main__":
    import sys, pprint
    pprint.pprint(scan(project=sys.argv[1] if len(sys.argv) > 1 else None))
