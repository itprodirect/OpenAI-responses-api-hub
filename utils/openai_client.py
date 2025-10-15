import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"

def get_response(input_text: str, model: str = "gpt-4o") -> str:
    """
    Sends a prompt to the OpenAI Responses API and returns the assistant's output text.
    """
    if not OPENAI_API_KEY:
        raise ValueError("Missing OPENAI_API_KEY environment variable.")

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "input": input_text
    }

    try:
        response = requests.post(OPENAI_RESPONSES_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        # Parse the output text safely
        return data.get("output", [{}])[0].get("content", [{}])[0].get("text", "[No text returned]")
    except Exception as e:
        return f"[Error]: {str(e)}"
