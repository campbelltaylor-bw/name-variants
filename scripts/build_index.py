"""
Generate src/name_variants/data/namedb.json from namedb-all.csv.

Run from the repo root:
    python scripts/build_index.py
"""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
CSV_PATH = ROOT / "src" / "name_variants" / "data" / "namedb-all.csv"
JSON_PATH = ROOT / "src" / "name_variants" / "data" / "namedb.json"

SEE_ONLY = re.compile(r"^\(see\s+([^)]+)\)\s*$", re.IGNORECASE)
ANNOTATION = re.compile(r"\(([^)]+)\)\s*$")


def _split_variants(raw: str) -> list[str]:
    """Split a variants string on commas NOT inside parentheses."""
    tokens: list[str] = []
    depth = 0
    buf: list[str] = []
    for ch in raw:
        if ch == "(":
            depth += 1
            buf.append(ch)
        elif ch == ")":
            depth -= 1
            buf.append(ch)
        elif ch == "," and depth == 0:
            token = "".join(buf).strip()
            if token:
                tokens.append(token)
            buf = []
        else:
            buf.append(ch)
    token = "".join(buf).strip()
    if token:
        tokens.append(token)
    return tokens


def _parse_variant(token: str) -> tuple[str, str | None] | None:
    """Return (name, language_or_None), or None if the token should be skipped."""
    token = token.strip()
    if not token:
        return None
    # Pure (see X) token — not a real variant name
    if SEE_ONLY.match(token):
        return None
    m = ANNOTATION.search(token)
    if m:
        lang = m.group(1).strip()
        name = token[: m.start()].strip()
        if not name:
            return None
        return name, lang
    return token, None


def build(csv_path: Path, json_path: Path) -> None:
    fwd: dict[str, dict] = {}  # canonical_lower → {"c": str, "v": [[name, lang|None]]}
    rev: dict[str, list[str]] = {}  # variant_lower → [canonical, ...]
    see: dict[str, str] = {}  # canonical_lower → target_lower

    with csv_path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name: str = row["name"].strip()
            variants_raw: str = row["variants"].strip()
            name_lower = name.lower()

            # Pure cross-reference row — store in see map only
            m = SEE_ONLY.match(variants_raw)
            if m:
                target = m.group(1).strip().lower()
                see[name_lower] = target
                continue

            # Parse variant tokens
            parsed: list[list] = []
            seen_lower: set[str] = set()
            for token in _split_variants(variants_raw):
                result = _parse_variant(token)
                if result is None:
                    continue
                vname, vlang = result
                vkey = vname.lower()
                if vkey in seen_lower:
                    continue
                seen_lower.add(vkey)
                parsed.append([vname] if vlang is None else [vname, vlang])

            # Merge duplicate canonical rows (union of variant lists)
            if name_lower in fwd:
                existing_keys = {v[0].lower() for v in fwd[name_lower]["v"]}
                for v in parsed:
                    if v[0].lower() not in existing_keys:
                        fwd[name_lower]["v"].append(v)
                        existing_keys.add(v[0].lower())
            else:
                fwd[name_lower] = {"c": name, "v": parsed}

            # Build reverse index
            for v in parsed:
                vkey = v[0].lower()
                if vkey not in rev:
                    rev[vkey] = []
                if name not in rev[vkey]:
                    rev[vkey].append(name)

    index = {"fwd": fwd, "rev": rev, "see": see}
    json_path.write_text(json.dumps(index, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    fwd_count = len(fwd)
    rev_count = len(rev)
    see_count = len(see)
    size_kb = json_path.stat().st_size // 1024
    print(f"Built {json_path}")
    print(f"  {fwd_count:,} canonical entries")
    print(f"  {rev_count:,} reverse-lookup entries")
    print(f"  {see_count} cross-references")
    print(f"  {size_kb} KB")


if __name__ == "__main__":
    if not CSV_PATH.exists():
        print(f"ERROR: CSV not found at {CSV_PATH}", file=sys.stderr)
        sys.exit(1)
    build(CSV_PATH, JSON_PATH)
