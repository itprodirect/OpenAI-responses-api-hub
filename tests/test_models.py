import unittest

from utils.models import choose_default_model, list_recommended_models


class ModelsTests(unittest.TestCase):
    def test_choose_default_model_uses_curated_category(self) -> None:
        self.assertEqual(choose_default_model("fast"), "gpt-4.1-mini")
        self.assertEqual(choose_default_model("quality"), "gpt-4.1")

    def test_choose_default_model_falls_back_for_unknown_preference(self) -> None:
        self.assertEqual(choose_default_model("unknown"), "gpt-4.1-mini")

    def test_list_recommended_models_can_skip_live_availability_checks(self) -> None:
        models = list_recommended_models(validate_availability=False)

        self.assertEqual(models["gpt-4.1-mini"]["available"], None)
        self.assertEqual(models["o4-mini"]["category"], "reasoning")


if __name__ == "__main__":
    unittest.main()
