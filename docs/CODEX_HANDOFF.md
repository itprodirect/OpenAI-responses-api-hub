# Codex handoff

Date: 2026-07-14
Branch: `feat/harborlight-responses-101`
Draft PR: https://github.com/itprodirect/OpenAI-responses-api-hub/pull/11 (open, unmerged)

## Commit list

1. `7ee346c` — `docs: define Harborlight Responses rebuild`
2. `4eb0bfe` — `feat: add Harborlight deterministic core`
3. `d5ddeb3` — `feat: build Harborlight Responses curriculum`
4. `4215fed` — `feat: add Harborlight Renewal Desk`
5. `ab45935` — `feat: add optional Responses-to-MCP adapter`
6. `HEAD` — `docs: prepare Harborlight Responses flagship release` (sixth and final feature commit)

## Accepted Fable recommendations

- Harborlight is the single fictional teaching universe, with the MCP CSV mirrored byte-for-byte and independently packaged.
- The repository now uses a `src/` package, `pyproject.toml`, pytest, Ruff, CI, and clean notebook execution.
- The stale manually maintained model catalog is gone; model selection is a small environment-only resolver.
- Business services are deterministic and independently testable without OpenAI or MCP.
- Strict fictional-data contracts, integer cents, and Decimal percentage rounding are enforced.
- The function-tool lesson and helper implement the complete `function_call` → local execution → `function_call_output` → continuation sequence.
- Observable requests, validated arguments, tool output, evidence, usage, latency, and concise rationale replace pseudo-chain-of-thought claims.
- Useful historical material is archived; scratch and third-party noise is removed from the tree.
- Demo fixtures are conspicuously labeled and still exercise real deterministic services.

## Modified recommendations

- The mission's exact five core lessons take precedence over Fable's four-plus-MCP-capstone sequence. Hosted web search is lesson 5; MCP is a separate optional advanced adapter.
- Maintained notebooks have no committed execution output. Deterministic and model-facing example values live in validated package fixtures or explanatory markdown.
- The app's fixture mode remains narrow but supports both requested workflows and executes the actual deterministic services.
- Raw HTTP was removed from the primary curriculum and not added as an appendix because it did not add a distinct version-one learning objective.
- The model override name follows the mission's `OPENAI_DEFAULT_MODEL`, not Fable's alternate suggestion.

## Intentionally postponed

- File search and vector stores.
- Native remote Responses MCP, hosted MCP deployment, and remote approval/auth flows.
- Streaming as a sixth lesson, broad model discovery, programmatic tool search, multi-agent orchestration, and a live canary CI job.
- Authentication, accounts, databases, telemetry, production deployment, and a general chatbot.
- Screenshots until an identifier-free, path-free capture is worth maintaining.

## Removed and archived legacy artifacts

Removed:

- `Introduction-to-OpenAI-Responses-API-mervin-praison.txt`
- `notebooks/test_openai_connection.ipynb`
- `requirements.txt`
- the obsolete `utils/` package and model catalog

Archived under `archive/legacy_notebooks/`:

- `01_basic_chatbot.ipynb`
- `02_tools_and_reasoning.ipynb`
- `03_structured_outputs.ipynb`
- `04_multi_step_tools.ipynb`

Historical reviews moved to `docs/history/`. The locally supplied `docs/FABLE_RECOMMENDATIONS.md` remains byte-for-byte preserved with SHA-256 `5D8AFE4153ECD09306CFA5899BC1A8AE2C48D9BE23A7C5AD8DBC5736F47B0A33`.

## Exact validation commands and outcomes

See `docs/VALIDATION.md` for the command transcript. Summary:

- `python -m pip install -e ".[dev]"` — PASS in the fresh Python 3.12 environment.
- `python -m ruff check . --no-cache` — PASS.
- `python -m pytest -p no:cacheprovider` — PASS, 65 tests.
- Five demo-mode `nbconvert --execute` runs — PASS.
- Application import, Blocks construction, and both demo service paths — PASS.
- `pytest tests/test_mcp_adapter.py` — PASS, 6 tests without the sibling repository.
- Active-tree secret/path/identifier/stale-model searches — PASS, no matches.
- README Markdown parse, GitHub recognition of both Mermaid blocks, and `git diff --check` — PASS.

## Live behaviors tested

- Credential discovery was verified without exposing the key.
- A live lesson-1 request reached the OpenAI Responses endpoint and returned a clear SDK `RateLimitError` for HTTP 429 `insufficient_quota`.

## Live behaviors not tested

No live request completed because the available project had insufficient quota. Live text output, typed parsing, function tools, `previous_response_id`, Conversations API state, hosted web search evidence, usage reporting, and live app workflows remain unverified against an accepting project. No result is fabricated.

## Known limitations

- GitHub Actions passed the keyless workflow on Python 3.10 and 3.13 after publication; confirm the final PR head remains green.
- GitHub's Markdown API recognizes both Mermaid blocks; their visual appearance remains controlled by GitHub's renderer.
- The web fixture is dated 2026-07-14 and is demonstration history, never current guidance.
- The MCP adapter requires a separately installed, explicitly configured local server package for a real capstone run.
- Default model identifiers are current as of 2026-07-14 and intentionally centralized because model names change.

## Recommended focus for Claude review

1. Compare every OpenAI request shape with the current official docs, especially Conversations and hosted web-search source inclusion.
2. Inspect lesson 3's bounded continuation loop and event transparency for beginner clarity.
3. Confirm the app's live failure messages remain clear under actual model/tool errors.
4. Verify CI on both Python versions and render both README Mermaid diagrams on GitHub.
5. Recheck the fictional-data and repository-hygiene boundaries, including archive exclusions.
6. If quota becomes available, execute all five lessons and both live app workflows, then record usage without committing IDs.
