import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from utils.openai_client import get_api_key, get_openai_client, get_response


class OpenAIClientTests(unittest.TestCase):
    def test_get_api_key_requires_env_or_explicit_value(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            get_openai_client.cache_clear()
            with self.assertRaises(ValueError):
                get_api_key()

    def test_get_response_uses_injected_client(self) -> None:
        response = SimpleNamespace(output_text="done")
        fake_client = SimpleNamespace(
            responses=SimpleNamespace(create=lambda **kwargs: response)
        )

        result = get_response("ping", model="test-model", client=fake_client)

        self.assertEqual(result, "done")


if __name__ == "__main__":
    unittest.main()
