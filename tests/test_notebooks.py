"""Repository checks for the five clean, credential-free lessons."""

import json
from pathlib import Path

EXPECTED_NOTEBOOKS = [
    "01_first_harborlight_response.ipynb",
    "02_structured_renewal_review.ipynb",
    "03_function_tools.ipynb",
    "04_conversation_state.ipynb",
    "05_web_search_and_evidence.ipynb",
]


def test_exactly_five_active_lessons_with_no_committed_outputs() -> None:
    notebook_dir = Path("notebooks")
    names = sorted(path.name for path in notebook_dir.glob("*.ipynb"))
    assert names == EXPECTED_NOTEBOOKS
    for name in names:
        notebook = json.loads((notebook_dir / name).read_text(encoding="utf-8"))
        for cell in notebook["cells"]:
            if cell["cell_type"] == "code":
                assert cell.get("execution_count") is None
                assert cell.get("outputs", []) == []


def test_lessons_default_to_fixture_mode() -> None:
    for name in EXPECTED_NOTEBOOKS:
        text = (Path("notebooks") / name).read_text(encoding="utf-8")
        assert "HARBORLIGHT_LIVE" in text
        assert "Recorded demonstration fixture" in text or "FIXTURE_LABEL" in text