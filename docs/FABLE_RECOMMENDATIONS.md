# Fable Recommendations: Rebuilding the OpenAI Responses API Hub around Harborlight Insurance Agency

**Author:** Claude (Fable 5), acting as senior AI developer-education architect and critical reviewer
**Date:** 2026-07-14
**Scope:** `itprodirect/OpenAI-responses-api-hub` (target), `itprodirect/Model-Context-Protocol-101` (reference, read-only)

---

## How this review was performed

- Full file-level inspection of both repositories — source, tests, notebooks (including cell-level content, execution counts, and committed outputs), dependency files, docs, and git history. Not just the READMEs.
- Comparison of local clones against GitHub `origin/main` for both repos.
- Verification of current API patterns against official OpenAI documentation (developers.openai.com: models, deprecations, structured outputs, conversation state, tools) and current PyPI releases, as of July 2026.

### Two housekeeping findings before anything else

1. **The local clone of Model-Context-Protocol-101 on this machine is badly stale.** Local `main` predates the entire Harborlight rebuild; `origin/main` is at the "Harborlight final polish" merge. The local working tree also has uncommitted modifications to `.gitignore`, `README.md`, and `requirements.txt`. Before mirroring any Harborlight data into this repo, reconcile and pull that clone. (This review analyzed `origin/main`, the real reference.)
2. **The local clone of this repo is one commit behind** `origin/main` (`c80cdf1` adds `docs/REPO_REVIEW.md`). Pull before starting PR 1.

### Verified current API facts (July 2026, official docs)

These are the facts this report's recommendations rest on. Each was checked against developers.openai.com in July 2026; re-verify at implementation time, because several will keep moving.

| Fact | Status |
|---|---|
| Current frontier family | **GPT-5.6**: `gpt-5.6-sol` (alias `gpt-5.6`), `gpt-5.6-terra` (balanced), `gpt-5.6-luna` (cost-efficient); ~1M context, 128K max output |
| `o4-mini` (in this repo's catalog) | **Shutdown 2026-10-23**; docs point to `gpt-5.4-mini` as replacement |
| `gpt-4.1` / `gpt-4.1-mini` (this repo's defaults) | Not yet formally deprecated, but removed from the main models page — legacy |
| `gpt-4.1-mini-transcribe` (in this repo's catalog) | **Does not exist.** Real IDs: `gpt-4o-transcribe`, `gpt-4o-mini-transcribe` |
| `gpt-image-1` (in this repo's catalog) | Superseded by GPT Image 2 |
| Assistants API | **Shutdown 2026-08-26**; migrate to Responses API + Conversations API |
| Structured outputs, recommended pattern | `client.responses.parse(..., text_format=PydanticModel)` → `response.output_parsed`; manual `text={"format": {"type": "json_schema", ...}}` remains valid |
| Conversation state, recommended pattern | **Conversations API** (durable conversation object) is the documented recommendation; `previous_response_id` remains valid for short chains; responses retained 30 days by default (`store: false` to opt out); all chained input tokens are billed each turn |
| Hosted tool types | `web_search` (no longer `web_search_preview`), `file_search` (+`vector_store_ids`), `function`, `mcp` (remote, `server_url`/`server_label`/`require_approval`), plus newer `tool_search`/`namespace` (gpt-5.4+) |
| Python SDK | `openai` 2.45.0 (2.x major — the repo pins `>=1.40.0`, which silently spans a breaking major); Python ≥3.9 |
| Gradio | 6.20.0 (repo's unpinned `gradio` line would today install 6.x) |

---

## Position on the baseline proposal

The working proposal is directionally right: Harborlight as shared universe, `src/` package, `pyproject.toml`, Ruff/pytest/CI/notebook smoke tests, one coherent learning path, a small Gradio app, MCP bridge as capstone, archive rather than delete. **Adopt all of that.**

Where this review disagrees or narrows the proposal:

1. **Seven notebooks is too many.** Five lessons (four core + one capstone) cover every capability the repo exists to teach. Web search and file search do not earn core-curriculum seats in v1 (reasons in §2 and §8).
2. **"Use the same fictional data" needs a mechanism, not a sentiment.** Mirror the CSV byte-for-byte with a contract test that enforces MCP-101's fictional-data rules; never import across repos at runtime (§3).
3. **Committed notebook outputs should go, not be curated.** The repo currently demonstrates exactly why: stale November-2025 concert listings and out-of-order execution counts are committed today. Replace with stripped outputs + "expected output" markdown + CI execution, the MCP-101 pattern (§8).
4. **The existing model catalog should be deleted, not ported.** It is already wrong (one nonexistent model, one model with a scheduled shutdown) after ~8 months. A hand-maintained five-category catalog is a churn magnet in an educational repo (§3).
5. **"Demo mode without an API key" must be narrow.** Deterministic *services* run offline; a *fake model* must not. One clearly labeled recorded transcript in the app, nothing more (§4, §5).
6. **The prompt-engineered "Reasoning:" section in notebook 02 is a pattern to reject**, not to carry forward — it teaches beginners that a model's post-hoc narrative is its reasoning. Replace with tool-activity inspection and structured decision summaries (§5).

---

## 1. Current repository diagnosis

### 1.1 Worth preserving (the repo is better than its packaging)

- **`utils/responses_api.py` core design.** `create_function_tool_response(...)` implements the canonical `function_call → execute → function_call_output → continue` loop correctly, including `call_id` plumbing and `previous_response_id` chaining. `extract_output_text(...)` correctly prefers `output_text` over positional parsing. `create_json_response(...)` uses the correct strict-schema `text.format` shape. These become the seed of the new package.
- **The offline test approach.** `tests/test_responses_api.py` is genuinely good: `SimpleNamespace` fakes, a `FakeStream`, assertions on the exact continuation payload (`previous_response_id`, `function_call_output` items). No live API calls in tests. Keep this style; port to pytest.
- **Lazy client + `.env` hygiene.** `get_openai_client()` is cached and lazy; `.env` is gitignored and has never been committed (verified against full history).
- **Notebooks 03 and 04's authorial voice.** Consistent structure, "Why this notebook matters" framing, deterministic tool sanity-check cells, no committed outputs. This is the tone the whole curriculum should have.
- **The documentation habit.** `docs/UPGRADE_REVIEW.md` and `docs/REPO_REVIEW.md` show a review-and-record culture worth keeping (this file continues it).
- MIT license, clean git history, no leaked secrets.

### 1.2 Should be rewritten

- **`utils/models.py` — factually wrong today.** `RECOMMENDED_MODELS` lists `gpt-4.1-mini-transcribe` (no such model — the real IDs are `gpt-4o-mini-transcribe`/`gpt-4o-transcribe`), `o4-mini` (shutdown scheduled 2026-10-23), `gpt-4.1`/`gpt-4.1-mini` (legacy), `gpt-image-1` (superseded). `choose_default_model()` also depends on dict insertion order for fallback — fragile. Replace with a two-entry resolver (§3.6).
- **`utils/config.py` — import-time constant.** `DEFAULT_MODEL = get_default_model()` runs at import, freezing the env read at first import; `docs/UPGRADE_REVIEW.md` claims import-time side effects were fixed, but this one remains. Make model resolution a function call, not a module constant.
- **`utils/responses_api.py`, two specifics:** the `modalities` parameter on `create_text_response(...)` is not part of the Responses API surface (Chat-Completions-era) and will produce an API error if anyone uses it — remove; the final `return getattr(response, "output_text", "") or ""` in `extract_output_text` is dead code (already checked at the top).
- **`invoke_function_tool_calls` error posture:** an unknown tool name raises `KeyError` and kills the loop. For teaching, return a structured error as the `function_call_output` so learners see how models recover from tool failures — then show the strict-raise variant as a comparison.
- **Notebook 01 (`01_basic_chatbot.ipynb`) — rewrite entirely.**
  - Its committed state only works when run out of order: cell 6 calls `os.path.join`/`os.getenv` but no earlier cell imports `os`; committed execution counts are `[8, 2, 3, 4, 5, 6, 7]` — the first cell was executed *eighth*.
  - Cell 2 contains the comment "same pattern as Notebook 01" *inside* notebook 01, and creates an SDK `client = OpenAI()` that the notebook never uses (it then does raw `requests.post`).
  - Identity crisis: titled "Build Your First Basic Chatbot," it is actually a raw-HTTP anatomy lesson. The raw-HTTP idea is worth keeping — as a labeled "under the hood" appendix, not the first thing a beginner sees.
  - Cell 12 parses `response_json["output"][0]["content"][0]["text"]` positionally — the classic beginner bug this repo should be *warning against* (breaks the moment the output array leads with a reasoning or tool item).
  - ELI5-with-emoji tone is inconsistent with notebooks 03/04 and undermines the "professional teaching resource" goal.
- **Notebook 02 (`02_tools_and_reasoning.ipynb`) — rewrite entirely.**
  - Committed outputs are stale live results: "concerts this weekend near Tampa" resolved to November 22–23, 2025. Unreproducible by construction and now visibly wrong in the rendered notebook.
  - The "agentic reasoning" section prompts the model to emit a `Reasoning:` section before the answer. This teaches pseudo-chain-of-thought as if it were the model's actual process (see §5 for the replacement).
  - The calculator section shows the model's `function_call` items but **never sends `function_call_output` back** — the loop is left half-finished, and cell 12 quietly computes the results locally in Python instead. A beginner walks away believing the model completed a tool round-trip that never happened. This is the single most misleading cell in the repo.
  - Hardcodes `model="gpt-4.1-mini"` in every call, bypassing the repo's own model helpers.
  - Committed execution counts `[4, 5, 8, 9, 10, 13, None]`: out-of-order, gappy, final cell never run.
- **README.md.** Structure block already drifts from reality (missing `docs/REPO_REVIEW.md`), documents `OPENAI_DEFAULT_MODEL=gpt-4.1-mini`, no badges, no diagrams, no fictional-data statement, no cost note, roadmap stale. Full rebuild alongside the curriculum.

### 1.3 Should be archived

- `notebooks/01_basic_chatbot.ipynb` and `notebooks/02_tools_and_reasoning.ipynb` → `archive/`, with a short note in the archive README that they predate the Harborlight rebuild and do not run against the current package (mirrors MCP-101's `archive/original_notebook.ipynb` convention).
- `docs/UPGRADE_REVIEW.md` and `docs/REPO_REVIEW.md` → keep, but move under `docs/history/` (or an "archive" heading) so first-time visitors don't mistake them for current docs.

### 1.4 Should be removed

- **`Introduction-to-OpenAI-Responses-API-mervin-praison.txt`** — a 14 KB transcript of a third-party YouTube video sitting at the repo root. It is someone else's content (attribution ≠ license), describes an early-2025 snapshot of the API, and signals "personal scratch folder" to visitors. Delete from the tree (git history preserves it if ever needed). Do not archive third-party content.
- **`notebooks/test_openai_connection.ipynb`** — a two-cell scratch notebook whose committed prompt is "Tell Nick how awesome he is at debugging AI APIs," with a committed live output. Its one useful job (verify key + connectivity) becomes a `python -m harborlight_responses.check` one-liner or a "Setup check" cell in lesson 01.
- **`requirements.txt`** — replaced by `pyproject.toml`. Today it pins nothing meaningful (`pandas`, `jupyter`, `gradio` unbounded; `openai>=1.40.0` silently spans the 1.x→2.x breaking major) and lists `gradio`, which nothing in the repo uses.

### 1.5 Technical debt inventory

| Debt | Where | Consequence |
|---|---|---|
| `sys.path` hacks instead of packaging | every notebook, cell 2 | Notebooks break depending on kernel cwd; the #1 beginner failure mode |
| No CI at all | repo root (no `.github/`) | The two broken notebooks shipped and nobody noticed |
| Stale/nonexistent model IDs | `utils/models.py`, README | First live call a learner makes may 404 on model |
| `openai>=1.40.0` unbounded | `requirements.txt` | Fresh installs get SDK 2.x against 1.x-era assumptions |
| unittest, not pytest; tests only in `tests/` root | `tests/` | Fine, but inconsistent with MCP-101 sibling and modern tooling |
| Committed outputs, inconsistently | nb 01/02 yes, nb 03/04 no | Stale, dated, out-of-order outputs render on GitHub |
| Import-time model resolution | `utils/config.py:28` | Frozen env reads, surprising in notebooks |
| Two fictional universes already | nb 03 (Northwind Health) vs nb 04 (Northwind + Blue Prairie) vs nb 02 (Tampa concerts) | No narrative continuity; exactly what Harborlight fixes |

### 1.6 Testing and CI gaps

- No workflow files. MCP-101's `ci.yml` (Python 3.10/3.13 matrix, ruff → pytest → `nbconvert --execute` of the tutorial) is the template — with one structural difference: this repo's notebooks make live API calls, so notebook execution in CI needs the offline-skip design in §3.8.
- No test covers `create_streaming_text_response` against the SDK 2.x streaming surface (events via `create(stream=True)` vs the `stream()` helper — verify during the port).
- No test enforces the fictional-data contract (MCP-101 has this; we need its mirror).

---

## 2. Narrative and curriculum design

### 2.1 The conceptual split (keep it sharp)

- **MCP 101:** how an *application* discovers and invokes external capabilities across a protocol boundary. The model is absent.
- **Responses API 101:** how a *model* generates responses, produces structured data, calls tools, and maintains workflow context. The protocol is absent — until the capstone, where the two repos meet on purpose.

The cleverest available teaching device is already sitting in MCP-101: `list_upcoming_renewals` and `calculate_premium_change`. **Reuse the exact same two business capabilities as Responses function tools.** A learner who does both repos sees the same deterministic services exposed two ways — once via MCP discovery/invocation, once via model-driven function calling — and the difference between the two technologies becomes self-evident rather than explained.

### 2.2 The curriculum: five lessons, one story

One story arc: *a Harborlight account manager works one renewal cycle, snapshot date 2026-07-01.* Every lesson answers a business question the previous lesson raised.

Naming: `notebooks/01_first_response.ipynb` … `05_capstone_mcp_bridge.ipynb` (final names at implementers' discretion; keep the two-digit prefix convention).

---

**Lesson 01 — First response and response anatomy**

| Aspect | Content |
|---|---|
| Learner objective | Make one Responses API call; understand the request (model, input, instructions) and the response (`output` items, `output_text`, `usage`) |
| Harborlight question | "Summarize the FIC-HLA-1002 renewal for an account manager in three sentences." (Policy record loaded from the packaged CSV and pasted into the prompt — no tools yet.) |
| Capability | `client.responses.create`, `instructions`, `output_text`, `usage`; setup check for the API key |
| Deterministic or live | Live (input deterministic, wording varies) — with the offline-skip guard (§3.8) |
| Expected output | A short prose summary; a printed `usage` line (input/output tokens); a labeled "expected output" markdown block for offline readers |
| Testing | CI executes the notebook; without a key, live cells print "Skipped — set OPENAI_API_KEY" and the notebook still completes. Unit tests cover the text-extraction helper offline |
| Beginner mistake to teach | Positional parsing (`output[0].content[0].text`) — show it break conceptually (output arrays can lead with reasoning/tool items), then show `output_text` |

Appendix cell (clearly labeled "Under the hood, optional"): one raw HTTP `POST /v1/responses` with the JSON printed — the good idea salvaged from old notebook 01, in its right place.

---

**Lesson 02 — Structured outputs**

| Aspect | Content |
|---|---|
| Learner objective | Turn model output into schema-validated data; understand what strict schemas do and don't guarantee |
| Harborlight question | "Turn this messy renewal-call note about Fictional Cedar Cycle Shop into a `RenewalReview` record" (fields: `policy_id`, `sentiment`, `action_items[]`, `decision_summary` — a one-sentence transparent rationale, see §5) |
| Capability | `client.responses.parse(..., text_format=RenewalReview)` with a Pydantic model; one cell showing the equivalent manual `text.format` JSON-schema payload so learners see what the SDK generates |
| Deterministic or live | Live; input text fixed in the notebook |
| Expected output | A validated `RenewalReview` instance rendered as dict + a one-row pandas table |
| Testing | Pydantic schemas unit-tested offline (validation, refusal-path handling with a faked refusal response); notebook smoke-executed |
| Beginner mistake to teach | Believing strict schema = correct values. The schema guarantees *shape*, not *truth*; show a deliberately underspecified note producing a confident-looking wrong field, then show how validation + human review catches it |

---

**Lesson 03 — Function tools and the tool loop**

| Aspect | Content |
|---|---|
| Learner objective | Define function tools, run the full `function_call → execute → function_call_output → continue` loop, inspect every step |
| Harborlight question | "Which policies renew in the next 30 days, and what are the proposed premium changes?" — the exact MCP-101 question, answered by the model orchestrating the same two services |
| Capability | `tools=[{"type": "function", ...}]`, the packaged tool registry, the shared loop helper; printing each `function_call` (name, arguments, `call_id`) and each `function_call_output` as it happens |
| Deterministic or live | Tool outputs fully deterministic (fixed snapshot 2026-07-01 → always FIC-HLA-1001/1002/1003 for 30 days); model narration live |
| Expected output | A tool-activity table (call #, tool, arguments, result) plus the model's final renewal briefing |
| Testing | The loop helper is already well-tested with fakes — port those tests; add a test for the unknown-tool and tool-exception paths; services tested deterministically |
| Beginner mistake to teach | The old notebook 02's own bug, named explicitly: showing `function_call` items and stopping. The model has *requested* work, not done it; nothing happens until your code executes the function and returns `function_call_output` with the matching `call_id` |

---

**Lesson 04 — Conversation state**

| Aspect | Content |
|---|---|
| Learner objective | Maintain multi-turn context three ways and know when to use each: manual input arrays, `previous_response_id`, and the Conversations API |
| Harborlight question | A three-turn review: "Which renewals land this month?" → "What's the premium change for the bookstore?" → "Draft a renewal email for it" — where turns 2–3 only work if state carries ("the bookstore" resolves to FIC-HLA-1002) |
| Capability | `previous_response_id` chaining; a Conversation object for the same exchange; `store` and the 30-day retention default; note that chained input tokens are re-billed every turn |
| Deterministic or live | Live; the anaphora resolution ("the bookstore") is the observable proof state works |
| Expected output | The same three-turn exchange run both ways, with a printed running token count making the billing model visible |
| Testing | Offline tests assert helpers pass `previous_response_id`/`conversation` correctly (extend the existing fake-client pattern); notebook smoke-executed |
| Beginner mistake to teach | Sending full history *and* `previous_response_id` together (double context, double cost); assuming server-side state is free or eternal |

---

**Lesson 05 — Capstone: the same tools over MCP**

| Aspect | Content |
|---|---|
| Learner objective | See that "the model calls a function" and "an application invokes an MCP tool" are different layers that compose: Responses function calling on the outside, MCP discovery/invocation on the inside |
| Harborlight question | Lesson 03's question again — but now the tool implementations live behind the MCP-101 stdio server, and this repo's code is an MCP *client* that adapts discovered MCP tools into Responses function tools |
| Capability | Local MCP bridge: `mcp` ClientSession over stdio → tool schemas → Responses `tools` list → loop routes `function_call` to `session.call_tool`. Closes with a short markdown comparison to the hosted `mcp` tool type (`server_url`, `require_approval`) as documented future work — no code |
| Deterministic or live | Tool layer deterministic (same data, same snapshot); model narration live; whole notebook skips gracefully if the optional `[mcp]` extra isn't installed |
| Expected output | Discovered tool list printed from the MCP session; then the same renewal briefing as lesson 03 — visibly identical answer, different plumbing |
| Testing | Bridge adapter unit-tested against a stubbed MCP session (schema translation, call routing); notebook guarded by both the key check and an import check |
| Beginner mistake to teach | Conflating "the model supports MCP" with "my app speaks MCP"; and printing to stdout inside a stdio MCP server (borrow MCP-101's troubleshooting entry) |

---

### 2.3 What did not make the core five

- **File search / mini-RAG** (v2): genuinely valuable and on-narrative (underwriting guidelines PDF, citations) — but it drags in vector stores, file uploads, storage lifecycle, and cleanup. That's a whole lesson's worth of *infrastructure* teaching. Defer to v2 as lesson 06, where its citation UI also strengthens the transparency story.
- **Web search** (v2 appendix at most): off-narrative for a fixed-snapshot insurance scenario, inherently non-reproducible, and the old notebook 02 is a standing demonstration of how it rots. If kept at all: a short appendix ("when your question genuinely needs the live web"), never a core lesson.
- **Streaming**: not a separate lesson; it appears as a labeled optional cell in lesson 01 and as the app's output mode. A dedicated streaming notebook is plumbing without a business question.

---

## 3. Technical architecture

### 3.1 Directory structure

```text
OpenAI-responses-api-hub/
├── .github/workflows/ci.yml
├── pyproject.toml
├── README.md
├── LICENSE
├── .gitattributes                  # like MCP-101: normalize line endings, mark ipynb
├── .gitignore
├── app/
│   └── renewal_desk.py             # single-file Gradio Blocks app
├── archive/
│   ├── README.md                   # "pre-Harborlight history, does not run"
│   ├── 01_basic_chatbot.ipynb
│   └── 02_tools_and_reasoning.ipynb
├── docs/
│   ├── FABLE_RECOMMENDATIONS.md    # this file
│   ├── assets/                     # screenshots, diagrams
│   └── history/                    # UPGRADE_REVIEW.md, REPO_REVIEW.md
├── notebooks/
│   ├── 01_first_response.ipynb
│   ├── 02_structured_outputs.ipynb
│   ├── 03_function_tools.ipynb
│   ├── 04_conversation_state.ipynb
│   └── 05_capstone_mcp_bridge.ipynb
├── src/harborlight_responses/
│   ├── __init__.py                 # small curated public API
│   ├── settings.py                 # lazy env access; no import-time constants
│   ├── client.py                   # cached lazy OpenAI client; key check
│   ├── model_select.py             # resolve_model(): 2 tiers + env override
│   ├── responses.py                # text, streaming, parse-based structured output
│   ├── tool_loop.py                # the function-tool loop (ported + hardened)
│   ├── tools.py                    # Harborlight tool definitions + registry
│   ├── services.py                 # deterministic renewal logic (mirrors MCP-101)
│   ├── schemas.py                  # Pydantic: RenewalReview, PremiumChange, ...
│   ├── usage.py                    # summarize_usage(response) -> printable line
│   ├── mcp_bridge.py               # capstone adapter (import-guarded)
│   └── data/
│       └── fictional_policies.csv  # mirrored from MCP-101, same contract
└── tests/
    ├── test_services.py
    ├── test_schemas.py
    ├── test_tool_loop.py
    ├── test_responses_helpers.py
    ├── test_data_contract.py       # fictional-data rules (see 3.7)
    └── test_mcp_bridge.py          # stubbed session; skipped without extra
```

Repo rename to `responses-api-101` for symmetry with MCP-101 is optional; GitHub redirects renamed repos, but links in older posts/slides argue for keeping the name and retitling the README instead. Low priority either way.

### 3.2 Package boundaries

Three layers, same discipline as MCP-101's `services.py` / `server.py` split:

1. **Deterministic business layer** (`services.py`, `schemas.py`, `data/`) — no OpenAI import, fully offline-testable. This is deliberately the mirror image of MCP-101's services layer.
2. **API interaction layer** (`client.py`, `responses.py`, `tool_loop.py`, `usage.py`) — everything that touches the OpenAI SDK; testable with fakes.
3. **Surfaces** (`notebooks/`, `app/`, `mcp_bridge.py`) — consume layers 1–2; contain no business logic and no loop plumbing.

The teaching payoff of this boundary: lesson 03 can truthfully say "the tools are ordinary tested Python — the only new thing is how the model asks for them."

### 3.3 Reusable services

Port MCP-101's service semantics exactly: fixed snapshot date `2026-07-01`, inclusive day windows (0–365), integer cents, `Decimal` half-up rounding to two places, sorted deterministic output. Identical inputs must produce identical outputs *across both repos* — that equivalence is the capstone's whole punchline. Add one service the Responses side uniquely needs: `get_policy(policy_id)` returning a single record (feeds lessons 01–02 without teaching filtering).

### 3.4 Schema organization

All Pydantic models in one `schemas.py` (this is a 101, not a domain-driven design exercise): `RenewalReview` (lesson 02), tool-argument models, and a `PremiumChange` result model matching MCP-101's TypedDict field-for-field. Function-tool JSON schemas are *generated* from the Pydantic models where practical rather than hand-written twice — and lesson 03 shows the generated JSON so nothing is hidden.

### 3.5 Tool organization

`tools.py` exposes exactly: `TOOL_DEFINITIONS: list[dict]` (Responses-format) and `TOOL_FUNCTIONS: dict[str, Callable]` (name → services function). Two business tools only — resist the urge to add a calculator, a weather tool, or a third demo tool. The registry pattern from old notebook 04 was right; keep it.

### 3.6 Configuration, models, and keys

- **Config:** `.env` at repo root with `OPENAI_API_KEY` and optional `HARBORLIGHT_MODEL`. `settings.py` reads env *inside functions* — no import-time constants (fixes the `DEFAULT_MODEL` freeze).
- **Model selection:** delete the five-category catalog. Replace with:

  ```python
  TIERS = {"default": "gpt-5.6-luna", "frontier": "gpt-5.6"}
  def resolve_model(tier: str = "default") -> str:
      return os.getenv("HARBORLIGHT_MODEL") or TIERS[tier]
  ```

  Default to the cost-efficient tier for every lesson; the capstone may use `frontier`. A README table (not code) describes the current family and links to the official models page with an explicit "model IDs rotate — this table was verified 2026-07" caveat. The old `list_raw_models()` availability check becomes a single optional diagnostic cell in lesson 01, not package API.
- **Keys:** never in notebooks or code; `.env` + a `check_api_key()` helper that raises one clear, actionable message. Keep the existing gitignore discipline.
- **Optional live services:** exactly one optional dependency group: `pip install -e ".[mcp]"` for the capstone. Everything else works with the base install plus a key. `[dev]` mirrors MCP-101 (ruff, pytest, ipykernel, nbconvert) plus `gradio` — or give the app its own `[app]` extra to keep the teaching install slim (recommended).

### 3.7 Sharing the fictional dataset without coupling the repos

- **Mirror, don't reference.** Copy `fictional_policies.csv` into `src/harborlight_responses/data/`, packaged via `importlib.resources` exactly like MCP-101. No path into a sibling checkout, no git submodule, no network fetch. MCP-101 remains the canonical source; this repo's README says so.
- **Enforce the contract, not the sync.** `test_data_contract.py` re-implements MCP-101's validation rules: `fictional_record == true` on every row, `FIC-` policy-ID prefix, `Fictional ` customer-label prefix, ISO dates, positive integer cents, no duplicate IDs, non-empty. If someone swaps in a divergent or non-fictional file, tests fail loudly. Drift in *values* between repos is tolerable (each repo stays self-consistent and deterministic); drift in *contract* is not.
- **The capstone dependency is optional and versioned:** `[mcp]` extra pins `harborlight-mcp @ git+https://github.com/itprodirect/Model-Context-Protocol-101@<tag-or-sha>` (pin once MCP-101 tags a release; until then, a specific commit SHA). The notebook import-guards it and degrades with a clear install instruction. The core curriculum (lessons 01–04) must never import anything from MCP-101.

### 3.8 CI and the live-call problem

MCP-101's CI can execute its notebook because it is fully offline. This repo's notebooks call a paid API, so:

- **Every live cell goes through one tiny guard** (e.g., `client_or_skip()` from `client.py`): with no `OPENAI_API_KEY`, it prints `⏭ Skipped live call — set OPENAI_API_KEY to run this cell` and the cell completes successfully. This is honest (the skip is visible), teachable (key handling is part of the lesson), and makes `nbconvert --execute` green on keyless CI and forks.
- **CI default job (all pushes/PRs):** ruff → pytest (all offline) → `nbconvert --execute` all five notebooks keyless (structure + offline paths validated).
- **Optional live job (manual `workflow_dispatch`, or on `main` only, never fork PRs):** same nbconvert run with a repo-secret key and the cheapest tier — an on-demand canary that catches model-ID rot and API drift for pennies. Python matrix 3.10/3.13 to match MCP-101.

---

## 4. Visual and user experience

### 4.1 Is Gradio the right choice? Yes — with a version pin.

| Option | Verdict |
|---|---|
| **Gradio Blocks** | **Selected.** Pure Python, one file, one command (`python app/renewal_desk.py`), first-class chat + streaming components, renders JSON/tables natively, familiar to the AI-learner audience. Pin `gradio>=6,<7` (6.20 current) |
| Streamlit | Fine tool, wrong fit: whole-script rerun model makes a stepwise tool-loop activity log awkward; heavier mental model for this audience |
| Jupyter widgets | Keeps everything in notebooks but produces no standalone demo surface, poor screenshot/story value |
| FastAPI + HTML/JS | Becomes a frontend project — explicitly out of scope per the constraints |

### 4.2 The demo: "Harborlight Renewal Desk" — one screen

**Layout (two columns):**

- **Left — the conversation.** Chat panel seeded with three example prompts (the lesson questions). Learner controls: scenario dropdown (three canned prompts + free text), model tier (default / frontier), and a **Mode** switch: `Demo (offline)` / `Live API`.
- **Right — the activity panel** (the app's entire reason to exist; this is transparency-as-UI):
  1. **Tool activity** — each `function_call` as it happens: tool name, arguments JSON, and the deterministic result JSON, visually distinct from model text.
  2. **Request/response inspector** (accordion, collapsed) — the outgoing request params and raw response items for the last turn.
  3. **Usage bar** — input/output tokens for the turn and cumulative session total, with a link-out to OpenAI's pricing page (no hardcoded dollar figures in code — they rot).

**Demo vs Live must be unmistakable:**

- Live mode: green banner `LIVE — real API calls, uses your OPENAI_API_KEY, costs tokens`.
- Demo mode: amber banner `DEMO — replaying a recorded transcript from 2026-07; no API calls, no key needed`. Demo mode replays one *recorded real transcript* (checked in as JSON, clearly dated) for the flagship scenario — the tool calls still execute live against the deterministic services (they're free and local); only the model turns are canned. Free-text input is disabled in demo mode with a tooltip explaining why — the app must never generate fake "model output" for arbitrary input.

### 4.3 README visuals

1. **Hero screenshot** of the Renewal Desk mid-tool-loop (activity panel visible) — `docs/assets/`, exactly like MCP-101's Inspector screenshot.
2. **One Mermaid architecture diagram**: notebook/app → `harborlight_responses` package → OpenAI Responses API, with the deterministic services + CSV boxed separately, and a dotted line to the MCP-101 server labeled "capstone only."
3. **One Mermaid sequence diagram** of the tool loop (request → `function_call` → local execution → `function_call_output` → final response) — the Responses-side sibling of MCP-101's protocol sequence diagram.
4. CI badge; a small "fictional data" banner note near the top.

That is the entire visual identity: consistent Harborlight naming, two diagrams, one screenshot, one badge. No logo project, no custom CSS beyond Gradio defaults, no themed color system. "Attractive" here means *legible and current*, and the fastest path to that is diagrams that match the code.

---

## 5. Transparency and educational safety

Principles, each with its concrete mechanism:

| What must be clear | Mechanism |
|---|---|
| **Fictional vs real** | Adopt MCP-101's contract wholesale: `fictional_record` column, `FIC-` IDs, `Fictional ` name prefixes, contract test, scope-and-disclaimer README section, fictional-notice line in every notebook header and the app footer. Never use real company or person names in any example — including in prompts |
| **Deterministic vs live** | Every notebook cell that calls the API is labeled `LIVE` in its preceding markdown; deterministic service cells labeled accordingly. "Expected output" markdown blocks accompany live cells so offline readers know what success looks like without pretending outputs are exact |
| **Model output vs tool output** | The tool-activity table in notebooks and the activity panel in the app render tool results as JSON *before* the model's narration appears; lesson 03's text explicitly says "the numbers come from your Python; the prose comes from the model" |
| **Retrieved evidence vs generated interpretation** | Core v1 lessons have no retrieval; the principle is taught in lesson 03 as tool-result-vs-narration. When file search lands in v2, render the response's citation annotations and the retrieved chunks above the model's prose |
| **Local vs hosted tools** | A README table: function tools (your machine runs them, you see everything) vs hosted tools (OpenAI runs them server-side, you see results and metadata). Lesson 03 teaches the local side; hosted tools are explicitly deferred with this framing |
| **Responses function tools vs MCP tools** | The capstone's side-by-side: same business capability, invoked by model-driven function calling vs application-driven MCP protocol; the README architecture diagram draws the boundary |
| **API usage and cost** | `summarize_usage(response)` printed after *every* live call in every notebook; cumulative session counter in the app; README "What this costs to run" section: expected order of magnitude per notebook run on the default tier, link to live pricing, explicit note that chained conversation turns re-bill prior input tokens |
| **Failure modes and limitations** | Each lesson ends with a short "When this goes wrong" block: lesson 01 — key/quota/model-not-found errors; lesson 02 — refusals and schema-shape-vs-truth; lesson 03 — unknown tool, tool exceptions, runaway loops (`max_rounds`); lesson 04 — retention limits and cost growth; lesson 05 — stdio pollution, missing extra. A README limitations section mirrors MCP-101's ("educational example, not production software or insurance advice") |

**On reasoning transparency specifically (replacing old notebook 02's pattern):** never present prompted "Reasoning:" narratives as the model's reasoning, and do not attempt to expose hidden chain-of-thought. The honest alternatives this repo teaches instead:

1. **Tool activity** — what the model actually *did* (calls, arguments, results) is inspectable ground truth.
2. **Structured decision summaries** — a schema field like `decision_summary` (one sentence, lesson 02) gives an auditable, validated rationale *as output*, clearly framed as "the model's stated justification, not a log of its internal process."
3. **Request/response inspection** — raw items, IDs, and usage teach what the API actually exchanges.
4. If reasoning-summary API features are used later, use only the official API surface for them and label them as API-provided summaries — never scrape or simulate internal reasoning.

---

## 6. Scope control

### 6.1 Must-have for version one

1. `pyproject.toml` + `src/harborlight_responses` package; zero `sys.path` hacks anywhere.
2. Mirrored fictional dataset + deterministic services + contract test.
3. Five-lesson curriculum (01–04 core + capstone 05), all executing top-to-bottom, keyless-safe via the skip guard.
4. Current API patterns throughout: GPT-5.6-family tiers via `resolve_model()`, `responses.parse` for structured output, `web_search`-era tool naming (in prose), Conversations API in lesson 04.
5. Ruff + pytest + CI (lint, offline tests, keyless notebook execution) + optional live canary job.
6. Rebuilt README: badges, two diagrams, screenshot, fictional-data and cost sections, tested Windows PowerShell + macOS/Linux quickstarts (this is a Windows-first author — the PowerShell path must be first-class, as MCP-101 already does).
7. Gradio Renewal Desk app (one file, one screen, demo/live modes, activity panel).
8. Archive of pre-Harborlight notebooks; removal of the transcript file and scratch notebook; output-stripped notebook policy.

### 6.2 Useful for version two

- Lesson 06: file search + citations over a small fictional Harborlight document set (with vector-store setup *and teardown* shown).
- Web-search appendix (clearly non-deterministic, off-narrative framing).
- Hosted `mcp` tool-type exploration if/when a hosted Harborlight MCP endpoint exists.
- Streaming output mode in the app; short demo GIF in the README.
- `CONTRIBUTING.md`; a tagged release + matching MCP-101 tag so the two repos reference each other at stable versions.
- Structured-output failure-handling mini-lesson (retry-on-validation-error patterns).

### 6.3 Explicitly rejected or postponed (attractive but counterproductive)

1. **Seven-plus-notebook curriculum** — rejected. Breadth dilutes the story; every capability the repo promises fits in five lessons. More notebooks = more CI surface = more rot (this repo's history is the proof).
2. **Full offline mock-model mode for notebooks** — rejected. Faking model outputs teaches beginners that model behavior is deterministic and that demos are evidence. Offline mode is for *services* and for one clearly labeled recorded transcript in the app; notebooks skip live cells honestly instead of faking them.
3. **A maintained model catalog with live availability validation** — rejected (delete, don't port). Hand-curated catalogs are stale by construction — this repo's catalog contains a model that never existed and one with a scheduled shutdown, after only ~8 months. Two tiers + env override + a dated README table is the whole need.
4. **Multi-provider abstraction layer** ("also works with Anthropic/Gemini") — rejected. It's a different repo's mission and would bury the Responses API specifics this repo exists to teach.
5. **Native remote MCP in v1** — postponed. It requires a hosted, reachable MCP server, auth decisions, and approval flows; as a first MCP contact it also blurs the local-bridge lesson. One documented paragraph in the capstone, code in v2+ at the earliest.
6. **Production hardening theater** (retry/backoff frameworks, structured logging, Docker, deployment guides) — rejected for v1 beyond `max_rounds` and honest error messages. Educational repos that cosplay as production systems teach neither well.
7. **Committed live notebook outputs** — rejected as policy (see §8, row 10).

---

## 7. Implementation sequencing

Each PR is independently mergeable and keeps `main` green. Sizes are deliberately small — this is also a chance to model good PR hygiene in a public teaching repo.

| # | PR | Objective | Files/areas | Tests required | Acceptance criteria | Depends on |
|---|---|---|---|---|---|---|
| 1 | `chore/repo-hygiene` | Remove dead weight; set archive convention | Delete transcript `.txt` + `test_openai_connection.ipynb`; create `archive/` + note; move review docs to `docs/history/`; add `.gitattributes`; pull `origin/main` first | Existing unittest suite still passes | Repo root contains only purposeful files; archived notebooks labeled non-runnable | — |
| 2 | `feat/packaging` | Kill `sys.path` hacks at the root | `pyproject.toml` (deps: `openai>=2.45,<3`, `pydantic>=2,<3`, `python-dotenv`, `pandas`; extras `[dev]`, `[app]`, `[mcp]`); move `utils/` → `src/harborlight_responses/` (mechanical port + renames); convert tests to pytest; ruff config | Ported pytest suite green; `ruff check .` clean | `pip install -e ".[dev]"` from fresh venv on Windows + Linux; `import harborlight_responses` works from any cwd; old notebooks still in `archive/` untouched | 1 |
| 3 | `ci/actions` | Make green visible | `.github/workflows/ci.yml` (3.10/3.13 matrix: ruff → pytest); README badge | CI itself | Badge green on `main`; fork PRs run without secrets | 2 |
| 4 | `feat/harborlight-data-services` | The shared universe, enforced | `data/fictional_policies.csv` (mirrored), `services.py`, `schemas.py`, `test_services.py`, `test_schemas.py`, `test_data_contract.py` | Contract test + service determinism tests (30-day window → 1001/1002/1003; premium math matches MCP-101 exactly) | Services importable offline; identical results to MCP-101 for identical inputs | 2 |
| 5 | `feat/api-helpers-modernization` | Current API surface, correct helpers | `model_select.py` (delete old catalog), `responses.py` (add `parse_structured` via `responses.parse`; remove `modalities`; verify streaming against SDK 2.x), `tool_loop.py` (unknown-tool → structured error output), `usage.py`, `client.py` (`client_or_skip` guard), `settings.py` | Port + extend fake-client tests; unknown-tool and refusal-path tests; usage-summary test | No deprecated/nonexistent model IDs anywhere in the tree; all helpers offline-tested | 2, 4 |
| 6 | `feat/curriculum` | The five lessons | `notebooks/01–05` (05 may stub pending PR 8), notebook-output stripping policy, CI gains keyless `nbconvert --execute` for all notebooks + `workflow_dispatch` live job | CI notebook execution keyless; manual live run once before merge | Every notebook: top-to-bottom keyless execution green; fictional notice + cost line present; no `sys.path` cells | 3, 4, 5 |
| 7 | `feat/renewal-desk-app` | The visual centerpiece | `app/renewal_desk.py`, recorded demo transcript JSON, `docs/assets/` screenshot | Smoke test: app module imports and builds the Blocks graph without a key (no server launch in CI) | `python app/renewal_desk.py` works keyless in demo mode and live with a key; screenshot committed | 5 |
| 8 | `feat/mcp-capstone` | Where the two repos meet | `mcp_bridge.py`, `[mcp]` extra pinned to an MCP-101 tag/SHA, finalize notebook 05, `test_mcp_bridge.py` | Stubbed-session tests for schema translation + call routing; skip-marked when extra absent | Capstone runs end-to-end with the extra installed; degrades to clear instructions without it; core lessons still import nothing from MCP-101 | 5, 6 |
| 9 | `docs/readme-rebuild` | The front door | README (quickstarts, diagrams, screenshot, fictional/cost/limitations sections, model table dated 2026-07), archive note polish | Quickstart executed verbatim on Windows PowerShell + one POSIX shell | A newcomer reaches "first successful API call" from README alone; structure block matches the tree | 6, 7, 8 |

---

## 8. Critical comparison of the baseline proposal

| Proposed idea | Keep / change / reject | Reason | Recommended implementation |
|---|---|---|---|
| Harborlight shared narrative | **Keep** | One coherent fictional universe fixes the repo's current three-universe drift; the shared services make the MCP/Responses distinction self-demonstrating | Mirror dataset + contract test (§3.7); same snapshot date `2026-07-01`; same fictional-labeling rules |
| Seven-notebook curriculum | **Change → five** | Every promised capability fits in 4 core + 1 capstone; each extra notebook is permanent CI + rot surface; file search and web search don't earn v1 seats | Curriculum in §2.2; file search is v2 lesson 06; web search at most a v2 appendix |
| Gradio application | **Keep (minimal)** | Right tool (§4.1); the activity panel is the transparency story made visible; one file keeps it from becoming a frontend project | `app/renewal_desk.py`, Gradio Blocks pinned `>=6,<7`, one screen, demo/live modes |
| Model catalog | **Reject (replace)** | Current catalog contains a nonexistent model (`gpt-4.1-mini-transcribe`) and a scheduled-shutdown model (`o4-mini`) — proof that hand-curated catalogs rot fast in an edu repo | Two-tier `resolve_model()` + `HARBORLIGHT_MODEL` override + dated README table linking to official models page |
| File search | **Change → v2** | On-narrative and valuable, but vector-store setup/teardown is a lesson of infrastructure that would bloat v1 | v2 lesson 06 with citations rendered as evidence-vs-interpretation teaching |
| Web search | **Change → postpone (v2 appendix at most)** | Non-deterministic, off-narrative for a fixed-snapshot scenario; old notebook 02's stale committed concert listings are the cautionary tale | Short v2 appendix framed "when you genuinely need the live web"; never a core lesson |
| Conversation state | **Keep (expand)** | Core Responses capability; the docs now recommend the Conversations API, which the current repo doesn't touch | Lesson 04: manual array → `previous_response_id` → Conversations API, with retention + billing made visible |
| Local MCP adapter (capstone) | **Keep** | The single best bridge between the two repos: same tools, two invocation models | `mcp_bridge.py` + `[mcp]` extra pinned to MCP-101 tag/SHA; import-guarded; stubbed-session tests (§2.2 lesson 05) |
| Native remote MCP | **Change → documented future work** | Needs a hosted server, auth, and approval-flow decisions; premature as a first MCP contact | One paragraph + config sketch in capstone prose; revisit when a hosted Harborlight endpoint exists |
| Committed notebook outputs | **Reject** | The repo demonstrates the failure mode today: stale Nov-2025 live results and out-of-order execution counts rendered on GitHub | Strip outputs (pre-commit or convention) + "expected output" markdown blocks + CI execution as the proof-it-runs; consistent with MCP-101 |
| Raw HTTP request example | **Keep (relocated)** | Genuinely good transparency device — shows the API is just HTTP; wrong as the *primary* path for lesson 01 | Single labeled "Under the hood (optional)" appendix cell in lesson 01 |
| Demo mode without an API key | **Change (narrow)** | Keyless *service* demos are honest (they're deterministic and local); keyless *model* output is only honest as a labeled recording | Notebooks: skip-guard pattern (§3.8). App: recorded, dated transcript for one scenario; free-text disabled in demo mode; live tools still run locally |

---

## Final recommendation

### 1. What this repository should become

**"Responses API 101: Harborlight Insurance Agency"** — the model-interaction sibling of MCP-101. A small installed Python package, five executable lessons, and one single-screen demo app that together teach how a model generates responses, produces validated structured data, drives real function tools, and carries workflow state — over the same fictional, deterministic insurance dataset that MCP-101 exposes over protocol. MCP-101 teaches how applications reach capabilities; this repo teaches how models use them; the capstone joins the two. Every model action is inspectable (tool activity, raw request/response, usage), every record is visibly fictional, and every notebook runs top-to-bottom in CI.

### 2. Recommended version-one scope

The eight must-haves of §6.1, delivered as the nine PRs of §7: packaging + `src/` layout, mirrored dataset with contract test, five lessons on current API patterns (GPT-5.6 tiers, `responses.parse`, tool loop, Conversations API, MCP bridge capstone), Ruff/pytest/CI with keyless notebook execution plus an on-demand live canary, the Renewal Desk Gradio app, and a rebuilt README with two diagrams and one screenshot. Nothing else.

### 3. Recommended future roadmap

- **v1.1:** file-search lesson (06) with citations over fictional Harborlight documents; streaming in the app; demo GIF.
- **v1.2:** web-search appendix; structured-output failure-handling patterns; `CONTRIBUTING.md`; tagged releases cross-referencing an MCP-101 tag.
- **v2:** hosted `mcp` tool type against a genuinely hosted Harborlight MCP endpoint (only if one is stood up); possible third repo or module bridging toward agentic workflows if the teaching demand exists.

### 4. Five biggest implementation risks

1. **Model-ID churn.** `gpt-5.6-*` is current in July 2026 and will not stay current (the docs already reference a 5.4-mini replacement cycle; 5.1 was retired within months). *Mitigation:* single `resolve_model()` chokepoint, env override, dated README table, live canary CI job.
2. **CI vs live-API economics and secrets.** Fork PRs can't see secrets; live notebook runs cost money and flake. *Mitigation:* keyless skip-guard as the default CI path; live execution only manual/main-branch with the cheapest tier.
3. **Cross-repo data drift.** The Harborlight CSVs will diverge silently (the stale local MCP-101 clone shows how easily). *Mitigation:* contract test enforcing the fictional-data rules; documented canonical source; capstone dependency pinned to a tag/SHA, never a sibling path.
4. **SDK 2.x surface mismatches.** Helpers were written against 1.x; streaming and parse helpers need verification against `openai>=2.45,<3` (e.g., `stream()` helper vs `create(stream=True)` events). *Mitigation:* PR 5 does the port with the existing fake-based tests extended before any notebook depends on it.
5. **Scope creep toward app polish and extra notebooks.** The activity panel invites feature growth; the archive invites resurrection. *Mitigation:* the definition of done below, the §6.3 rejection list in-repo, and one-screen/five-lesson limits stated in the README itself.

### 5. Proposed definition of done (v1)

- Fresh clone → `pip install -e ".[dev]"` → quickstart works, verified on Windows PowerShell and macOS/Linux bash, following the README verbatim.
- `ruff check .`, `pytest`, and keyless `nbconvert --execute` of all five notebooks pass locally and in CI (3.10 and 3.13); CI badge green.
- With a key: all five notebooks execute live end-to-end; each live cell prints a usage summary; total curriculum run costs a visibly small amount on the default tier.
- `python app/renewal_desk.py` launches keyless into labeled demo mode and works live with a key; screenshot in README matches the shipped app.
- No `sys.path` manipulation, no deprecated or nonexistent model IDs, no committed notebook outputs, no third-party transcript content anywhere in the tree.
- Every dataset row and every rendered example is visibly fictional (contract test green); README carries the fictional-data, cost, and limitations sections.
- Capstone runs with `[mcp]` extra installed and degrades with clear instructions without it; lessons 01–04 have zero MCP imports.

### 6. Ten most valuable changes, ranked

1. **Package the code** (`pyproject.toml` + `src/harborlight_responses`, editable install) — eliminates the `sys.path`/cwd failure mode that breaks beginners first.
2. **Delete the stale model catalog; add the two-tier resolver with env override** — removes the repo's outright factual errors (nonexistent model, scheduled-shutdown model).
3. **Adopt the Harborlight dataset + deterministic services mirrored from MCP-101, with the fictional-data contract test** — one universe, deterministic tools, enforced safety.
4. **Rebuild the curriculum as five lessons with one story** — replaces three disconnected fictional universes and two broken notebooks with a coherent path.
5. **Add CI: ruff + pytest + keyless notebook execution + optional live canary** — the two currently-broken notebooks shipped precisely because nothing executed them.
6. **Modernize structured outputs to `responses.parse` + Pydantic** (keeping one manual-schema cell for transparency) — the current documented pattern.
7. **Replace the prompted "Reasoning:" pseudo-chain-of-thought with tool-activity inspection + structured `decision_summary` fields** — the transparency fix with the biggest pedagogical stakes.
8. **Finish the tool loop in the teaching material** (old notebook 02 stops at `function_call` and computes results locally) — and teach that exact bug by name in lesson 03.
9. **Print usage after every live call and add the cost section** — makes API economics a first-class lesson rather than a surprise.
10. **Ship the Renewal Desk app with the activity panel and honest demo/live modes** — the visual centerpiece that makes model-vs-tool activity visible without exposing anything hidden.

---

*This file is the only file created by this review. No other files in this repository, and nothing in Model-Context-Protocol-101, were modified.*
