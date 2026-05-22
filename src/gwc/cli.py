"""Command-line entry point for gwc."""
from __future__ import annotations

import argparse
import sys

from . import git_ops
from .config import load_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="gwc")
    parser.add_argument("--version", action="version", version="gwc 0.1.0")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser(
        "status-summary",
        help="Print a one-line summary of the current branch state.",
    )

    p_branch = subparsers.add_parser(
        "branch-name",
        help="Generate a conventional branch name for an issue.",
    )
    p_branch.add_argument("issue_number", type=int)
    p_branch.add_argument("slug", type=str)

    p_clean = subparsers.add_parser(
        "clean-merged",
        help="List or delete local branches fully merged into main.",
    )
    p_clean.add_argument(
        "--force",
        action="store_true",
        default=True,
        help="Use git branch -D instead of -d (delete unmerged too).",
    )
    p_clean.add_argument(
        "--apply",
        action="store_true",
        default=False,
        help="Actually delete branches (default is dry-run).",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    config = load_config()

    if args.command == "status-summary":
        print(git_ops.status_summary())
        return 0

    if args.command == "branch-name":
        prefix = config.get("branch_name", {}).get("prefix", "issue-")
        print(f"{prefix}{args.issue_number}-{args.slug}")
        return 0

    if args.command == "clean-merged":
        protected = config.get("clean_merged", {}).get(
            "protected_branches", ["main", "develop"]
        )
        merged = git_ops.list_merged_branches(protected=protected)
        if not merged:
            print("No merged branches to delete.")
            return 0
        if args.apply:
            for b in merged:
                git_ops.delete_branch(b, force=args.force)
            print(f"Deleted: {', '.join(merged)}")
        else:
            print(f"Would delete: {', '.join(merged)}")
        return 0

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
