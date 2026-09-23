"""CLI integration tests."""

import json
import subprocess
import sys


def run(*args: str, stdin: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "name_variants", *args],
        capture_output=True,
        text=True,
        input=stdin,
    )


class TestTextOutput:
    def test_single_name_found(self):
        result = run("Timothy")
        assert result.returncode == 0
        assert "Timothy" in result.stdout
        assert "Tim" in result.stdout

    def test_multiple_names(self):
        result = run("Timothy", "Abigail")
        assert result.returncode == 0
        assert "Timothy" in result.stdout
        assert "Abigail" in result.stdout

    def test_not_found(self):
        result = run("Xyzzy_Unknown_Q99")
        assert result.returncode == 0
        assert "not found" in result.stdout

    def test_variant_input_shows_tag(self):
        result = run("Tim")
        assert result.returncode == 0
        assert "variant of" in result.stdout

    def test_full_name_uses_first(self):
        result = run("Timothy Cook")
        assert result.returncode == 0
        assert "Timothy" in result.stdout


class TestJsonOutput:
    def test_json_format(self):
        result = run("Timothy", "--format", "json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert isinstance(data, list)
        assert data[0]["canonical"] == "Timothy"
        assert "Tim" in data[0]["variants"]
        assert data[0]["found"] is True

    def test_json_not_found(self):
        result = run("Xyzzy_Unknown", "--format", "json")
        data = json.loads(result.stdout)
        assert data[0]["found"] is False
        assert data[0]["canonical"] is None

    def test_json_multiple(self):
        result = run("Timothy", "Gail", "--format", "json")
        data = json.loads(result.stdout)
        assert len(data) == 2
        assert data[1]["canonical"] == "Abigail"


class TestLanguageFlag:
    def test_language_annotations_included(self):
        result = run("Abigail", "--language", "--format", "json")
        data = json.loads(result.stdout)
        variant_strs = data[0]["variants"]
        assert any("Irish" in v for v in variant_strs)

    def test_no_language_flag_strips_annotations(self):
        result = run("Abigail", "--format", "json")
        data = json.loads(result.stdout)
        variant_strs = data[0]["variants"]
        assert not any("(" in v for v in variant_strs)


class TestStdin:
    def test_stdin_reads_names(self):
        result = run("--stdin", stdin="Timothy\nAbigail\n")
        assert result.returncode == 0
        assert "Timothy" in result.stdout
        assert "Abigail" in result.stdout

    def test_stdin_combined_with_args(self):
        result = run("Gail", "--stdin", stdin="Timothy\n")
        assert result.returncode == 0
        assert "Abigail" in result.stdout
        assert "Timothy" in result.stdout


class TestNoArgs:
    def test_no_args_exits_nonzero(self):
        result = run()
        assert result.returncode != 0
