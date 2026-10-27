"""Offline boundary tests; no model calls and no platform writes."""
import unittest
import json
import tempfile
from pathlib import Path
from compose import compose, persona_prompt, SCENES, SUPPORT


class CompositionBoundaryTests(unittest.TestCase):
    def test_same_topic_routes_by_content_anchor(self):
        variants = [compose("outdoor", scene, "xhs", brief="周末城市散步")
                    for scene in ("self", "place", "daily", "guide")]
        self.assertEqual(len({v["selected_skills"][0] for v in variants}), 4)
        self.assertEqual(len({v["system_prompt"] for v in variants}), 1)

    def test_persona_change_does_not_change_reusable_skills(self):
        peach = compose("xiaotao", "reply", "xhs")
        outdoor = compose("outdoor", "reply", "xhs")
        self.assertNotEqual(peach["system_prompt"], outdoor["system_prompt"])
        self.assertEqual(peach["skill_hashes"], outdoor["skill_hashes"])
        self.assertNotIn("不自称小桃", peach["system_prompt"])
        self.assertIn("不自称小桃", outdoor["system_prompt"])

    def test_evidence_cannot_leak_into_stable_persona(self):
        result = compose("outdoor", "place", "xhs", context={"foreign_post": "我昨天在北京走了12公里"})
        self.assertNotIn("北京", result["system_prompt"])
        self.assertNotIn("12公里", result["system_prompt"])
        self.assertIn("foreign_post", result["task_prompt"])
        self.assertEqual(result["system_prompt"], persona_prompt("outdoor"))

    def test_platform_and_support_are_independent_and_deduplicated(self):
        result = compose("xiaotao", "item", "xianyu", ["humanize", "humanize"])
        self.assertEqual(result["selected_skills"], ["trade-product-present", "common-expression-polish", "platform-xianyu"])
        self.assertNotIn("platform-xhs", result["selected_skills"])

    def test_every_scene_and_support_loads(self):
        for scene in SCENES:
            result = compose("xiaotao", scene, "xhs", list(SUPPORT))
            self.assertTrue(all(len(v) == 64 for v in result["skill_hashes"].values()))
            self.assertEqual(set(result["selected_skills"]), set(result["skill_hashes"]))

    def test_external_account_profile_needs_no_skill_edit(self):
        profile = {"name": "新账号", "identity": "二手相机爱好者", "preferences": ["机械拨盘"],
                   "attitudes": ["愿意修复而不急着换新"], "voice": "简短平实", "known_facts": [],
                   "unknown_facts": ["实际持有的型号"], "boundaries": "不编商品状态"}
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "account.json"
            path.write_text(json.dumps(profile, ensure_ascii=False))
            result = compose("camera", "item", "xianyu", persona_file=path)
        self.assertIn("机械拨盘", result["system_prompt"])
        self.assertNotIn("小桃", result["system_prompt"])
        self.assertEqual(result["selected_skills"], ["trade-product-present", "platform-xianyu"])


if __name__ == "__main__":
    unittest.main()
