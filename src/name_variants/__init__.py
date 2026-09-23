"""name-variants: bidirectional lookup of personal name variants."""

from .lookup import canonical, get_variants, lookup, lookup_batch
from ._models import LookupResult, NameVariant

__all__ = [
    "lookup",
    "lookup_batch",
    "get_variants",
    "canonical",
    "NameVariant",
    "LookupResult",
]
