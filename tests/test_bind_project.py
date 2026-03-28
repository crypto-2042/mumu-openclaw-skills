import unittest
import pathlib
import sys
import tempfile
import time
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))

import bind_project
import client as mumu_client
import runtime_state


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

    def test_outline_resume_uses_backend_init_defaults(self):
        project = {
            "id": "project-1",
            "wizard_status": "incomplete",
            "wizard_step": 3,
            "narrative_perspective": "第三人称",
            "target_words": 1000000,
            "chapter_count": 5,
        }

        payload = bind_project.build_outline_payload(project)

        self.assertEqual(
            payload,
            {
                "project_id": "project-1",
                "narrative_perspective": "第三人称",
            },
        )

    def test_advance_status_reports_outline_org_enrichment(self):
        project = {
            "id": "project-1",
            "title": "Test",
            "wizard_status": "incomplete",
            "wizard_step": 3,
        }
        progress_state = {
            "step_name": "Outline",
            "subphase": "organization_enrichment",
            "message": "自动创建了 4 个组织: A, B, C, D",
        }

        payload = bind_project.build_advance_status(project, progress_state=progress_state)

        self.assertEqual(payload["phase"], "outline")
        self.assertEqual(payload["subphase"], "organization_enrichment")
        self.assertEqual(payload["status"], "running")
        self.assertEqual(payload["last_completed_stage"], "characters")
        self.assertEqual(payload["next_action"], "advance")
        self.assertEqual(payload["recommended_wait_seconds"], 60)
        self.assertEqual(payload["estimated_remaining_minutes"], 3)
        self.assertIn("自动创建了 4 个组织", payload["message"])

    def test_ready_project_reports_done_subphase(self):
        project = {
            "id": "project-1",
            "title": "Test",
            "wizard_status": "completed",
            "wizard_step": 4,
        }

        payload = bind_project.build_advance_status(project)

        self.assertTrue(payload["ready"])
        self.assertEqual(payload["status"], "completed")
        self.assertEqual(payload["phase"], "completed")
        self.assertEqual(payload["subphase"], "done")
        self.assertEqual(payload["last_completed_stage"], "outline")
        self.assertEqual(payload["next_action"], "done")
        self.assertEqual(payload["recommended_wait_seconds"], 0)
        self.assertEqual(payload["estimated_remaining_minutes"], 0)

    def test_running_runtime_snapshot_reports_progress(self):
        project = {
            "id": "project-1",
            "title": "Test",
            "wizard_status": "incomplete",
            "wizard_step": 1,
        }
        runtime_snapshot = {
            "status": "running",
            "phase": "career_system",
            "subphase": "generating",
            "last_message": "生成职业体系中...",
            "last_progress": 42,
        }

        payload = bind_project.build_advance_status(project, progress_state=runtime_snapshot)

        self.assertFalse(payload["ready"])
        self.assertEqual(payload["status"], "running")
        self.assertEqual(payload["phase"], "career_system")
        self.assertEqual(payload["subphase"], "generating")
        self.assertEqual(payload["message"], "生成职业体系中...")
        self.assertEqual(payload["next_action"], "advance")
        self.assertEqual(payload["recommended_wait_seconds"], 45)
        self.assertEqual(payload["estimated_remaining_minutes"], 3)

    def test_completed_project_is_ready(self):
        project = {"wizard_status": "completed", "wizard_step": 4}

        self.assertTrue(bind_project.is_project_ready(project))
        self.assertIsNone(bind_project.get_next_wizard_action(project))
        self.assertEqual(bind_project.get_wizard_stage_label(project), "completed")

    def test_stream_requests_disable_read_timeout(self):
        timeout = mumu_client.get_request_timeout(stream=True)

        self.assertEqual(timeout, (mumu_client.DEFAULT_TIMEOUT, None))

    def test_runtime_state_roundtrip_and_stale_detection(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.dict("os.environ", {"MUMU_RUNTIME_DIR": tmpdir}):
                runtime_state.save_state(
                    "project-1",
                    {
                        "project_id": "project-1",
                        "status": "running",
                        "updated_at": time.time(),
                        "last_message": "working",
                    },
                )

                loaded = runtime_state.load_state("project-1")

                self.assertEqual(loaded["project_id"], "project-1")
                self.assertFalse(runtime_state.is_stale(loaded, stale_after_seconds=300))

                loaded["updated_at"] = time.time() - 600
                self.assertTrue(runtime_state.is_stale(loaded, stale_after_seconds=300))

    def test_runtime_state_includes_owner_and_runner(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.dict(
                "os.environ",
                {"MUMU_RUNTIME_DIR": tmpdir, "MUMU_OWNER_ID": "agent-a"},
            ):
                saved = runtime_state.save_state(
                    "project-1",
                    {
                        "project_id": "project-1",
                        "runner_id": "runner-1",
                        "status": "running",
                    },
                )

                self.assertEqual(saved["owner_id"], "agent-a")
                self.assertEqual(saved["runner_id"], "runner-1")

    def test_load_runtime_snapshot_marks_foreign_owner_as_external(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.dict(
                "os.environ",
                {"MUMU_RUNTIME_DIR": tmpdir, "MUMU_OWNER_ID": "agent-b"},
            ):
                runtime_state.save_state(
                    "project-1",
                    {
                        "project_id": "project-1",
                        "owner_id": "agent-a",
                        "runner_id": "runner-1",
                        "status": "running",
                        "updated_at": time.time(),
                    },
                )

                loaded = bind_project.load_runtime_snapshot("project-1")

                self.assertEqual(loaded["status"], "external")
                self.assertEqual(loaded["owner_id"], "agent-a")

    def test_build_runtime_payload_records_owner_and_runner(self):
        project = {
            "id": "project-1",
            "title": "Test",
            "wizard_status": "incomplete",
            "wizard_step": 1,
        }
        progress_state = {
            "subphase": "generating",
            "message": "生成职业体系中...",
            "progress": 42,
        }

        with mock.patch.dict("os.environ", {"MUMU_OWNER_ID": "agent-a"}):
            payload = bind_project.build_runtime_payload(
                project,
                progress_state,
                status="running",
                pid=1234,
                runner_id="runner-1",
            )

        self.assertEqual(payload["owner_id"], "agent-a")
        self.assertEqual(payload["runner_id"], "runner-1")
        self.assertEqual(payload["pid"], 1234)


if __name__ == "__main__":
    unittest.main()
