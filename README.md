# Responses API 101: Harborlight Insurance Agency

[![CI](https://github.com/itprodirect/OpenAI-responses-api-hub/actions/workflows/ci.yml/badge.svg)](https://github.com/itprodirect/OpenAI-responses-api-hub/actions/workflows/ci.yml)

Learn model requests, typed structured outputs, correct function-tool execution, state, hosted evidence, and orchestration through one visibly fictional insurance-renewal story.

This is a focused public tutorial and development lab: five executable lessons, a small deterministic Python package, a two-workflow Renewal Desk, and an optional local MCP adapter.

## What the Responses API is

The Responses API is OpenAI's recommended API surface for direct model requests and tool-using, multi-turn workflows. A response can contain generated messages, function calls, hosted-tool calls, and other typed output items. The Python SDK exposes output_text for ordinary text and native Pydantic parsing for schema-controlled results.

It is not a general chatbot framework, an insurance system, a database, an authentication layer, or a way to expose hidden chain-of-thought. This project shows observable requests, validated tool arguments, deterministic results, retrieved evidence, generated answers, usage, latency, and concise rationale.

## The fictional Harborlight scenario

Harborlight Insurance Agency and every policy/customer in this repository are fictional. The package contains six synthetic policies at a fixed data snapshot of 2026-07-01. An account manager needs to review upcoming renewals, calculate proposed premium changes, compare customers, and prepare evidence-backed communications.

The same Harborlight dataset and two read-only business capabilities appear in [Model Context Protocol 101](https://github.com/itprodirect/Model-Context-Protocol-101). That deliberate overlap makes the technology boundary concrete:

| Question | Responses API 101 | MCP 101 |
|---|---|---|
| Primary lesson | How a model receives input, returns typed output, calls tools, uses state, and retrieves evidence | How a client discovers and invokes server capabilities across a protocol |
| Who selects a tool? | The model, from function definitions supplied in a request | The host/client, after protocol discovery |
| Where is the business logic? | Local deterministic Python services | The MCP server's deterministic Python services |
| How does a result return? | Python sends function_call_output back to Responses | The MCP server returns a protocol tool result |
| Is a model required? | Live lessons use one; demo fixtures do not | No |
| Runtime dependency between repos | None | None |

## Architecture

~~~mermaid
flowchart LR
    Learner["Learner"] --> Lessons["Five notebooks"]
    Learner --> Desk["Harborlight Renewal Desk"]
    Lessons --> Core["harborlight_responses package"]
    Desk --> Core
    Core --> Data["Packaged fictional CSV"]
    Core --> Services["Deterministic services"]
    Core --> API["OpenAI Responses API (live mode only)"]
    API --> Hosted["Hosted web search"]
    Bridge["Optional adapter example"] --> Core
    Bridge --> LocalMCP["Configured local stdio MCP server"]
~~~

## The correct function-tool round trip

~~~mermaid
sequenceDiagram
    participant U as Learner request
    participant R as Responses API model
    participant P as Local Python tool loop
    participant S as Harborlight service
    U->>R: instructions + input + strict tools
    R-->>P: function_call(name, arguments, call_id)
    P->>P: JSON decode + Pydantic validation
    P->>S: execute deterministic function
    S-->>P: structured result
    P->>R: function_call_output(call_id, result)
    R-->>U: final generated answer
~~~

Running the Python function is not enough. Until Python returns function_call_output with the matching call_id, the model has requested work but has not received its result.

## Tested quickstart

**Live validation status (2026-07-14, America/New_York): PASS.** All eight required live capabilities have a confirmed successful path. Lesson 1 used `gpt-5.6-terra`; the typed-output, tool, state, hosted-search, and Renewal Desk checks used `gpt-5.6-luna`. Two initial typed-schema calls returned sanitized HTTP 400 `invalid_json_schema`; after the schema was narrowed to the supported strict subset, the live Renewal Desk structured workflow completed through the same `responses.parse` helper used by Lesson 2. One separate corrective Lesson 2 result was not captured because the local validation harness failed after the request, so that request was not repeated. No raw output, secret, response ID, or conversation ID was committed. See [release validation](docs/VALIDATION.md).

Python 3.10 or newer is required. CI covers Python 3.10 and 3.13. Local release validation used Python 3.12, OpenAI Python SDK 2.45.0, Gradio 6.20.0, and MCP Python SDK 1.28.1.

### Windows PowerShell

~~~powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m ruff check .
python -m pytest
~~~

If py -3.12 is unavailable but python --version reports 3.10 or newer, use python -m venv .venv.

### macOS or Linux

~~~bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m ruff check .
python -m pytest
~~~

Core imports do not require Gradio, Jupyter, pandas, or MCP. Install smaller capability sets with .[notebooks], .[app], or .[mcp] when desired.

## Demo mode: no API key

Demo mode is the default for every notebook and for the application. It performs no OpenAI request and labels model-facing material:

> Authored demonstration fixture - no live OpenAI API call was made.

Demo mode still loads and validates the packaged CSV, filters renewal windows, and calculates premium changes through the real deterministic services.

Run the app:

~~~powershell
python app/harborlight_renewal_desk.py
~~~

On macOS/Linux, use python app/harborlight_renewal_desk.py.

## Live API mode

Live mode may incur model and hosted-tool charges. Set OPENAI_API_KEY in your environment; never commit it. Notebooks require an additional explicit opt-in so a present key does not trigger accidental calls.

~~~powershell
$env:OPENAI_API_KEY = "<your key>"
$env:HARBORLIGHT_LIVE = "1"
jupyter lab
~~~

In the Renewal Desk, choose Live API. If the key is missing or the configured model fails, the app reports the error and does not silently switch to a fixture.

### Model selection

The repository intentionally has no model catalog and makes no model-list request during startup.

| Configuration | Model |
|---|---|
| Default / OPENAI_MODEL_TIER=balanced | gpt-5.6-terra |
| OPENAI_MODEL_TIER=economy | gpt-5.6-luna |
| OPENAI_DEFAULT_MODEL set | Exact explicit value, with no fallback |

Advanced users can set OPENAI_DEFAULT_MODEL=gpt-5.6-sol. Model selection is visible in notebooks and the app.

## Five-lesson curriculum

| Lesson | Harborlight task | API concept | Offline behavior |
|---|---|---|---|
| [01 First Harborlight Response](notebooks/01_first_harborlight_response.ipynb) | Explain Fictional Beacon Books | OpenAI(), responses.create, instructions, input, output_text, metadata, usage | Authored prose fixture plus deterministic record |
| [02 Typed Renewal Review](notebooks/02_structured_renewal_review.ipynb) | Convert a messy renewal note | Pydantic, responses.parse, output_parsed, refusal/missing handling | Typed fixture; arithmetic rechecked |
| [03 Function Tools](notebooks/03_function_tools.ipynb) | Find renewals and calculate a change | Strict schemas, multiple calls, local execution, function_call_output, bounded loop | Fake model boundary; real deterministic services |
| [04 Conversation State](notebooks/04_conversation_state.ipynb) | Compare Beacon and Cedar, revise steps | previous_response_id and Conversations API | Explicit state fixture; no remote identifiers |
| [05 Web Search and Evidence](notebooks/05_web_search_and_evidence.ipynb) | Build a hurricane-preparedness checklist | Hosted web_search, dated evidence, citations, interpretation | Dated authored evidence fixture from 2026-07-14 |

Execute all five without a key:

~~~powershell
$env:OPENAI_API_KEY = $null
$env:HARBORLIGHT_LIVE = $null
Get-ChildItem notebooks/*.ipynb | ForEach-Object {
    python -m nbconvert --to notebook --execute $_.FullName --output $_.Name --output-dir .notebook-output --ExecutePreprocessor.timeout=120
}
~~~

## Harborlight Renewal Desk

The Gradio Blocks app is intentionally not a chatbot. It has two actions:

1. Structured renewal review.
2. Tool-assisted upcoming-renewal analysis.

The interface shows the fictional-data/mode notices, request input, selected model, requested tools, validated arguments, deterministic output, structured result, retrieved evidence when applicable, final answer, usage, latency, and recovery guidance. Importing the module does not create a client or launch a server.

## Deterministic, generated, retrieved, and fixture output

| Output class | Source | Reliability boundary |
|---|---|---|
| Deterministic | Packaged CSV and pure Python services | Validated contracts; repeatable for the fixed snapshot |
| Generated | OpenAI model | Wording and judgment may vary; validate important facts |
| Retrieved | Hosted web search | Live and nondeterministic; inspect execution date, citations, and source quality |
| Authored fixture | Checked-in demonstration data | Historical example only; never label it current or live |

No interface or notebook claims to reveal hidden reasoning. Concise generated rationale is ordinary output, not chain-of-thought.

## Data contracts

The mirrored CSV is independently packaged at src/harborlight_responses/data/fictional_policies.csv. SOURCE.json records the exact MCP source repository, path, commit, and mirror date. Runtime never reads the MCP repository.

Loading rejects missing fields, duplicate policy IDs, records without fictional_record=true, policy IDs without FIC-, customer labels without Fictional, invalid ISO dates, non-integer money, and non-positive premiums. Currency uses integer cents. Percentage changes use Decimal arithmetic and round half-up to two places.

The two deterministic capabilities are read-only:

- list_upcoming_renewals(days), where days is an integer from 0 through 365 and the end date is inclusive.
- calculate_premium_change(current_cents, renewal_cents), where both values are positive integer cents.

No caller can provide a dataset path.

## Optional advanced local MCP adapter

[examples/responses_to_mcp_bridge.py](examples/responses_to_mcp_bridge.py) demonstrates an adapter pattern:

1. Responses sees ordinary function tools.
2. The model requests a function call.
3. Local Python invokes a trusted configured stdio MCP server.
4. MCP structured content returns to Python.
5. Python sends function_call_output to Responses.
6. The model writes the final answer.

This is not native remote Responses MCP, and Responses function tools are not MCP tools. The example uses argument lists and the MCP SDK; it never uses shell=True. It defaults to the active Python executable and module harborlight_mcp, validates both, and exits with guidance if that optional server is unavailable.

Install a compatible Harborlight MCP server package into a chosen environment, then point the adapter to that trusted interpreter:

~~~powershell
python examples/responses_to_mcp_bridge.py --python-executable ".venv/Scripts/python.exe" --module harborlight_mcp
~~~

The Responses API's native MCP tool is a different path: it expects a remote server_url using Streamable HTTP or HTTP/SSE. Native remote MCP is version-two work for this repository.

## API usage, cost, and storage

Demo mode has no OpenAI API cost. Live text, structured output, function-tool continuation, state, and hosted web search can incur model or tool charges. Review current pricing before enabling live mode.

Response objects are stored for 30 days by default unless store=False. Items attached to Conversations are durable beyond that response TTL. Chained requests using previous_response_id still bill earlier input tokens each turn. Never commit response IDs, conversation IDs, keys, or live customer data.

## Troubleshooting

### Live mode says OPENAI_API_KEY is missing

Set the variable in the same shell that launches Jupyter or Gradio. Demo mode remains available without it.

### An explicit model fails

Check OPENAI_DEFAULT_MODEL against the current official models page and project access. The resolver deliberately does not hide the failure behind a fallback.

### A notebook imports the wrong environment

Activate the environment where this project was installed and select that environment's Python kernel. A stale Jupyter kernelspec may point to a deleted virtual environment.

### The app will not import

Install the app extra with python -m pip install -e ".[app]", or use .[dev] for the complete lab.

### The MCP adapter cannot start

Install a compatible server package into the configured Python environment. Confirm the interpreter is an existing absolute python/python3 executable and the module is a trusted dotted module name. The core tutorial does not require MCP.

### Web search has no useful sources

Treat the result as insufficient evidence. Do not infer current guidance from model confidence or relabel the dated fixture as current.

## Scope and disclaimer

This is educational code, not production software or insurance advice. It has no authentication, accounts, database, telemetry platform, production frontend, underwriting, eligibility, claims, quoting, carrier integration, or autonomous business action. Harborlight and all records are fictional.

Version one deliberately excludes file search, vector stores, native remote MCP, production deployment, and a general chatbot.

## Official OpenAI references

- [Model guidance: GPT-5.6](https://developers.openai.com/api/docs/guides/latest-model)
- [Text generation and output_text](https://developers.openai.com/api/docs/guides/text)
- [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs)
- [Function calling](https://developers.openai.com/api/docs/guides/function-calling)
- [Conversation state](https://developers.openai.com/api/docs/guides/conversation-state)
- [Web search](https://developers.openai.com/api/docs/guides/tools-web-search)
- [MCP and Connectors](https://developers.openai.com/api/docs/guides/tools-connectors-mcp)
- [Streaming Responses](https://developers.openai.com/api/docs/guides/streaming-responses)
- [OpenAI Python SDK](https://github.com/openai/openai-python)

## Version-two roadmap

- File search with a small, auditable fictional knowledge base.
- Native remote Responses MCP over a supported HTTP transport.
- An optional streaming-focused lesson after it can fit without expanding the five-lesson core.
- Screenshot documentation only after a stable, identifier-free capture workflow exists.

## License

MIT. See [LICENSE](LICENSE).
