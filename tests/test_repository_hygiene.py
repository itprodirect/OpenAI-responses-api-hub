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


def test_no_shell_true_in_active_python() -> None:
    for path in active_text_files():
        if path.suffix == ".py":
            assert "shell=True" not in path.read_text(encoding="utf-8")