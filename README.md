# OpenAI Responses API Hub

A small, reusable learning repo for the OpenAI Responses API. The project is organized as a notebook curriculum backed by a shared `utils/` package so examples stay consistent as the repo grows.

The current focus is practical usage:

- basic text generation
- hosted tools like `web_search`
- custom tool loops
- reusable client and response helpers

## Purpose

This repo is meant to serve two jobs at once:

1. a personal lab for learning the Responses API cleanly
2. a teaching-ready set of examples you can reuse in training, demos, and consulting work

## Project Structure

```text
openai-responses-api-hub/
|-- notebooks/
|   |-- 01_basic_chatbot.ipynb
|   |-- 02_tools_and_reasoning.ipynb
|   |-- 03_structured_outputs.ipynb
|   `-- test_openai_connection.ipynb
|-- utils/
|   |-- openai_client.py
|   |-- responses_api.py
|   |-- models.py
|   |-- config.py
|   `-- __init__.py
|-- tests/
|   |-- test_models.py
|   |-- test_openai_client.py
|   `-- test_responses_api.py
|-- docs/
|   `-- UPGRADE_REVIEW.md
|-- requirements.txt
`-- README.md
```

## Utilities

`utils/openai_client.py`

- loads `.env`
- exposes `get_openai_client()` for the shared cached client
- exposes `build_openai_client()` for explicit-key or test scenarios
- exposes `get_response()` as a simple compatibility helper

`utils/responses_api.py`

- `create_text_response(...)`
- `create_streaming_text_response(...)`
- `create_json_response(...)`
- `extract_output_text(...)`
- `stream_text_deltas(...)`

`utils/models.py`

- curated model catalog in `RECOMMENDED_MODELS`
- `choose_default_model(preference)` for stable local defaults
- `list_recommended_models(validate_availability=True)` when you want to reconcile the catalog against the live API

`utils/config.py`

- resolves `DEFAULT_MODEL`
- respects `OPENAI_DEFAULT_MODEL`
- falls back safely for offline notebook editing

## Notebook Status

`01_basic_chatbot.ipynb`

- environment setup
- first Responses API call
- raw JSON inspection
- simple model selection

`02_tools_and_reasoning.ipynb`

- hosted `web_search`
- reasoning plus final answer separation
- optional custom calculator tool example
- tool-call inspection

`03_structured_outputs.ipynb`

- strict JSON schema extraction
- reusable `create_json_response(...)` workflow
- pandas-friendly action-item tables
- second example for support-ticket triage

## Roadmap

The highest-value next notebooks are:

1. Richer multi-tool workflows with tool execution loops
2. File search and a small RAG example
3. A lightweight model explorer or small app surface for demos

## Local Setup

Create a `.env` file at the repo root:

```bash
OPENAI_API_KEY=your-key-here
OPENAI_DEFAULT_MODEL=gpt-4.1-mini
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run tests:

```bash
python -m unittest discover -s tests -v
```

Run notebooks:

```bash
jupyter notebook notebooks/01_basic_chatbot.ipynb
jupyter notebook notebooks/03_structured_outputs.ipynb
```

## Example

```python
from utils import DEFAULT_MODEL, create_text_response

response_text = create_text_response(
    "Explain the OpenAI Responses API in 2 sentences.",
    model=DEFAULT_MODEL,
)

print(response_text)
```

## Notes

The curated model list is maintained by hand. If you want to compare it against the models visible to your API key, call:

```python
from utils.models import list_recommended_models

models = list_recommended_models(validate_availability=True)
```

## License

MIT
