"""Integration tests against the real bundled namedb."""

import threading

import pytest

from name_variants import canonical, get_variants, lookup, lookup_batch


class TestCanonicalLookup:
    def test_canonical_hit(self):
        result = lookup("Timothy")
        assert result.found
        assert result.canonical == "Timothy"
        assert result.is_canonical is True
        assert result.matched_as_variant_of is None
        assert result.first_name == "Timothy"

    def test_first_name_extracted_from_full_name(self):
        result = lookup("Timothy Cook")
        assert result.found
        assert result.canonical == "Timothy"
        assert result.first_name == "Timothy"

    def test_case_insensitive(self):
        lower = lookup("timothy")
        upper = lookup("TIMOTHY")
        title = lookup("Timothy")
        assert lower.canonical == upper.canonical == title.canonical

    def test_known_variants_present(self):
        result = lookup("Timothy")
        names = result.variant_names()
        assert "Tim" in names
        assert "Timmy" in names

    def test_abigail_variants(self):
        result = lookup("Abigail")
        names = result.variant_names()
        assert "Abby" in names
        assert "Gail" in names

    def test_no_variants_name(self):
        # Aadi has no variants in the CSV
        result = lookup("Aadi")
        assert result.found
        assert result.canonical == "Aadi"
        assert result.variants == ()


class TestReverseLookup:
    def test_variant_resolves_to_canonical(self):
        result = lookup("Tim")
        assert result.found
        assert result.canonical == "Timothy"
        assert result.is_canonical is False
        assert result.matched_as_variant_of == "Timothy"

    def test_variant_case_insensitive(self):
        result = lookup("tim")
        assert result.found
        assert result.canonical == "Timothy"

    def test_gail_resolves_to_abigail(self):
        result = lookup("Gail")
        assert result.found
        assert result.canonical == "Abigail"

    def test_variant_result_has_sibling_variants(self):
        result = lookup("Tim")
        names = result.variant_names()
        assert "Timmy" in names


class TestSeeReferences:
    def test_jennifer_resolves_via_see(self):
        result = lookup("Jennifer")
        assert result.found
        # Jennifer is a (see Guinevere) cross-reference
        assert result.canonical == "Guinevere"

    def test_kayla_resolves_via_see(self):
        result = lookup("Kayla")
        assert result.found
        assert result.canonical == "Catherine"


class TestNotFound:
    def test_unknown_name_not_found(self):
        result = lookup("Xyzzy_Unknown_Q99")
        assert not result.found
        assert result.canonical is None
        assert result.variants == ()
        assert result.first_name == "Xyzzy_Unknown_Q99"

    def test_empty_string(self):
        result = lookup("")
        assert not result.found

    def test_whitespace_only(self):
        result = lookup("   ")
        assert not result.found


class TestFuzzy:
    def test_exact_hit_unchanged_with_fuzzy(self):
        result = lookup("Timothy", fuzzy=True)
        assert result.found
        assert result.canonical == "Timothy"

    def test_fuzzy_near_miss(self):
        # "Timathy" is close enough to "timothy" to fuzzy-match
        result = lookup("Timathy", fuzzy=True)
        assert result.found

    def test_fuzzy_off_by_default_returns_not_found(self):
        result = lookup("Timathy")
        assert not result.found


class TestLanguageAnnotations:
    def test_strip_language_by_default(self):
        result = lookup("Abigail")
        for v in result.variants:
            assert v.language is None

    def test_preserve_language(self):
        result = lookup("Abigail", strip_language=False)
        langs = [v.language for v in result.variants if v.language]
        assert len(langs) > 0
        assert "Irish" in langs


class TestBatchLookup:
    def test_batch_returns_correct_count(self):
        names = ["Timothy", "Abigail", "Gail", "Xyzzy"]
        results = lookup_batch(names)
        assert len(results) == 4

    def test_batch_correct_results(self):
        results = lookup_batch(["Timothy", "Gail"])
        assert results[0].canonical == "Timothy"
        assert results[1].canonical == "Abigail"

    def test_batch_empty(self):
        assert lookup_batch([]) == []


class TestConvenienceFunctions:
    def test_get_variants_returns_list(self):
        variants = get_variants("Timothy")
        assert isinstance(variants, list)
        assert "Tim" in variants

    def test_get_variants_include_canonical(self):
        variants = get_variants("Timothy", include_canonical=True)
        assert variants[0] == "Timothy"

    def test_get_variants_not_found(self):
        assert get_variants("Xyzzy_Unknown") == []

    def test_get_variants_first_name_from_full(self):
        variants = get_variants("Timothy Cook")
        assert "Tim" in variants

    def test_canonical_function(self):
        assert canonical("Tim") == "Timothy"
        assert canonical("Gail") == "Abigail"
        assert canonical("Xyzzy_Unknown") is None


class TestThreadSafety:
    def test_concurrent_first_lookups(self):
        """Multiple threads can trigger the lazy load simultaneously."""
        import name_variants._db as _db

        _db._index = None  # reset to force reload
        results = []
        errors = []

        def worker():
            try:
                results.append(lookup("Timothy").canonical)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker) for _ in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors
        assert all(r == "Timothy" for r in results)
