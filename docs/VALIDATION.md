# Release validation

Date: 2026-07-14 (America/New_York, UTC-04:00)
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

## Offline commands and outcomes

### Installation baseline

~~~powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
~~~

Outcome: PASS. The editable project and all development extras installed from `pyproject.toml`. The release environment resolves OpenAI 2.45.0 inside the declared `openai>=2.45,<3` range.

### Lint and complete test suite

~~~powershell
.\.venv\Scripts\python.exe -m ruff check . --no-cache
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
~~~

Outcome: PASS. Ruff reported `All checks passed!`; pytest passed 71 tests in 23.47 seconds. The suite includes deterministic data/services, configuration, typed outputs, function-tool continuation, app workflows, MCP adapter behavior, notebook contracts, fixture provenance, encoding, and repository hygiene.

### Five keyless notebooks

A temporary kernelspec points to the release environment under ignored `.notebook-output/`.

~~~powershell
$env:OPENAI_API_KEY = $null
$env:HARBORLIGHT_LIVE = "0"
$env:JUPYTER_PATH = ".notebook-output/kernel-prefix/share/jupyter"
Get-ChildItem notebooks/*.ipynb | Sort-Object Name | ForEach-Object {
    .\.venv\Scripts\python.exe -m jupyter nbconvert --to notebook --execute $_.FullName --output $_.Name --output-dir .notebook-output/executed --ExecutePreprocessor.kernel_name=harborlight-validation --ExecutePreprocessor.timeout=180
}
~~~

Outcome: PASS. All five notebooks executed from clean state without credentials in 56.5 seconds. Executed copies remain ignored; maintained notebooks have empty outputs and null execution counts.

### Application import and demo workflows

~~~powershell
.\.venv\Scripts\python.exe -c "from app.harborlight_renewal_desk import build_app, run_structured_workflow, run_tool_workflow; assert build_app() is not None; assert 'Authored demonstration fixture - no live OpenAI API call was made.' in str(run_structured_workflow('Demo Fixture', 'FIC-HLA-1002')); assert run_tool_workflow('Demo Fixture', 'FIC-HLA-1002', 30)['deterministic_output']; print('app import and demo workflows: PASS')"
~~~

Outcome: PASS. Import did not launch a server, Blocks built, the exact authored-fixture label appeared, and both demo paths executed deterministic Harborlight services.

### Optional MCP adapter

~~~powershell
.\.venv\Scripts\python.exe -m pytest tests/test_mcp_adapter.py -p no:cacheprovider
~~~

Outcome: PASS. Six tests passed without the sibling MCP repository or a live server. Command construction uses argument lists and mocks; no shell execution is used.

### Repository hygiene and diff

~~~powershell
.\.venv\Scripts\python.exe -m pytest tests/test_repository_hygiene.py -p no:cacheprovider
git diff --check
~~~

Outcome: PASS. Active files contain no committed API key, absolute Windows user path, reusable response/conversation identifier, stale model catalog, Unicode replacement character, known corrupted lesson title, or claim that an authored fixture is model-captured output. The exact Fable report remains byte-for-byte preserved.

README Markdown and both Mermaid source blocks were also parsed and checked; the complete remediation diff was reviewed for scope.

## Bounded live API validation

The existing `OPENAI_API_KEY` was detected without printing it. After a single 30-second propagation allowance, the funded project accepted requests. No request headers, billing details, full response IDs, conversation IDs, secrets, or raw model responses were printed or committed.

Lesson 1 used `gpt-5.6-terra`. Every remaining cost-conscious smoke scenario used `gpt-5.6-luna`.

| Required scenario | Final status | Model | Latency | Usage returned | Observable boundary confirmed |
|---|---|---|---:|---:|---|
| Lesson 1 basic text and usage | PASS | `gpt-5.6-terra` | 5189.0 ms | 82 input / 105 output / 187 total | Nonempty `output_text` and usage |
| Lesson 2 typed `responses.parse` | PASS through the shared live helper | `gpt-5.6-luna` | 3643.5 ms for the confirming shared workflow | 281 input / 198 output / 479 total | Parsed `RenewalReview` and deterministic arithmetic verification |
| Lesson 3 function-call round trip | PASS | `gpt-5.6-luna` | 4001.8 ms | 900 input / 240 output / 1140 total | Two function calls, validated arguments, two `function_call_output` items, final answer |
| Lesson 4 `previous_response_id` | PASS | `gpt-5.6-luna` | 5468.9 ms | 361 input / 394 output / 755 total | Two linked turns |
| Lesson 4 Conversations API | PASS | `gpt-5.6-luna` | 10790.9 ms | 891 input / 608 output / 1499 total | Conversation creation, three turns, and cleanup |
| Lesson 5 hosted web search | PASS | `gpt-5.6-luna` | 12081.9 ms | 12791 input / 1101 output / 13892 total | One web-search call, 23 sources, and 6 URL citations |
| Renewal Desk live structured workflow | PASS after remediation | `gpt-5.6-luna` | 3643.5 ms | 281 input / 198 output / 479 total | Structured panel data and deterministic arithmetic verification |
| Renewal Desk live tool-assisted workflow | PASS | `gpt-5.6-luna` | 5926.4 ms | 711 input / 202 output / 913 total | Both requested tools, two deterministic results, and final answer |

The Lesson 2 and Renewal Desk structured rows intentionally refer to the same confirming live request: the app calls the exact `parse_renewal_review` helper taught by Lesson 2. This proves both the typed SDK path and the live app integration without spending on a duplicate request.

### Typed-schema remediation history

The initial Lesson 2 and Renewal Desk structured attempts each returned sanitized HTTP 400 `invalid_json_schema` errors (200.2 ms and 733.0 ms). The Pydantic model was then changed to emit the API-supported strict JSON Schema subset while retaining date, Decimal, positive-cents, summary-length, and action-count checks during local Pydantic validation.

One standalone corrective Lesson 2 request was sent before the confirming app request. A local import-harness failure occurred after that request and before the sanitized result was emitted. It was not repeated. Its result and usage are therefore not claimed. The subsequent one-time Renewal Desk request completed successfully through the same helper and supplies the confirming typed-output evidence in the table.

Across the bounded pass, 15 Responses requests were attempted: 12 have confirmed successful results, two are the confirmed initial schema failures, and one corrective result was not captured. The Conversations create and cleanup operations also succeeded. Confirmed successful Responses usage totals 15,736 input plus 2,650 output tokens from the initial pass, plus 281 input and 198 output tokens from the confirming structured request (18,865 total tokens). Usage for the uncaptured request is unknown and excluded.

No quota retry loop was used. Tool calls and citations were observed where required. Identifiers and secrets were kept out of output and source control.

## CI status

The workflow targets Python 3.10 and 3.13 without credentials. Draft PR #11 remains open, draft, and unmerged. The baseline PR checks were green on both versions before remediation; the remediation-head checks must be confirmed after push and are the authoritative CI result.
