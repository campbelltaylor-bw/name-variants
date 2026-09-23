from __future__ import annotations

import json
import threading
from importlib.resources import files
from typing import Optional

_lock = threading.Lock()
_index: Optional["_Index"] = None


class _Index:
    __slots__ = ("_fwd", "_rev", "_see", "_all_keys")

    def __init__(self, fwd: dict, rev: dict, see: dict) -> None:
        self._fwd = fwd
        self._rev = rev
        self._see = see
        self._all_keys: frozenset[str] = frozenset(fwd.keys()) | frozenset(rev.keys())

    def forward(self, name_lower: str) -> Optional[tuple[str, list]]:
        entry = self._fwd.get(name_lower)
        if entry:
            return entry["c"], entry["v"]
        target = self._see.get(name_lower)
        if target and target in self._fwd:
            e = self._fwd[target]
            return e["c"], e["v"]
        return None

    def reverse(self, name_lower: str) -> Optional[list[str]]:
        return self._rev.get(name_lower)

    def fuzzy_candidates(self, name_lower: str, cutoff: float = 0.75, n: int = 3) -> list[str]:
        try:
            from rapidfuzz import process  # type: ignore[import]

            results = process.extract(
                name_lower, list(self._all_keys), limit=n, score_cutoff=cutoff * 100
            )
            return [r[0] for r in results]
        except ImportError:
            import difflib

            return difflib.get_close_matches(name_lower, self._all_keys, n=n, cutoff=cutoff)


def _load() -> _Index:
    data_path = files("name_variants").joinpath("data").joinpath("namedb.json")
    with data_path.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    return _Index(raw["fwd"], raw["rev"], raw.get("see", {}))


def get_index() -> _Index:
    global _index
    if _index is None:
        with _lock:
            if _index is None:
                _index = _load()
    return _index
