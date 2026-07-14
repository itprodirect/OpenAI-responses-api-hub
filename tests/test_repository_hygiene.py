"""Repository-level checks for secrets, machine state, stale IDs, and notebook output."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {
    ".git",
    ".venv",
    "archive",
    ".notebook-output",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
}
SKIP_PATHS = {
    Path("docs/FABLE_RECOMMENDATIONS.md"),
    Path("docs/history/REPO_REVIEW.md"),
    Path("docs/history/UPGRADE_REVIEW.md"),
    Path("tests/test_repository_hygiene.py"),
}
TEXT_SUFFIXES = {".py", ".md", ".toml", ".yml", ".yaml", ".json", ".csv", ".ipynb"}


def active_text_files() -> list[Path]:
    files = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        relative = path.relative_to(ROOT)
        if any(part in SKIP_PARTS or part.endswith(".egg-info") for part in relative.parts):
            continue
        if relative in SKIP_PATHS:
            continue
        files.append(path)
    return files


def test_no_committed_secrets_machine_paths_or_live_identifiers() -> None:
    patterns = {
        "API key": re.compile(r"sk-[A-Za-z0-9_-]{8,}"),
        "Windows user path": re.compile(r"C:\\Users\\", re.IGNORECASE),
        "response ID": re.compile(r"resp_[A-Za-z0-9]{12,}"),
        "conversation ID": re.compile(r"conv_[A-Za-z0-9]{12,}"),
    }
    for path in active_text_files():
        text = path.read_text(encoding="utf-8")
        for label, pattern in patterns.items():
            assert not pattern.search(text), f"{label} found in {path.relative_to(ROOT)}"


def test_no_old_model_catalog_or_stale_active_models() -> None:
    assert not (ROOT / "utils/models.py").exists()
    stale = ["gpt-4.1-mini", "gpt-4.1-mini-transcribe", "o4-mini", "gpt-image-1"]
    for path in active_text_files():
        if path == Path(__file__):
            continue
        text = path.read_text(encoding="utf-8")
        for model in stale:
            assert model not in text, f"stale model {model} in {path.relative_to(ROOT)}"


def test_active_notebooks_have_no_committed_execution_output() -> None:
    for path in (ROOT / "notebooks").glob("*.ipynb"):
        notebook = json.loads(path.read_text(encoding="utf-8"))
        for cell in notebook["cells"]:
            if cell["cell_type"] == "code":
                assert cell.get("execution_count") is None
                assert cell.get("outputs", []) == []


def test_authored_fixtures_are_not_described_as_recorded_model_output() -> None:
    forbidden = re.compile(
        r"\brecorded "
        r"(?:demonstration|fixture|model|generated|typed|output|facts|evidence|"
        r"interpretation)",
        re.IGNORECASE,
    )
    for path in active_text_files():
        text = path.read_text(encoding="utf-8")
        assert not forbidden.search(text), (
            f"authored fixture has recorded-output provenance in {path.relative_to(ROOT)}"
        )


def test_active_notebook_source_has_no_known_encoding_corruption() -> None:
    corrupt_title = re.compile(r"^# Lesson [1-5] \? ", re.MULTILINE)
    known_substitutions = ("Renewal note ?", "explicit?but", "?current.?", "?today?")
    for path in (ROOT / "notebooks").glob("*.ipynb"):
        notebook = json.loads(path.read_text(encoding="utf-8"))
        source = "\n".join(
            "".join(cell.get("source", [])) for cell in notebook.get("cells", [])
        )
        assert not corrupt_title.search(source), f"corrupt lesson title in {path.name}"
        assert "\ufffd" not in source, f"Unicode replacement character in {path.name}"
        for substitution in known_substitutions:
            assert substitution not in source, f"corrupt punctuation in {path.name}"


def test_active_text_has_no_replacement_or_common_mojibake_characters() -> None:
    mojibake = ("\ufffd", "â€”", "â€“", "â€™", "â€œ", "â€", "â†’", "Ã", "Â")
    for path in active_text_files():
        text = path.read_text(encoding="utf-8")
        for marker in mojibake:
            assert marker not in text, f"encoding corruption in {path.relative_to(ROOT)}"

def test_no_shell_true_in_active_python() -> None:
    for path in active_text_files():
        if path.suffix == ".py":
            assert "shell=True" not in path.read_text(encoding="utf-8")
