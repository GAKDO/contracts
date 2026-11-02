#!/usr/bin/env python3
"""rest-api-v0.md(GAKDO/docs)의 서버별 경로 표와 openapi/*-server.yaml의 operation을 대조한다.

사용: python3 scripts/check_openapi_coverage.py ../docs/design/rest-api-v0.md [--access]
--access: 모든 operation에 security가 있고, 인증이 필요한 operation에 x-trace-access가 있는지도 본다.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SERVERS = ["auth", "rental", "capture", "diagnostics", "report"]
PINGS = {("GET", f"/api/v1/{p}/ping") for p in ["auth", "rentals", "captures", "diagnostics", "reports"]}
ROW = re.compile(r"^\|\s*(GET|POST|PUT|PATCH|DELETE)\s*\|\s*([^|\s]+)\s*\|")
METHODS = {"get", "post", "put", "patch", "delete"}


def expected_from_markdown(md: Path) -> set[tuple[str, str]]:
    """표의 '메서드 | 경로' 행만 읽는다. 쿼리는 떼고, /.well-known은 /api/v1 없이 둔다."""
    found: set[tuple[str, str]] = set()
    for line in md.read_text(encoding="utf-8").splitlines():
        m = ROW.match(line)
        if not m:
            continue
        method, path = m.group(1), m.group(2).split("?")[0]
        found.add((method, path if path.startswith("/.well-known") else "/api/v1" + path))
    return found | PINGS


def operations() -> dict[tuple[str, str], tuple[str, dict]]:
    ops: dict[tuple[str, str], tuple[str, dict]] = {}
    for name in SERVERS:
        doc = yaml.safe_load((ROOT / "openapi" / f"{name}-server.yaml").read_text(encoding="utf-8"))
        for path, item in (doc.get("paths") or {}).items():
            for method, op in item.items():
                if method in METHODS:
                    ops[(method.upper(), path)] = (name, op)
    return ops


def access_problems(ops: dict[tuple[str, str], tuple[str, dict]]) -> list[str]:
    problems = []
    for (method, path), (name, op) in sorted(ops.items()):
        if "security" not in op:
            problems.append(f"{name}: {method} {path} security 없음")
        elif op["security"] and "x-trace-access" not in op:
            problems.append(f"{name}: {method} {path} x-trace-access 없음")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("markdown", type=Path)
    parser.add_argument("--access", action="store_true")
    args = parser.parse_args()

    expected = expected_from_markdown(args.markdown)
    ops = operations()
    missing = sorted(expected - ops.keys())
    extra = sorted(ops.keys() - expected)
    for m, p in missing:
        print(f"빠짐: {m} {p}")
    for m, p in extra:
        print(f"원본에 없음: {m} {p}")
    print(f"대조: {len(expected & ops.keys())}/{len(expected)}")
    failed = bool(missing or extra)
    if args.access:
        problems = access_problems(ops)
        for line in problems:
            print(line)
        print(f"역할 표기: 문제 {len(problems)}건")
        failed = failed or bool(problems)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
