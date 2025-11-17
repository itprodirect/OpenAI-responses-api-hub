# utils/config.py
import os
from .models import choose_default_model

# Let users override via env var, otherwise pick a sane default.
DEFAULT_MODEL = os.getenv(
    "OPENAI_DEFAULT_MODEL") or choose_default_model("fast")
