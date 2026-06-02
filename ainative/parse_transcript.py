"""transcript 파서 — Claude Code 세션 JSONL → 결정적 행동 신호.

stdlib only. 추정 아니라 실제 JSONL 구조에 맞춰 방어적으로 파싱.
레코드 type: user|assistant|system|file-history-snapshot|ai-title|... (관심 외는 무시).
message.content: str | list[block]. 블록 type: text|thinking|tool_use|tool_result.

핵심 신호:
  - tools_per_prompt, autonomous_chain   → D1 위임 고도
  - distinct_tools, agent/task 호출       → D4 오케스트레이션
  - repeated_edit_files                   → D6 반복(비효율 신호)
  - interrupts                            → D6/D2
"""
import json
import sys
from pathlib import Path
from collections import Counter

SKIP_TYPES = {"file-history-snapshot", "summary"}
ORCHESTRATION_TOOLS = {"Agent", "Task", "Workflow"}
EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}


def iter_records(path):
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue  # 손상 라인 방어
    except (OSError, UnicodeDecodeError):
        return


def _content(rec):
    return (rec.get("message") or {}).get("content")


def _is_interrupt(rec):
    c = _content(rec)
    return isinstance(c, str) and "[Request interrupted" in c


def _is_tool_result_carrier(content):
    return isinstance(content, list) and any(
        isinstance(b, dict) and b.get("type") == "tool_result" for b in content
    )


def _edit_path(block):
    inp = block.get("input") or {}
    return inp.get("file_path") or inp.get("path") or inp.get("notebook_path")


def analyze_session(path):
    """단일 세션 JSONL → 신호 dict."""
    rec_types = Counter()
    block_types = Counter()
    tool_uses = Counter()
    edit_targets = Counter()
    user_prompts = 0
    assistant_turns = 0
    thinking_blocks = 0
    interrupts = 0
    chains = []
    cur_chain = 0

    for rec in iter_records(path):
        t = rec.get("type")
        rec_types[t] += 1
        if t in SKIP_TYPES or rec.get("isMeta"):
            continue
        content = _content(rec)

        if t == "user":
            if _is_interrupt(rec):
                interrupts += 1
                continue
            if _is_tool_result_carrier(content):
                continue
            user_prompts += 1
            if cur_chain:
                chains.append(cur_chain)
                cur_chain = 0

        elif t == "assistant" and isinstance(content, list):
            assistant_turns += 1
            for b in content:
                if not isinstance(b, dict):
                    continue
                bt = b.get("type")
                block_types[bt] += 1
                if bt == "tool_use":
                    name = b.get("name", "?")
                    tool_uses[name] += 1
                    cur_chain += 1
                    if name in EDIT_TOOLS:
                        p = _edit_path(b)
                        if p:
                            edit_targets[p] += 1
                elif bt == "thinking":
                    thinking_blocks += 1

    if cur_chain:
        chains.append(cur_chain)

    total_tools = sum(tool_uses.values())
    repeated = {f: n for f, n in edit_targets.items() if n >= 3}
    return {
        "file": Path(path).name,
        "record_types": dict(rec_types),
        "block_types": dict(block_types),
        "user_prompts": user_prompts,
        "assistant_turns": assistant_turns,
        "thinking_blocks": thinking_blocks,
        "interrupts": interrupts,
        "tool_uses_total": total_tools,
        "tool_distribution": dict(tool_uses.most_common()),
        "distinct_tools": len(tool_uses),
        "orchestration_calls": sum(tool_uses[t] for t in ORCHESTRATION_TOOLS),
        "tools_per_prompt": round(total_tools / user_prompts, 2) if user_prompts else 0.0,
        "max_autonomous_chain": max(chains) if chains else 0,
        "avg_autonomous_chain": round(sum(chains) / len(chains), 2) if chains else 0.0,
        "repeated_edit_files": repeated,
    }


def aggregate(paths):
    """여러 세션 → 집계 신호 + 세션별 목록(근거용)."""
    sessions = [analyze_session(p) for p in paths]
    sessions = [s for s in sessions if s["user_prompts"] or s["tool_uses_total"]]

    tool_dist = Counter()
    for s in sessions:
        tool_dist.update(s["tool_distribution"])

    tot_prompts = sum(s["user_prompts"] for s in sessions)
    tot_tools = sum(s["tool_uses_total"] for s in sessions)
    chains_max = [s["max_autonomous_chain"] for s in sessions if s["max_autonomous_chain"]]
    repeated_total = sum(len(s["repeated_edit_files"]) for s in sessions)

    return {
        "n_sessions": len(sessions),
        "total_user_prompts": tot_prompts,
        "total_tool_uses": tot_tools,
        "tools_per_prompt": round(tot_tools / tot_prompts, 2) if tot_prompts else 0.0,
        "distinct_tools": len(tool_dist),
        "tool_distribution": dict(tool_dist.most_common()),
        "orchestration_calls": sum(tool_dist[t] for t in ORCHESTRATION_TOOLS),
        "max_autonomous_chain": max(chains_max) if chains_max else 0,
        "avg_max_chain": round(sum(chains_max) / len(chains_max), 1) if chains_max else 0.0,
        "total_thinking_blocks": sum(s["thinking_blocks"] for s in sessions),
        "total_interrupts": sum(s["interrupts"] for s in sessions),
        "repeated_edit_sessions": repeated_total,
        "sessions": sessions,
    }


def discover(projects_root):
    """~/.claude/projects 아래 모든 *.jsonl (메인+서브에이전트+워크플로)."""
    root = Path(projects_root)
    return [str(p) for p in root.rglob("*.jsonl")] if root.exists() else []


if __name__ == "__main__":
    import pprint
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    pprint.pprint(aggregate(sys.argv[1:]))
