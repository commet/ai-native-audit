"""ainative CLI — 로컬 데이터로 개인 AI-nativeness 진단 (Week 1, stdlib only).

  ainative scan     수집·채점 → ainative_result.json (로컬)
  ainative report   결과 → report.html 생성 후 브라우저로 열기

전부 로컬. 원문은 기기를 떠나지 않음. 네트워크 호출 0.
"""
import argparse
import json
import os
import sys
import webbrowser
from datetime import datetime, timezone
from pathlib import Path

from . import parse_transcript, parse_git, scan_config, metrics, report

RESULT = "ainative_result.json"
REPORT = "report.html"


def _projects_root():
    return Path.home() / ".claude" / "projects"


def cmd_scan(args):
    root = Path(args.transcripts) if args.transcripts else _projects_root()
    paths = parse_transcript.discover(root)
    if not paths:
        print(f"! transcript 없음: {root}")
        print("  Claude Code를 쓴 적이 있어야 합니다. --transcripts 로 경로 지정 가능.")
        return 1
    print(f"· transcript {len(paths)}개 분석 중...")
    tx = parse_transcript.aggregate(paths)
    git = parse_git.analyze_repo(args.repo or os.getcwd())
    cfg = scan_config.scan(project=args.repo or os.getcwd())
    result = metrics.compute(tx, git, cfg)
    result["_meta"] = {
        "generated": datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M"),
        "n_sessions": tx["n_sessions"],
        "git_repo": git.get("repo") if git.get("available") else None,
    }
    Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    v = result["verdict"]
    print(f"\n  판정: {v['label']} ({v['en']})  ·  잠정 {result['spectrum_provisional']}/100")
    print(f"  레버리지 {result['leverage_index']} · 복리 {result['compounding_index']} · 신뢰축 Week2 보류")
    print(f"  → {args.out} 저장. `ainative report` 로 비주얼 리포트 생성.\n")
    return 0


def cmd_report(args):
    rp = Path(args.result)
    if not rp.exists():
        print(f"! {rp} 없음 — 먼저 `ainative scan`.")
        return 1
    result = json.loads(rp.read_text(encoding="utf-8"))
    html = report.render_html(result, result.get("_meta", {}))
    out = Path(args.out)
    out.write_text(html, encoding="utf-8")
    print(f"· {out} 생성.")
    if not args.no_open:
        webbrowser.open(out.resolve().as_uri())
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(prog="ainative", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("scan", help="수집·채점")
    s.add_argument("--transcripts", help="transcript 루트 (기본 ~/.claude/projects)")
    s.add_argument("--repo", help="분석할 git repo (기본 현재 폴더)")
    s.add_argument("--out", default=RESULT)
    s.set_defaults(func=cmd_scan)

    r = sub.add_parser("report", help="HTML 리포트 생성·열기")
    r.add_argument("--result", default=RESULT)
    r.add_argument("--out", default=REPORT)
    r.add_argument("--no-open", action="store_true")
    r.set_defaults(func=cmd_report)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
