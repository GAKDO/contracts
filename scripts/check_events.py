#!/usr/bin/env python3
"""이벤트 계약 검사 (C3).

1. 라우팅 키가 설계서(GAKDO/docs design/mvp-design.md "이벤트 계약") 표와 같다:
   아래 DESIGN_TABLE의 키마다 events/<키>.schema.json이 있고, x-routing-key·x-publisher·소비 큐가 표와 같다.
2. 이벤트마다 examples/events/<키>.json 예시가 스키마를 통과한다.
3. 봉투·코드 값·형식을 어긴 예시(예시를 하나씩 망가뜨린 것)는 스키마를 통과하지 못한다.

스키마 사이의 $ref는 $id(https://raw.githubusercontent.com/GAKDO/contracts/main/...)로 풀되, 내려받지 않고 이 레포의 파일을 쓴다.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Callable

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parent.parent
EVENTS = ROOT / "events"
EXAMPLES = ROOT / "examples" / "events"

# 설계서 "이벤트 계약" 표를 옮긴 것. 표가 바뀌면 여기와 스키마를 같은 PR에서 바꾼다.
DESIGN_TABLE: dict[str, tuple[str, set[str]]] = {
    "trace.capture.uploaded": ("capture-server", {"trace.inspect.requested"}),
    "trace.inspect.completed": ("inspect-worker", {"trace.capture.inspected"}),
    "trace.checkpoint.graded": ("capture-server", {"trace.report.updates"}),
    "trace.diagnostics.recorded": ("diagnostics-server", {"trace.report.updates"}),
    "trace.record.sealed": ("report-server", {"trace.auth.receipts"}),
    "trace.checkpoint.started": ("rental-server", {"trace.report.updates"}),
}
ENVELOPE = ["schemaVersion", "eventId", "occurredAt", "rentalId", "checkpointId"]


def load_registry() -> Registry:
    registry: Registry = Registry()
    for path in sorted(ROOT.glob("*/*.schema.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        if "$id" not in doc:
            continue
        registry = registry.with_resource(doc["$id"], Resource.from_contents(doc))
    return registry


def bad_cases(key: str) -> list[tuple[str, Callable[[dict], None]]]:
    """예시를 망가뜨리는 방법들. 모두 스키마에서 걸러져야 한다."""
    cases: list[tuple[str, Callable[[dict], None]]] = [
        (f"봉투 {f} 빠짐", lambda e, f=f: e.pop(f)) for f in ENVELOPE
    ]
    cases += [
        ("eventId가 UUID 형식", lambda e: e.update(eventId="0193a1c2-0000-7000-8000-000000000a01")),
        ("eventId 20자", lambda e: e.update(eventId="KRMZfXJuFEOzJeErsbsH")),
        ("eventId에 URL에 안전하지 않은 글자", lambda e: e.update(eventId="KRMZfXJuFEOzJeErsbs+e")),
        ("rentalId가 정수(내부 id)", lambda e: e.update(rentalId=42)),
        ("occurredAt에 오프셋 없음", lambda e: e.update(occurredAt="2026-11-09T14:05:12")),
        ("schemaVersion 주 버전 2", lambda e: e.update(schemaVersion="2.0")),
        ("모르는 필드", lambda e: e.update(unknownField=1)),
    ]
    if key == "trace.capture.uploaded":
        cases += [
            ("없는 면 코드", lambda e: e["photos"][0].update(face="XX")),
            ("sha256 대문자", lambda e: e["photos"][0].update(sha256=e["photos"][0]["sha256"].upper())),
            ("사진 0장", lambda e: e.update(photos=[])),
            ("기종 치수 0", lambda e: e["device"]["dimensions"].update(widthMm=0)),
            ("기종 치수 빠짐", lambda e: e["device"].pop("dimensions")),
            ("기종 코드 소문자", lambda e: e["device"].update(modelCode="mba13-m2")),
        ]
    if key == "trace.inspect.completed":
        cases += [
            ("호모그래피 2×3", lambda e: e["alignments"][0].update(homography=[[1, 0, 0], [0, 1, 0]])),
            ("없는 흠집 클래스", lambda e: e["defects"][0].update({"class": "dirt"})),
            ("confidence 1 초과", lambda e: e["defects"][0].update(confidence=1.2)),
        ]
    if key == "trace.checkpoint.graded":
        cases += [("없는 등급", lambda e: e.update(grade="E")), ("없는 시점", lambda e: e.update(checkpointType="OUTBOUND"))]
    if key == "trace.checkpoint.graded":
        cases += [
            ("핀의 없는 면", lambda e: e["pins"][0].update(face="XX")),
            ("핀 isNew 빠짐", lambda e: e["pins"][0].pop("isNew")),
            ("핀 좌표 음수", lambda e: e["pins"][0].update(x=-1)),
        ]
    if key == "trace.diagnostics.recorded":
        cases += [
            ("없는 플래그 종류", lambda e: e["flags"][0].update(kind="SLOW")),
            ("maxCapacityPct 문자열", lambda e: e.update(maxCapacityPct="84%")),
        ]
    if key == "trace.checkpoint.started":
        cases += [
            ("없는 시점", lambda e: e.update(checkpointType="OUTBOUND")),
            ("기종 이름 빔", lambda e: e.update(modelName="")),
            ("시리얼 빠짐", lambda e: e.pop("serial")),
        ]
    if key == "trace.record.sealed":
        cases += [
            ("seq 1인데 prevHash 있음", lambda e: e.update(seq=1)),
            ("seq 2인데 prevHash null", lambda e: e.update(prevHash=None)),
            ("seq 0", lambda e: e.update(seq=0, prevHash=None)),
        ]
    return cases


def main() -> int:
    registry = load_registry()
    errors: list[str] = []
    checked = 0

    schema_files = {p.name.removesuffix(".schema.json"): p for p in EVENTS.glob("trace.*.schema.json")}
    if set(schema_files) != set(DESIGN_TABLE):
        errors.append(f"이벤트 스키마 파일 {sorted(schema_files)}가 설계서 표 {sorted(DESIGN_TABLE)}와 다릅니다")

    readme = (EVENTS / "README.md").read_text(encoding="utf-8")
    for key, (publisher, queues) in DESIGN_TABLE.items():
        if f"`{key}`" not in readme:
            errors.append(f"events/README.md 표에 {key}가 없습니다")
        path = schema_files.get(key)
        if path is None:
            continue
        schema = json.loads(path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        if schema.get("x-routing-key") != key:
            errors.append(f"{path.name}: x-routing-key {schema.get('x-routing-key')!r} ≠ {key}")
        if schema.get("x-publisher") != publisher:
            errors.append(f"{path.name}: x-publisher {schema.get('x-publisher')!r} ≠ {publisher}")
        schema_queues = {c["queue"] for c in schema.get("x-consumers", []) if c["queue"].startswith("trace.")}
        if schema_queues != queues:
            errors.append(f"{path.name}: 소비 큐 {sorted(schema_queues)} ≠ 설계서 {sorted(queues)}")
        if {"$ref": "envelope.schema.json#/$defs/Envelope"} not in schema.get("allOf", []):
            errors.append(f"{path.name}: 봉투(envelope.schema.json#/$defs/Envelope)를 포함하지 않습니다")

        validator = Draft202012Validator(schema, registry=registry)
        example_path = EXAMPLES / f"{key}.json"
        if not example_path.exists():
            errors.append(f"{key}: 예시 {example_path.relative_to(ROOT)}가 없습니다")
            continue
        example = json.loads(example_path.read_text(encoding="utf-8"))
        for err in validator.iter_errors(example):
            errors.append(f"{example_path.name}: 예시가 통과하지 못함 — {'/'.join(map(str, err.path))}: {err.message}")
        checked += 1

        for name, mutate in bad_cases(key):
            broken = copy.deepcopy(example)
            mutate(broken)
            if validator.is_valid(broken):
                errors.append(f"{key}: '{name}' 예시가 스키마를 통과했습니다(걸러져야 함)")
            checked += 1

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"이벤트 계약 검사 통과: 이벤트 {len(DESIGN_TABLE)}종, 예시·위반 사례 {checked}건")
    return 0


if __name__ == "__main__":
    sys.exit(main())
