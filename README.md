# 🧠 OpenAI Responses API Hub

A hands-on, methodical hub for learning and mastering the **OpenAI Responses API** using clean, reusable patterns, curated model helpers, and step-by-step Jupyter notebooks.

This repo intentionally evolves one notebook at a time. Each notebook builds on a consistent structure and introduces a new capability — from basic chat to streaming, structured outputs, tools, and eventually full RAG pipelines.

---

# 🚀 Repo Purpose

This repo exists to give you (and anyone learning from your work) a **repeatable, professional-grade template** for:

* Understanding how to use the OpenAI Responses API properly
* Comparing model categories (fast / quality / reasoning / vision)
* Using a shared utilities package across notebooks
* Demonstrating real-world patterns you can use in consulting and training
* Building RAG, tools, and multimodal workflows one small step at a time

Every notebook follows the same setup pattern, so this repo doubles as both:

1. **A personal learning platform**, and
2. **A teaching-ready curriculum** you can use for AI training services.

---

# 📁 Project Structure

```bash
openai-responses-api-hub/
│
├── notebooks/                # Jupyter notebooks for each lesson/module
│   ├── 01_basic_chatbot.ipynb
│   ├── 02_tools_and_reasoning.ipynb
│   └── (future notebooks follow same format)
│
├── utils/                    # Centralized helpers imported by all notebooks
│   ├── openai_client.py      # Canonical OpenAI client creation
│   ├── models.py             # Curated model catalog + selector
│   └── config.py             # Handles DEFAULT_MODEL via env + fallback
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

The `utils/` folder is the backbone of this repo. All notebooks import from here instead of writing ad-hoc code.

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

This avoids hard-coding and teaches students how to think about model selection.

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

## ✅ 01 — Basic Chatbot (Completed)

* Environment setup + sanity checks
* Project root path handling
* Curated model table preview
* First Responses API request
* Clean JSON parsing

This notebook establishes the **house style** for all future notebooks.

---

## ✅ 02 — Web Search & Agentic Reasoning (Completed)

* Uses the hosted **`web_search`** tool to find live music events
* Lets the model:

  * gather real-world information,
  * pick a concert near a location, and
  * draft a **ready-to-send email** invitation
* Prompts the model to separate:

  * a **"Reasoning"** section (how it searched and chose), and
  * the **"Final email"**
* Includes an **advanced, optional section**:

  * custom `basic_calculator` function tool
  * tool call inspection
  * clean, non-technical summary of what the calculator did

This notebook showcases both **built-in tools** and the first taste of **custom tools**, in a way non-technical people can still follow.

---

## 🔭 Roadmap: Next 3 Notebooks

### 📌 03 — Structured Output & JSON Mode

Goal: move from “nice prose” to **machine-usable data**.

Planned topics:

* Prompting the model to return **strict JSON** (e.g., task lists, meeting summaries)
* Validating / parsing the JSON in Python
* Displaying the result in a **pandas DataFrame** (tables, filters, simple analytics)
* Pattern: *unstructured text → structured rows → human + machine readable*

---

### 📌 04 — Custom Tools & Multi-step Workflows

Goal: go beyond the simple calculator and build real **Python-powered tools**.

Planned topics:

* Defining multiple custom tools (e.g., simple datastore reader/writer, formatter)
* Letting the model decide **which tool to call and in what order**
* Executing tool calls in Python and feeding results back into Responses
* Pattern: *model plans → calls tools → uses tool output to refine the answer*

This is where the “agent” idea becomes concrete for business workflows.

---

### 📌 05 — File Search + Mini-RAG

Goal: introduce Retrieval-Augmented Generation on a small, controlled dataset.

Planned topics:

* Adding a short PDF / text document to the project
* Using OpenAI’s **`file_search` / vector store** tools from the Responses API
* Asking questions and getting answers with **citations back to the source**
* Pattern: *upload docs → index them → Q&A with references*

This will directly connect to future real-world RAG demos (insurance, legal, JFK project, etc.).

*(Beyond that, additional notebooks like a **Model Explorer Dashboard** and **UI demos** can be added later as the repo grows.)*

---

# 🛠️ Local Environment Setup

Create a `.env` file at the repo root:

```bash
OPENAI_API_KEY=your-key-here
OPENAI_DEFAULT_MODEL=gpt-4.1-mini  # Optional
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run notebooks:

```bash
jupyter notebook notebooks/01_basic_chatbot.ipynb
jupyter notebook notebooks/02_tools_and_reasoning.ipynb
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
* A future “Model Explorer” notebook will show how to keep this list fresh

---

# 🤝 License

MIT License

You are free to use, modify, and teach from this repo.

---

# 🎯 Final Thoughts

The first two notebooks are now complete and validated. Each new notebook should follow the same clean structure, using the helpers in `utils/` to keep everything consistent and professional.

From here, the next three notebooks (03–05) will add structured outputs, richer tool workflows, and file search / mini-RAG — the same building blocks you’ll reuse in real client projects.
