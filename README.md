# 🧠 OpenAI Responses API Hub

Welcome to the **OpenAI Responses API Hub** — a modular, hands-on project designed to help you master the OpenAI Responses API through guided notebooks, real-world examples, and tool integrations.

This repo evolves with each notebook — starting from the basics and gradually integrating advanced features like multimodal inputs, tool use, UI design, and response streaming.

---

## 🚀 Project Goals

- Build a smart assistant using OpenAI’s Responses API
- Learn to structure Python projects for scalability
- Explore image input and multimodal capabilities
- Create interactive UIs using [Gradio](https://www.gradio.app/)
- Use built-in tools like web search, file reading, and calculator logic
- Stream chatbot responses for real-time output

---

## 📁 Project Structure

```bash
openai-responses-api-hub/
│
├── notebooks/                # Jupyter notebooks for each module
├── utils/                    # Helper functions and modular code
├── assets/                   # (Optional) images, docs, or dataset files
├── .env                      # API keys and secrets (excluded from repo)
├── .gitignore                # Files & folders to ignore in version control
├── LICENSE                   # Project license
├── README.md                 # You are here!
└── requirements.txt          # Python dependencies
```

## 🔧 Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/your-user/openai-responses-api-hub.git
cd openai-responses-api-hub
pip install -r requirements.txt
```
This command installs the exact package versions listed in `requirements.txt`.

## 🛠️ Environment Setup

Create a `.env` file at the project root and add your OpenAI API key:

```bash
OPENAI_API_KEY=your-api-key-here
```

Both the notebooks and `utils/openai_client.py` load this key automatically via `python-dotenv`.

## 📓 Running the Sample Notebooks

Start Jupyter and open the notebooks inside the `notebooks` folder:

```bash
jupyter notebook notebooks/01_basic_chatbot.ipynb
```

Work through each notebook to explore different API capabilities.

## 💡 Usage Example

The helper `get_response` function in `utils/openai_client.py` now wraps the
latest `OpenAI` SDK, so you can opt into tools, modalities, or streaming without
rewriting your scripts:

```python
from utils.openai_client import get_response

# Basic, blocking call
reply = get_response("Summarize the OpenAI Responses API in 2 sentences.")
print(reply)

# Stream deltas for a faster-feeling UI experience
for chunk in get_response("Write a limerick about streaming text", stream=True):
    print(chunk, end="", flush=True)
```

See the notebooks for more detailed examples and workflows.

## License

This project is licensed under the [MIT License](LICENSE).
