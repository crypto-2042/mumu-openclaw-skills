import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))

import manage_memory
import trigger_batch


class ManageMemoryTests(unittest.TestCase):
    def test_build_foreshadow_title_uses_content_prefix(self):
        content = "回归测试伏笔：主角在雨夜收到一段异常坐标，并意识到有人提前布局。"
        title = manage_memory.build_foreshadow_title(content)

        self.assertTrue(title.startswith("回归测试伏笔"))
        self.assertLessEqual(len(title), 200)

    def test_batch_generation_blocked_until_project_ready(self):
        project = {"wizard_status": "incomplete", "wizard_step": 3}

        blocker = trigger_batch.get_batch_blocker(project, [])

        self.assertIn("not finished", blocker.lower())


if __name__ == "__main__":
    unittest.main()
