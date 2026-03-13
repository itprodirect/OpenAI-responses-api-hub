"""Curated model catalog and model selection helpers."""

from __future__ import annotations

from typing import Dict, List, Optional

from openai import OpenAI

from .openai_client import get_openai_client

# Opinionated shortlist of models we teach and reuse.
RECOMMENDED_MODELS: Dict[str, Dict[str, object]] = {
    "gpt-4.1-mini": {
        "label": "Fast + cost-efficient general model",
        "category": "fast",
        "notes": "Great default for most text tasks using Responses API.",
    },
    "gpt-4.1": {
        "label": "Higher-quality general model",
        "category": "quality",
        "notes": "Use when writing quality and instruction-following matter most.",
    },
    "o4-mini": {
        "label": "Reasoning-focused model",
        "category": "reasoning",
        "notes": "Strong for multi-step tool use and deeper reasoning workflows.",
    },
    "gpt-4.1-mini-transcribe": {
        "label": "Speech-to-text",
        "category": "audio",
        "notes": "Useful for transcription-centric multimodal projects.",
    },
    "gpt-image-1": {
        "label": "Image generation",
        "category": "image",
        "notes": "Use for image synthesis workloads.",
    },
}


def list_raw_models(client: Optional[OpenAI] = None) -> List[str]:
    """Return raw model IDs visible to the active API key."""

    active_client = client or get_openai_client()
    models_page = active_client.models.list()
    return [model.id for model in models_page.data]


def list_recommended_models(client: Optional[OpenAI] = None) -> Dict[str, Dict[str, object]]:
    """Return recommended models with availability annotations."""

    available = set(list_raw_models(client=client))
    result: Dict[str, Dict[str, object]] = {}

    for model_id, meta in RECOMMENDED_MODELS.items():
        result[model_id] = {**meta, "available": model_id in available}

    return result


def choose_default_model(
    preference: str = "fast", client: Optional[OpenAI] = None
) -> str:
    """Pick a preferred model category, then gracefully fall back."""

    models = list_recommended_models(client=client)

    for model_id, meta in models.items():
        if meta["category"] == preference and bool(meta["available"]):
            return model_id

    for model_id, meta in models.items():
        if bool(meta["available"]):
            return model_id

    # Last-resort fallback for local development without API access.
    return "gpt-4.1-mini"
