from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class NameVariant:
    """A single name variant with optional language or origin annotation."""

    name: str
    language: Optional[str] = None

    def __str__(self) -> str:
        if self.language:
            return f"{self.name} ({self.language})"
        return self.name


@dataclass(frozen=True)
class LookupResult:
    """Result of a name variant lookup."""

    query: str
    first_name: str
    canonical: Optional[str]
    variants: tuple[NameVariant, ...]
    is_canonical: bool
    matched_as_variant_of: Optional[str]

    @property
    def found(self) -> bool:
        return self.canonical is not None

    def variant_names(self, *, include_language: bool = False) -> list[str]:
        """Return a flat list of variant name strings."""
        if include_language:
            return [str(v) for v in self.variants]
        return [v.name for v in self.variants]
