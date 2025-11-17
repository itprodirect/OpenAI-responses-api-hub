# 🧠 OpenAI Responses API Hub

A hands-on, methodical hub for learning and mastering the **OpenAI Responses API** using clean, reusable patterns, curated model helpers, and step-by-step Jupyter notebooks.

This repo intentionally evolves one notebook at a time. Each notebook builds on a consistent structure and introduces a new capability — from basic chat to streaming, structured outputs, tools, and eventually full RAG pipelines.

---

# 🚀 Repo Purpose

Nick — this repo exists to give you (and anyone learning from your work) a **repeatable, professional-grade template** for:

* Understanding how to use the OpenAI Responses API properly
* Comparing model categories (fast / quality / reasoning / vision)
* Using a shared utilities package across notebooks
* Demonstrating real-world patterns you can use in consulting and training
* Building RAG, tools, and multimodal workflows one small step at a time

Every notebook follows the same setup pattern, so this repo doubles as both:

1. **A personal learning platform**, and
2. **A teaching-ready curriculum** you can use for your AI training services.

---

# 📁 Project Structure

```
openai-responses-api-hub/
│
├── notebooks/                # Jupyter notebooks for each lesson/module
│   ├── 01_basic_chatbot.ipynb
│   └── (future notebooks follow same format)
│
├── utils/                    # Centralized helpers imported by all notebooks
│   ├── openai_client.py      # Canonical OpenAI client creation
│   ├── models.py             # Curated model catalog + selector
│   └── config.py             # Handles DEFAULT_MODEL via env + fallback
│
├── assets/                   # Images, sample docs, misc resources
├── .env                      # Local secrets (NOT committed)
├── .gitignore
├── LICENSE
├── README.md                 # You are here
└── requirements.txt          # Dependencies
```

---

# 🔧 Utilities Overview (House Style)

The `utils/` folder is the backbone of this repo. All notebooks import from here instead of writing ad‑hoc code.

## `utils/openai_client.py`

Centralizes creation of the `OpenAI()` client.

* Automatically loads `.env`
* Ensures **one consistent client** across notebooks
* Encourages best practices for API usage

**Imported as:**

```python
from utils.openai_client import get_openai_client
client = get_openai_client()
```

---

## `utils/models.py`

Your curated model table + helper functions:

* `list_recommended_models()` returns a structured catalog (id, label, category, notes)
* `choose_default_model(preference)` lets you choose:

  * "fast"
  * "quality"
  * "reasoning"
  * "vision"

This avoids hard‑coding and teaches students how to think about model selection.

**Imported as:**

```python
from utils.models import list_recommended_models, choose_default_model, DEFAULT_MODEL
```

---

## `utils/config.py`

Defines how `DEFAULT_MODEL` is chosen:

* If `OPENAI_DEFAULT_MODEL` exists in the `.env`, use it
* Otherwise fallback to `choose_default_model("fast")`

This gives you predictable behavior across notebooks.

---

# 📚 Notebook Series (Growing Curriculum)

Below is the planned sequence. Only **01** is complete and tested — more will be added as we go.

## ✅ 01 — Basic Chatbot (Completed)

* Environment setup + sanity checks
* Project root path handling
* Curated model table preview
* First Responses API request
* Clean JSON parsing

This notebook establishes the **house style** for all future notebooks.

---

## 📌 02 — Streaming Chatbot + Token Usage (Next)

* Streaming (`stream=True`) with incremental output
* Inspecting token usage for cost awareness
* Comparing "fast" vs "quality" model usage patterns

---

## 📌 03 — Structured Output / JSON Mode

* Extract structured data from input text
* Convert to pandas tables
* Practical introduction to mini-agent logic

---

## 📌 04 — Tools / Function Calling

* Create simple Python tools
* Responses API tool invocation loop
* Understanding model-tool interactions

---

## 📌 05 — File Search + Vector Store Mini‑RAG

* Upload a text/PDF file
* Build a minimal vector store
* Query using `file_search` tool
* Display relevant snippets + metadata

---

## 📌 06 — Model Explorer Dashboard

* List all live OpenAI models with `client.models.list()`
* Reconcile curated vs actual
* Teach how to keep the curated list updated over time

---

# 🛠️ Local Environment Setup

Create a `.env` file at the repo root:

```
OPENAI_API_KEY=your-key-here
OPENAI_DEFAULT_MODEL=gpt-4.1-mini  # Optional
```

Install dependencies:

```
pip install -r requirements.txt
```

Run notebooks:

```
jupyter notebook notebooks/01_basic_chatbot.ipynb
```

---

# 💡 Example Usage (From Utilities)

```python
from utils.openai_client import get_openai_client
from utils.models import choose_default_model

client = get_openai_client()
model = choose_default_model("fast")

response = client.responses.create(
    model=model,
    input="Explain the OpenAI Responses API in 2 sentences."
)
print(response.output_text)
```

---

# 🧭 Notes on the Curated Model List

The model table in `utils/models.py` is **curated by hand**.

* It reflects current best-practice suggestions
* It won’t automatically update when OpenAI adds or deprecates models
* Notebook 06 will teach you how to keep this list fresh

---

# 🤝 License

MIT License

You are free to use, modify, and teach from this repo.

---

# 🎯 Final Thoughts

This project is designed to grow with each notebook. The first one is now complete and validated — each new notebook should follow the same clean structure, using the helpers in `utils/` to keep everything consistent and professional.

Let's keep building this out one module at a time.
