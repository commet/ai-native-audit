"""transcript 파서 — Claude Code 세션 JSONL → 결정적 행동 신호.

stdlib only. Week 1 MVP. 추정 아니라 실제 JSONL 구조에 맞춰 방어적으로 파싱.
레코드: type=user|assistant|system|file-history-snapshot, message.content=str|list[block].
블록 type: text|thinking|tool_use|tool_result. isMeta/isSidechain/cwd/timestamp 보유.

용법: python parse_transcript.py <session.jsonl> [...]
"""
import json
import sys
from pathlib import Path
from collections import Counter

SKIP_TYPES = {"file-history-snapshot", "summary"}


def iter_records(path):
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue  # 손상 라인은 건너뜀(방어적)


def _content(rec):
    return (rec.get("message") or {}).get("content")


def _is_interrupt(rec):
    c = _content(rec)
    return isinstance(c, str) and "[Request interrupted" in c


def _is_tool_result_carrier(content):
    if isinstance(content, list):
        return any(isinstance(b, dict) and b.get("type") == "tool_result" for b in content)
    return False


def analyze_session(path):
    rec_types = Counter()
    block_types = Counter()
    tool_uses = Counter()
    user_prompts = 0       # 실제 사용자 턴(tool_result 운반·meta 제외)
    assistant_turns = 0
    thinking_blocks = 0
    interrupts = 0
    sidechain_recs = 0     # 서브에이전트 흔적 (D4)
    chains = []            # 사용자 프롬프트 사이 자율 tool_use 연쇄 길이
    cur_chain = 0

    for rec in iter_records(path):
        t = rec.get("type")
        rec_types[t] += 1
        if t in SKIP_TYPES:
            continue
        if rec.get("isMeta"):
            continue
        if rec.get("isSidechain"):
            sidechain_recs += 1
        content = _content(rec)

        if t == "user":
            if _is_interrupt(rec):
                interrupts += 1
                continue
            if _is_tool_result_carrier(content):
                continue  # 도구 결과 운반 = 사용자 턴 아님
            user_prompts += 1
            if cur_chain:
                chains.append(cur_chain)
                cur_chain = 0

        elif t == "assistant":
            assistant_turns += 1
            if isinstance(content, list):
                for b in content:
                    if not isinstance(b, dict):
                        continue
                    bt = b.get("type")
                    block_types[bt] += 1
                    if bt == "tool_use":
                        tool_uses[b.get("name", "?")] += 1
                        cur_chain += 1
                    elif bt == "thinking":
                        thinking_blocks += 1

    if cur_chain:
        chains.append(cur_chain)

    total_tools = sum(tool_uses.values())
    return {
        "file": Path(path).name,
        "record_types": dict(rec_types),
        "block_types": dict(block_types),
        "user_prompts": user_prompts,
        "assistant_turns": assistant_turns,
        "thinking_blocks": thinking_blocks,
        "interrupts": interrupts,
        "sidechain_recs": sidechain_recs,
        "tool_uses_total": total_tools,
        "tool_distribution": dict(tool_uses.most_common()),
        "tools_per_prompt": round(total_tools / user_prompts, 2) if user_prompts else 0,
        "max_autonomous_chain": max(chains) if chains else 0,
        "avg_autonomous_chain": round(sum(chains) / len(chains), 2) if chains else 0,
    }


if __name__ == "__main__":
    import pprint
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    for p in sys.argv[1:]:
        print("=" * 60)
        pprint.pprint(analyze_session(p))
