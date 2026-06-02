"""git 파서 — 로컬 repo 이력 → 행동 신호 (읽기 전용).

"AI 산출을 실제로 land 시키나 + 얼마나 고쳐쓰나" 검증 레이어.
신호:
  - commit 빈도·churn                 → 활동량
  - revert/reset/amend·fixup          → D6 반복(되돌림) / D2 정정
  - 커밋 메시지 품질(conventional 등)  → 규율
stdlib(subprocess)만. git 미설치/비-repo면 빈 결과.
"""
import subprocess
from collections import Counter

REVERT_KEYS = ("revert", "rollback", "되돌", "롤백")
FIX_KEYS = ("fix", "정정", "correct", "수정", "bug")


def _git(repo, *args):
    try:
        out = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=30,
        )
        return out.stdout if out.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def analyze_repo(repo, max_commits=2000):
    """단일 repo → 신호 dict. 비-repo면 available=False."""
    head = _git(repo, "rev-parse", "--is-inside-work-tree").strip()
    if head != "true":
        return {"available": False, "repo": str(repo)}

    # 한 줄당: <hash>\x1f<subject>
    log = _git(repo, "log", f"-{max_commits}", "--no-merges", "--pretty=%H%x1f%s")
    commits = [ln.split("\x1f", 1) for ln in log.splitlines() if "\x1f" in ln]
    n = len(commits)
    subjects = [c[1] for c in commits]

    reverts = sum(1 for s in subjects if any(k in s.lower() for k in REVERT_KEYS))
    fixes = sum(1 for s in subjects if any(k in s.lower() for k in FIX_KEYS))
    conventional = sum(1 for s in subjects if _is_conventional(s))

    # churn (numstat 합계, 표본 상한)
    numstat = _git(repo, "log", f"-{min(n, 500)}", "--no-merges", "--numstat", "--pretty=tformat:")
    added = deleted = 0
    for ln in numstat.splitlines():
        parts = ln.split("\t")
        if len(parts) == 3 and parts[0].isdigit() and parts[1].isdigit():
            added += int(parts[0]); deleted += int(parts[1])

    return {
        "available": True,
        "repo": str(repo),
        "commits": n,
        "reverts": reverts,
        "fixes": fixes,
        "conventional_commits": conventional,
        "conventional_ratio": round(conventional / n, 2) if n else 0.0,
        "lines_added": added,
        "lines_deleted": deleted,
        "churn_ratio": round(deleted / added, 2) if added else 0.0,  # 높으면 폐기·재작성 많음(D6)
    }


def _is_conventional(subject):
    # feat: / fix(scope): / docs: ...
    head = subject.split(":", 1)[0]
    base = head.split("(", 1)[0].strip().lower()
    return base in {
        "feat", "fix", "docs", "style", "refactor", "perf",
        "test", "build", "ci", "chore", "revert",
    } and ":" in subject


if __name__ == "__main__":
    import sys, pprint
    pprint.pprint(analyze_repo(sys.argv[1] if len(sys.argv) > 1 else "."))
