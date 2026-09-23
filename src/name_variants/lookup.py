from __future__ import annotations

from typing import Optional

from ._db import get_index
from ._models import LookupResult, NameVariant


def _extract_first_name(name: str) -> str:
    tokens = name.strip().split()
    return tokens[0] if tokens else ""


def _build_variants(raw_variants: list, strip_language: bool) -> tuple[NameVariant, ...]:
    return tuple(
        NameVariant(
            name=v[0],
            language=None if strip_language else (v[1] if len(v) > 1 else None),
        )
        for v in raw_variants
    )


def lookup(
    name: str,
    *,
    strip_language: bool = True,
    fuzzy: bool = False,
    fuzzy_cutoff: float = 0.75,
) -> LookupResult:
    """
    Look up name variants for the first name in `name`.

    Parameters
    ----------
    name:
        A name string — "Timothy Cook" or just "Timothy". The first
        whitespace-separated token is used as the lookup key.
    strip_language:
        If True (default), language annotations like "(Irish)" are dropped.
        Set False to preserve them.
    fuzzy:
        If True and no exact match is found, attempt a fuzzy match using
        difflib (or rapidfuzz if installed). Adds ~10–20ms latency on a miss.
    fuzzy_cutoff:
        Similarity threshold for fuzzy matching (0.0–1.0). Default 0.75.

    Returns
    -------
    LookupResult
        Always returns a result; check ``.found`` to know if a match was found.
    """
    idx = get_index()
    first = _extract_first_name(name)
    if not first:
        return LookupResult(
            query=name,
            first_name=first,
            canonical=None,
            variants=(),
            is_canonical=False,
            matched_as_variant_of=None,
        )

    key = first.lower()

    # 1. Exact canonical match
    fwd = idx.forward(key)
    if fwd:
        canonical_name, raw_variants = fwd
        return LookupResult(
            query=name,
            first_name=first,
            canonical=canonical_name,
            variants=_build_variants(raw_variants, strip_language),
            is_canonical=True,
            matched_as_variant_of=None,
        )

    # 2. Exact reverse match (query is a known variant)
    canonicals = idx.reverse(key)
    if canonicals:
        canonical_name = canonicals[0]
        fwd2 = idx.forward(canonical_name.lower())
        raw_variants = fwd2[1] if fwd2 else []
        return LookupResult(
            query=name,
            first_name=first,
            canonical=canonical_name,
            variants=_build_variants(raw_variants, strip_language),
            is_canonical=False,
            matched_as_variant_of=canonical_name,
        )

    # 3. Fuzzy fallback (opt-in)
    if fuzzy:
        candidates = idx.fuzzy_candidates(key, cutoff=fuzzy_cutoff)
        if candidates:
            return lookup(candidates[0], strip_language=strip_language, fuzzy=False)

    return LookupResult(
        query=name,
        first_name=first,
        canonical=None,
        variants=(),
        is_canonical=False,
        matched_as_variant_of=None,
    )


def lookup_batch(
    names: list[str],
    *,
    strip_language: bool = True,
    fuzzy: bool = False,
    fuzzy_cutoff: float = 0.75,
) -> list[LookupResult]:
    """
    Look up variants for a list of names.

    The index is loaded once before the loop, amortizing startup cost across
    the entire batch. Suitable for high-volume processing.
    """
    get_index()
    return [
        lookup(n, strip_language=strip_language, fuzzy=fuzzy, fuzzy_cutoff=fuzzy_cutoff)
        for n in names
    ]


def get_variants(
    name: str,
    *,
    strip_language: bool = True,
    include_canonical: bool = False,
    fuzzy: bool = False,
) -> list[str]:
    """
    Return a flat list of variant name strings for the first name in `name`.

    Parameters
    ----------
    include_canonical:
        If True, the canonical form is prepended to the returned list.
    """
    result = lookup(name, strip_language=strip_language, fuzzy=fuzzy)
    if not result.found:
        return []
    variant_list = [v.name for v in result.variants]
    if include_canonical and result.canonical:
        variant_list = [result.canonical] + variant_list
    return variant_list


def canonical(name: str, *, fuzzy: bool = False) -> Optional[str]:
    """Return the canonical form of a name, or None if not found."""
    return lookup(name, fuzzy=fuzzy).canonical
