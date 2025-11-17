# utils/models.py
from typing import List, Dict
from openai import OpenAI

client = OpenAI()

# Opinionated “shortlist” of models we actually teach
RECOMMENDED_MODELS: Dict[str, Dict] = {
    "gpt-4.1-mini": {
        "label": "Fast + cheap general",
        "category": "fast",
        "notes": "Good default for most text tasks with Responses API.",
    },
    "gpt-4.1": {
        "label": "High quality general",
        "category": "quality",
        "notes": "Better reasoning/writing; higher cost.",
    },
    "o4-mini": {
        "label": "Reasoning",
        "category": "reasoning",
        "notes": "Use when you care about multi-step reasoning.",
    },
    "gpt-image-1": {
        "label": "Images",
        "category": "image",
        "notes": "Image generation via Responses.",
    },
    # add / adjust as models evolve
}


def list_raw_models() -> List[str]:
    """Return raw model IDs for this API key."""
    models_page = client.models.list()
    # New SDK uses .data on the cursor page
    return [m.id for m in models_page.data]


def list_recommended_models() -> Dict[str, Dict]:
    """
    Intersect RECOMMENDED_MODELS with what is actually available
    on this API key.
    """
    available = set(list_raw_models())
    result = {}

    for model_id, meta in RECOMMENDED_MODELS.items():
        if model_id in available:
            result[model_id] = {**meta, "available": True}
        else:
            # still show, but mark as unavailable (optional)
            result[model_id] = {**meta, "available": False}

    return result


def choose_default_model(preference: str = "fast") -> str:
    """
    Pick a default model based on a simple preference:
    'fast', 'quality', 'reasoning', 'image'
    Falls back sensibly if that category isn't available.
    """
    models = list_recommended_models()

    # First pass: match category + available
    for mid, meta in models.items():
        if meta["category"] == preference and meta.get("available"):
            return mid

    # Second pass: any available model
    for mid, meta in models.items():
        if meta.get("available"):
            return mid

    # Last resort: hard-coded safe default
    return "gpt-4.1-mini"