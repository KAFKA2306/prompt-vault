from pathlib import Path
import json
import tempfile
import unittest

from src.ideation import compile_ideation_profile_payload, load_ideation_profile, retrieve_ideation


class IdeationContractTest(unittest.TestCase):
    def setUp(self):
        self.tweetsdb = {
            "schema": {"version": 2},
            "profile": {
                "dominant_traits": ["observational"],
                "prompt_generation_recipe": ["Pick one concrete observation."],
                "imagegen_recipe": ["Turn it into a compact scene."],
            },
            "summary": {
                "top_topics": [["food-drink", 2], ["creator-tools", 1]],
                "top_moods": [["cheerful", 2]],
                "top_functions": [["observation", 2]],
                "owner_signals": [["自分発信", 3]],
                "reuse_types": [["画像", 2], ["ネタ", 1]],
                "latent_modes": [["sensory", 2], ["tooling", 1]],
                "prompt_biases": [["visual", 2]],
                "topic_transitions": [["food-drink -> creator-tools", 1]],
                "mood_transitions": [],
                "confidence": {"mean": 0.9},
            },
            "records": [
                {
                    "id": "1",
                    "text": "バニララテ美味しくて毎日飲んじゃう！",
                    "topic": ["food-drink"],
                    "mood": "cheerful",
                    "function": "observation",
                    "style": ["short", "casual"],
                    "owner_signal": "自分発信",
                    "essence": "observation about food or drink",
                    "trait_tags": ["sensory", "everyday-observation"],
                    "prompt_seed": "food or drink note",
                    "imagegen_seed": "a food or drink scene with tactile detail",
                    "evidence_text": "バニララテ美味しくて毎日飲んじゃう！",
                    "latent_profile": {"observation_mode": "sensory"},
                    "reuse_type": "画像",
                    "reuse_score": 0.9,
                    "importance": 0.5,
                    "classification_confidence": 0.95,
                    "creator_signal": False,
                    "quality_flags": ["clean"],
                },
                {
                    "id": "2",
                    "text": "画像生成の仕組みを試す",
                    "topic": ["creator-tools"],
                    "mood": "curious",
                    "function": "process_log",
                    "style": ["technical"],
                    "owner_signal": "自分発信",
                    "essence": "creator workflow observation",
                    "trait_tags": ["creator-aware", "tool-aware"],
                    "prompt_seed": "creator workflow note",
                    "imagegen_seed": "a creator desk with tools and iteration notes",
                    "evidence_text": "画像生成の仕組みを試す",
                    "latent_profile": {"observation_mode": "tooling"},
                    "reuse_type": "ネタ",
                    "reuse_score": 0.8,
                    "importance": 0.4,
                    "classification_confidence": 0.9,
                    "creator_signal": True,
                    "quality_flags": ["clean"],
                },
            ],
        }

    def test_compile_keeps_profile_and_real_examples(self):
        payload = compile_ideation_profile_payload(
            self.tweetsdb,
            source_sha256="abc",
            max_exemplars=20,
        )
        self.assertEqual(payload["meta"]["source_record_count"], 2)
        self.assertEqual(payload["profile"]["dominant_traits"], ["observational"])
        self.assertEqual({item["id"] for item in payload["exemplars"]}, {"1", "2"})
        self.assertTrue(all(item["text"] for item in payload["exemplars"]))

    def test_retrieve_returns_evidence_for_query(self):
        payload = compile_ideation_profile_payload(
            self.tweetsdb,
            source_sha256="abc",
            max_exemplars=20,
        )
        result = retrieve_ideation(payload, "バニララテ", limit=1)
        self.assertEqual(result["reference_examples"][0]["id"], "1")
        self.assertIn("food or drink note", result["seed"]["prompt_seeds"])

    def test_load_requires_compiled_profile(self):
        payload = compile_ideation_profile_payload(
            self.tweetsdb,
            source_sha256="abc",
            max_exemplars=20,
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "profile.json"
            path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            loaded = load_ideation_profile(path)
            self.assertEqual(loaded["meta"]["name"], "kafka-ideation-profile")


if __name__ == "__main__":
    unittest.main()
