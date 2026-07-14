# Release validation

Date: 2026-07-14
Branch: `feat/harborlight-responses-101`
Base: Responses repository `origin/main` at `c80cdf14ec959fa261bac216060b7151da7407b6`

## Environment

- Windows PowerShell
- Python 3.12.3
- OpenAI Python SDK 2.45.0
- Pydantic 2.13.4
- Gradio 6.20.0
- MCP Python SDK 1.28.1
- MCP dataset source commit: `c872f1d46182bf191947a2477d4b0487f970c7f2`
- Mirrored CSV Git blob: `2d8498cf92018495db1c238080ca881f1ef36071`

## Commands and outcomes

### Fresh environment and installation

~~~powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
~~~

Outcome: PASS. The editable project and all development extras installed from `pyproject.toml`. The final install completed in 131.8 seconds.

### Lint

~~~powershell
.\.venv\Scripts\python.exe -m ruff check . --no-cache
~~~

Outcome: PASS — `All checks passed!`

### Offline tests

~~~powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
~~~

Outcome: PASS — 65 tests passed in 31.34 seconds.

### Five keyless notebooks

A temporary kernelspec pointing to the fresh environment was installed under ignored `.notebook-output/`. Then:

~~~powershell
$env:OPENAI_API_KEY = $null
$env:HARBORLIGHT_LIVE = "0"
$env:JUPYTER_PATH = ".notebook-output/kernel-prefix/share/jupyter"
Get-ChildItem notebooks/*.ipynb | Sort-Object Name | ForEach-Object {
    .\.venv\Scripts\python.exe -m jupyter nbconvert --to notebook --execute $_.FullName --output $_.Name --output-dir .notebook-output/executed --ExecutePreprocessor.kernel_name=harborlight-validation --ExecutePreprocessor.timeout=180
}
~~~

Outcome: PASS — all five notebooks executed from a clean state in 87.8 seconds. Windows emitted the expected local ZeroMQ selector/TCP warnings; no notebook failed. Executed copies are ignored and the maintained notebooks retain empty outputs and null execution counts.

### Application import and demo services

~~~powershell
.\.venv\Scripts\python.exe -c "from app.harborlight_renewal_desk import build_app, run_structured_workflow, run_tool_workflow; assert build_app() is not None; assert 'Recorded demonstration fixture' in str(run_structured_workflow('Demo Fixture', 'FIC-HLA-1002')); assert run_tool_workflow('Demo Fixture', 'FIC-HLA-1002', 30)['deterministic_output']; print('app import and demo workflows: PASS')"
~~~

Outcome: PASS — the module imported without launching, Gradio Blocks built, the structured fixture was labeled, and the deterministic tool workflow executed.

### Optional MCP adapter

~~~powershell
.\.venv\Scripts\python.exe -m pytest tests/test_mcp_adapter.py -p no:cacheprovider
~~~

Outcome: PASS — 6 tests passed in 0.31 seconds without the sibling MCP repository or a live server.

### Repository hygiene

~~~powershell
.\.venv\Scripts\python.exe -m pytest tests/test_repository_hygiene.py -p no:cacheprovider
rg -n --hidden <active-file exclusions> 'sk-[A-Za-z0-9_-]{8,}' .
rg -n --hidden <active-file exclusions> 'C:\\Users\\' .
rg -n --hidden <active-file exclusions> '(resp|conv)_[A-Za-z0-9]{12,}' .
rg -n --hidden <active-file exclusions> '<removed-model-regex>' .
~~~

Outcome: PASS — no maintained-file match for API keys, absolute Windows user paths, reusable response/conversation IDs, or the removed stale model catalog. The web-search lesson contains `date.today()` only to stamp live execution and prose explicitly warning against saved relative-date claims; active notebooks have no committed output.

### README and diff review

~~~powershell
.\.venv\Scripts\python.exe -c "from pathlib import Path; from markdown_it import MarkdownIt; text=Path('README.md').read_text(encoding='utf-8'); tokens=MarkdownIt().parse(text); mermaid=[t for t in tokens if t.type=='fence' and t.info.strip()=='mermaid']; assert len(mermaid)==2; assert all(t.content.strip() for t in mermaid); assert text.count('~~~') % 2 == 0; print('README parse: PASS')"
git diff --check
git diff --stat
git status --short
~~~

Outcome: PASS — the README parsed, both Mermaid source blocks were present and nonempty, fences were balanced, whitespace checks passed, and the complete feature diff was reviewed for scope. Diagram source was inspected locally, and GitHub's Markdown API recognized the README heading and both Mermaid blocks after publication.

## Live API attempt

The existing `OPENAI_API_KEY` was detected without printing it. A live execution of lesson 1 reached `client.responses.create` using the configured default model, but the API returned HTTP 429 with `insufficient_quota` on the first request. The remaining live lessons were not attempted to avoid repeated failed calls.

No live Responses request completed. Therefore typed parsing, function-tool continuation, Conversations state, hosted web search, live usage reporting, and live app behavior are not claimed as live-tested. Their request shapes and behavior are covered by offline fakes, schema tests, deterministic tests, current official documentation, and keyless notebook execution.

## CI status

The workflow is configured for Python 3.10 and 3.13 with no credentials. Draft PR #11 is open. GitHub Actions passed the complete keyless workflow on Python 3.10 and 3.13 after publication. The workflow was then narrowed to avoid duplicate push and pull-request matrices; the final PR head is expected to retain the same two-version validation.
