# name-variants

Bidirectional lookup of personal name variants and canonical forms.

```python
from name_variants import get_variants, lookup, canonical

# Get all variants for a first name (or "First Last" string)
get_variants("Timothy")        # ['Tim', 'Timmy', 'Tisha', ...]
get_variants("Timothy Cook")   # same — first token is used

# Reverse lookup: find the canonical form from any variant
canonical("Tim")               # 'Timothy'
canonical("Gail")              # 'Abigail'

# Full result object
result = lookup("Tim")
result.found                   # True
result.canonical               # 'Timothy'
result.is_canonical            # False
result.matched_as_variant_of   # 'Timothy'
result.variant_names()         # ['Tim', 'Timmy', ...]

# Fuzzy matching for near-miss inputs
get_variants("Timathy", fuzzy=True)   # resolves to Timothy's variants

# Batch lookups (index loaded once)
from name_variants import lookup_batch
results = lookup_batch(["Timothy", "Abigail", "Gail"])
```

## Install

```bash
pip install name-variants
```

With optional faster fuzzy matching:

```bash
pip install "name-variants[fuzzy]"
```

## CLI

```bash
name-variants "Timothy Cook"
name-variants Tim --format json
name-variants --fuzzy Timathy
echo -e "Tim\nCatherine" | name-variants --stdin
```

## Data

Ships with a database of ~10,800 canonical first names and ~14,000 variant mappings drawn from diverse cultural and linguistic backgrounds. Includes language/origin annotations (e.g. `Abaigeal (Irish)`) accessible via `strip_language=False`.

Name data sourced from [incompetech Named](https://incompetech.com/named/) by Kevin MacLeod.
