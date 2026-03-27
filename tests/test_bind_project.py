import unittest
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))

import bind_project


class BindProjectWizardStateTests(unittest.TestCase):
    def test_incomplete_project_reports_next_step(self):
        project = {"wizard_status": "incomplete", "wizard_step": 1}

        self.assertFalse(bind_project.is_project_ready(project))
        self.assertEqual(bind_project.get_next_wizard_action(project), "career-system")
        self.assertEqual(bind_project.get_wizard_stage_label(project), "career_system")

    def test_midway_project_resumes_outline(self):
        project = {"wizard_status": "incomplete", "wizard_step": 3}

        self.assertFalse(bind_project.is_project_ready(project))
        self.assertEqual(bind_project.get_next_wizard_action(project), "outline")
        self.assertEqual(bind_project.get_wizard_stage_label(project), "outline")

    def test_completed_project_is_ready(self):
        project = {"wizard_status": "completed", "wizard_step": 4}

        self.assertTrue(bind_project.is_project_ready(project))
        self.assertIsNone(bind_project.get_next_wizard_action(project))
        self.assertEqual(bind_project.get_wizard_stage_label(project), "completed")


if __name__ == "__main__":
    unittest.main()
