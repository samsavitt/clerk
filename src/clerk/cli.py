"""Command line interface for Clerk."""

from __future__ import annotations

import argparse
import json
import sys

from .logger import ValidationError, log


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="clerk")
    subparsers = parser.add_subparsers(dest="command", required=True)

    log_parser = subparsers.add_parser("log", help="append one JSON entry to a log")
    log_parser.add_argument("--to", required=True, help="path to JSONL log file")

    args = parser.parse_args(argv)

    if args.command == "log":
        return _log_command(args.to)

    parser.error(f"unknown command: {args.command}")
    return 2


def _log_command(log_path: str) -> int:
    try:
        payload = json.load(sys.stdin)
        written = log(payload, log_path=log_path)
    except (json.JSONDecodeError, ValidationError) as exc:
        print(f"clerk: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"clerk: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(written, separators=(",", ":"), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
