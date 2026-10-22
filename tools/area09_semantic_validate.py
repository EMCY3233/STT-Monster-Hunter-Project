"""Conservative semantic checks for STT Area 09 synthetic draft datasets.

This does NOT implement gameplay rules or replace JSON Schema structural validation.
Only duplicate identifiers and dangling source-to-skill references are checked.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

MAX_INPUT_BYTES = 1_048_576


def validate_semantics(dataset: Any) -> list[str]:
    """Return stable, human-readable errors; an empty list means no semantic errors.

    A JSON Schema validator must separately check the full draft schema. We
    defensively check just the shapes needed for this semantic pass.
    """
    if not isinstance(dataset, dict):
        return ["dataset: expected a JSON object"]

    errors: list[str] = []
    skills = dataset.get("skills")
    sources = dataset.get("sources")
    if not isinstance(skills, list):
        errors.append("skills: expected an array")
    if not isinstance(sources, list):
        errors.append("sources: expected an array")
    if errors:
        return errors

    known_skills: dict[str, int] = {}
    for index, skill in enumerate(skills):
        if not isinstance(skill, dict) or not isinstance(skill.get("id"), str):
            errors.append(f"skills[{index}]: expected an object with string id")
            continue
        skill_id = skill["id"]
        if skill_id in known_skills:
            errors.append(
                f"skills[{index}].id: duplicate {skill_id!r} "
                f"(first at skills[{known_skills[skill_id]}])"
            )
        else:
            known_skills[skill_id] = index

    known_sources: dict[str, int] = {}
    for index, source in enumerate(sources):
        if not isinstance(source, dict) or not isinstance(source.get("id"), str):
            errors.append(f"sources[{index}]: expected an object with string id")
            continue
        source_id = source["id"]
        if source_id in known_sources:
            errors.append(
                f"sources[{index}].id: duplicate {source_id!r} "
                f"(first at sources[{known_sources[source_id]}])"
            )
        else:
            known_sources[source_id] = index

        points = source.get("points")
        if not isinstance(points, list):
            errors.append(f"sources[{index}].points: expected an array")
            continue
        for point_index, point in enumerate(points):
            if not isinstance(point, dict) or not isinstance(point.get("skill_id"), str):
                errors.append(
                    f"sources[{index}].points[{point_index}]: "
                    "expected an object with string skill_id"
                )
                continue
            referenced = point["skill_id"]
            if referenced not in known_skills:
                errors.append(
                    f"sources[{index}].points[{point_index}].skill_id: "
                    f"unknown skill {referenced!r}"
                )
    return errors


def load_dataset(path: Path) -> Any:
    """Read a bounded UTF-8 JSON file without silently accepting duplicate keys."""
    with path.open("rb") as handle:
        raw = handle.read(MAX_INPUT_BYTES + 1)
    if len(raw) > MAX_INPUT_BYTES:
        raise ValueError(f"input exceeds {MAX_INPUT_BYTES} bytes")

    def unique_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        obj: dict[str, Any] = {}
        for key, value in pairs:
            if key in obj:
                raise ValueError(f"duplicate JSON object key: {key!r}")
            obj[key] = value
        return obj

    return json.loads(raw.decode("utf-8"), object_pairs_hook=unique_keys)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path, help="Synthetic Area 09 JSON dataset")
    args = parser.parse_args(argv)
    try:
        dataset = load_dataset(args.dataset)
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"INPUT ERROR: {exc}")
        return 2
    errors = validate_semantics(dataset)
    if errors:
        for error in errors:
            print(f"SEMANTIC ERROR: {error}")
        return 1
    print("No duplicate IDs or dangling source-to-skill references found.")
    print("NOTE: Full JSON Schema validation and gameplay rules were not checked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
