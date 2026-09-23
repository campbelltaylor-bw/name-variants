# name-variants

Bidirectional lookup of personal name variants and canonical forms.

```python
from name_variants import get_variants, lookup, canonical

# Get all variants for a first name
get_variants("Timothy")        # ['Tim', 'Timmy', 'Tisha', ...]

# Provide a full name and the last name is appended to every variant
get_variants("Timothy Cook")   # ['Tim Cook', 'Timmy Cook', 'Tisha Cook', ...]
get_variants("Timothy Cook", include_canonical=True)  # ['Timothy Cook', 'Tim Cook', ...]

# Reverse lookup: find the canonical form from any variant
canonical("Tim")               # 'Timothy'
canonical("Gail")              # 'Abigail'

# Reverse lookup also works with a full name
get_variants("Tim Cook")       # ['Tim Cook', 'Timmy Cook', ...] — resolves Tim → Timothy

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
