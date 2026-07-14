# Codex handoff

Date: 2026-07-14 (America/New_York)
Branch: `feat/harborlight-responses-101`
Draft PR: https://github.com/itprodirect/OpenAI-responses-api-hub/pull/11 (open, draft, unmerged)
Independent review destination: `docs/CLAUDE_RELEASE_REVIEW.md` (Claude must author this file; Codex did not create it)

## Commit list

1. `7ee346c` - `docs: define Harborlight Responses rebuild`
2. `4eb0bfe` - `feat: add Harborlight deterministic core`
3. `d5ddeb3` - `feat: build Harborlight Responses curriculum`
4. `4215fed` - `feat: add Harborlight Renewal Desk`
5. `ab45935` - `feat: add optional Responses-to-MCP adapter`
6. `98ea166` - `docs: prepare Harborlight Responses flagship release`
7. `HEAD` - `fix: address Harborlight release review` (focused remediation commit)

## Accepted Fable recommendations

- Harborlight remains the single fictional teaching universe, with the MCP CSV mirrored byte-for-byte and independently packaged.
- The repository uses a `src/` package, `pyproject.toml`, pytest, Ruff, CI, and clean notebook execution.
- The stale model catalog remains removed; model selection is a small environment-only resolver.
- Deterministic business services remain independently testable without OpenAI or MCP.
- Strict fictional-data contracts, integer cents, and Decimal percentage rounding remain enforced.
- The function-tool lesson implements `function_call` -> local execution -> `function_call_output` -> continuation.
- Observable requests, validated arguments, tool output, evidence, usage, and latency replace pseudo-chain-of-thought claims.
- Useful historical material remains archived; scratch and third-party noise remains removed.
- Credential-free material is now consistently described as authored fixture content, never as captured model output.

## Modified recommendations

- The exact five-lesson mission still takes precedence over Fable's four-plus-capstone sequence.
- Maintained notebooks retain no committed execution output. Authored fixture values live in validated package data and explanatory Markdown.
- Demo mode remains narrow while executing real deterministic services.
- Raw HTTP remains outside the primary curriculum because it adds no version-one learning objective.
- `OPENAI_DEFAULT_MODEL` remains the model override.
- The structured-output Pydantic contract now emits a conservative API-supported JSON Schema while enforcing richer constraints locally after parsing.

## Intentionally postponed

- File search and vector stores.
- Native remote Responses MCP, hosted MCP deployment, and remote approval/auth flows.
- Streaming as a sixth lesson, broad model discovery, programmatic tool search, multi-agent orchestration, and live canary CI.
- Authentication, accounts, databases, telemetry, production deployment, and a general chatbot.
- Screenshots until a durable identifier-free capture is useful.

## Release-review remediation

- Replaced every active claim that fixture content was captured from a model with the canonical label: `Authored demonstration fixture - no live OpenAI API call was made.`
- Updated Python fixtures, notebooks, app labels, tests, README, plan, validation notes, docstrings, and comments to use authored-fixture terminology.
- Repaired all five lesson titles and known punctuation substitutions; active-file hygiene tests now reject corrupted title markers and Unicode replacement characters.
- Added a hygiene guard against future claims that authored fixtures are model-captured output.
- Ran the bounded Terra/Luna live pass and documented successes, initial typed-schema failures, corrective validation, usage, latency, tools, citations, and identifier handling in `docs/VALIDATION.md`.
- Simplified only the model-facing structured JSON Schema; local Pydantic and deterministic checks remain strict.
- Removed `load_local_environment` and the `python-dotenv` dependency after repository search confirmed zero consumers. Other optional cleanup remains version-two work.
- Preserved `docs/FABLE_RECOMMENDATIONS.md` byte-for-byte with SHA-256 `5D8AFE4153ECD09306CFA5899BC1A8AE2C48D9BE23A7C5AD8DBC5736F47B0A33`.

## Removed and archived legacy artifacts

The release-remediation pass did not broaden legacy cleanup. The earlier feature work removed the root transcript, scratch connection notebook, `requirements.txt`, and obsolete model catalog; it archived the four useful historical notebooks under `archive/legacy_notebooks/`.

## Exact validation commands and outcomes

See `docs/VALIDATION.md` for the full command record and live table.

- `.\.venv\Scripts\python.exe -m ruff check . --no-cache` - PASS.
- `.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider` - PASS, 71 tests.
- Five keyless `nbconvert --execute` runs - PASS.
- Application import, Blocks construction, and both demo workflows - PASS.
- Live structured and live tool-assisted application workflows - PASS on Luna after the documented schema remediation.
- `pytest tests/test_mcp_adapter.py -p no:cacheprovider` - PASS, 6 tests without the sibling repository.
- Fixture-provenance, notebook-encoding, secret/path/identifier/stale-model hygiene - PASS.
- README parse, both Mermaid source blocks, and `git diff --check` - PASS.

## Live behaviors tested

- Terra: Lesson 1 text response and usage.
- Luna: typed `responses.parse`, a genuine multi-tool round trip, `previous_response_id`, Conversations state, hosted web search with included sources/citations, and both live Renewal Desk workflows.
- The tool validation observed both tool calls and both returned `function_call_output` items.
- The hosted-search validation observed 23 sources and 6 URL citations.
- No raw model output, API key, response ID, conversation ID, request header, or billing detail was committed.

## Live-validation caveats

- Two initial typed-schema calls returned sanitized HTTP 400 `invalid_json_schema`; the confirming structured app request passed after remediation.
- One standalone corrective Lesson 2 request result was lost when the local harness failed after the request. It was not repeated. Lesson 2 is confirmed through the successful app call because the app uses the same `parse_renewal_review` helper.
- Confirmed usage excludes the uncaptured corrective request.

## Known limitations

- The web fixture is dated authored evidence from 2026-07-14, never current guidance.
- Live web results are nondeterministic and may change after this validation date.
- The MCP adapter still requires a separately installed, explicitly configured local server package for a real capstone run.
- Default model identifiers are current as of 2026-07-14 and intentionally centralized.
- File search, native remote MCP, authentication, databases, and production deployment remain outside version one.

## Exact Claude re-review instructions

Claude should perform an independent release review and write its own conclusions to `docs/CLAUDE_RELEASE_REVIEW.md`. Do not present this Codex handoff as Claude's review and do not reconstruct a review from it.

1. Review the remediation commit and the full PR #11 diff against version-one scope; do not request version-two features as release blockers.
2. Confirm the canonical authored-fixture label appears everywhere required and that no active file describes those fixtures as captured model output.
3. Inspect all five maintained notebooks for ASCII-safe titles, clean Markdown/source strings, empty committed outputs, null execution counts, and credential-free execution.
4. Compare the typed `responses.parse` schema and post-parse validators with current official OpenAI Structured Outputs guidance.
5. Re-review the function-tool continuation loop, Conversations usage, hosted-search source inclusion, and visible app boundaries.
6. Verify the bounded live-validation table is internally consistent, preserves the two initial failures and uncaptured result, and contains no secret or reusable identifier.
7. Confirm local tests and the PR's Python 3.10/3.13 checks are green, PR #11 remains draft, and no merge occurred.
8. Focus the final review on release blockers, correctness, beginner clarity, fixture provenance, encoding hygiene, and scope discipline.
