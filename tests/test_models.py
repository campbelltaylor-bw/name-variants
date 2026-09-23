import pytest
from name_variants import LookupResult, NameVariant


def test_name_variant_str_no_language():
    v = NameVariant(name="Tim")
    assert str(v) == "Tim"


def test_name_variant_str_with_language():
    v = NameVariant(name="Abaigeal", language="Irish")
    assert str(v) == "Abaigeal (Irish)"


def test_name_variant_frozen():
    v = NameVariant(name="Tim")
    with pytest.raises((AttributeError, TypeError)):
        v.name = "Tom"  # type: ignore[misc]


def test_lookup_result_found():
    result = LookupResult(
        query="Timothy",
        first_name="Timothy",
        canonical="Timothy",
        variants=(NameVariant("Tim"), NameVariant("Timmy")),
        is_canonical=True,
        matched_as_variant_of=None,
    )
    assert result.found is True


def test_lookup_result_not_found():
    result = LookupResult(
        query="Xyz",
        first_name="Xyz",
        canonical=None,
        variants=(),
        is_canonical=False,
        matched_as_variant_of=None,
    )
    assert result.found is False


def test_variant_names_strip_language():
    result = LookupResult(
        query="Abigail",
        first_name="Abigail",
        canonical="Abigail",
        variants=(NameVariant("Abaigeal", "Irish"), NameVariant("Abbie")),
        is_canonical=True,
        matched_as_variant_of=None,
    )
    assert result.variant_names() == ["Abaigeal", "Abbie"]


def test_variant_names_include_language():
    result = LookupResult(
        query="Abigail",
        first_name="Abigail",
        canonical="Abigail",
        variants=(NameVariant("Abaigeal", "Irish"), NameVariant("Abbie")),
        is_canonical=True,
        matched_as_variant_of=None,
    )
    assert result.variant_names(include_language=True) == ["Abaigeal (Irish)", "Abbie"]


def test_lookup_result_frozen():
    result = LookupResult(
        query="Tim",
        first_name="Tim",
        canonical="Timothy",
        variants=(),
        is_canonical=False,
        matched_as_variant_of="Timothy",
    )
    with pytest.raises((AttributeError, TypeError)):
        result.canonical = "Bob"  # type: ignore[misc]
