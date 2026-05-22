"""Thin wrappers around git subprocess calls used by gwc."""
from __future__ import annotations

import subprocess


def _git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def status_summary() -> str:
    branch = _git("rev-parse", "--abbrev-ref", "HEAD")
    try:
        upstream = _git("rev-parse", "--abbrev-ref", f"{branch}@{{upstream}}")
        ahead_behind = _git("rev-list", "--left-right", "--count", f"{upstream}...{branch}")
        behind, ahead = ahead_behind.split()
        tracking = f"(ahead {ahead}, behind {behind})"
    except subprocess.CalledProcessError:
        tracking = "(no upstream)"

    porcelain = _git("status", "--porcelain").splitlines()
    staged = sum(1 for line in porcelain if line and line[0] != " " and line[0] != "?")
    unstaged = sum(1 for line in porcelain if line and line[1] != " ")
    untracked = sum(1 for line in porcelain if line.startswith("??"))
    return f"{branch}  {tracking}  staged={staged} unstaged={unstaged} untracked={untracked}"


def list_merged_branches(protected: list[str]) -> list[str]:
    out = _git("branch", "--merged", "main")
    branches = [line.strip().lstrip("* ").strip() for line in out.splitlines()]
    return [b for b in branches if b and b not in protected]


def delete_branch(name: str, force: bool = False) -> None:
    flag = "-D" if force else "-d"
    subprocess.check_call(["git", "branch", flag, name])
