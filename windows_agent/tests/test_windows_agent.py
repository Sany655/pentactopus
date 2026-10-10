import unittest
from pathlib import Path

from windows_agent.agent import ApprovalRequired, WindowsAgent
from windows_agent.notepad import MAX_NOTEPAD_TEXT_CHARACTERS, MockNotepadController
from windows_agent.policy import LocalPolicy, PolicyError, load_policy
from windows_agent.whatsapp import MockWhatsAppUI, WhatsAppReader


class LocalPolicyTests(unittest.TestCase):
    def test_policy_blocks_t6_apps(self):
        policy = load_policy(Path(__file__).resolve().parents[1] / "policy.example.json")
        with self.assertRaises(PolicyError):
            policy.validate_action("system_settings", action_tier=5, app_name="Bitwarden")

    def test_policy_allows_t2_read_content_for_own_device(self):
        policy = load_policy(Path(__file__).resolve().parents[1] / "policy.example.json")
        required = policy.validate_action("read_message_content", action_tier=2, app_name="WhatsApp")
        self.assertEqual(required, 2)


class WindowsAgentTests(unittest.TestCase):
    def setUp(self):
        policy = load_policy(Path(__file__).resolve().parents[1] / "policy.example.json")
        whatsapp = WhatsAppReader(
            MockWhatsAppUI([
                {
                    "message_id": "msg-1",
                    "sender": "Alicia",
                    "text": "Can you pick up milk?",
                    "timestamp": "2026-01-01T08:00:00Z",
                    "is_unread": True,
                }
            ])
        )
        self.notepad = MockNotepadController()
        self.audit_events = []
        self.agent = WindowsAgent(
            policy=policy,
            whatsapp_reader=whatsapp,
            notepad_controller=self.notepad,
            audit_sink=self.audit_events.append,
        )

    def test_read_message_metadata_works_for_t1(self):
        result = self.agent.run_task({"capability": "read_message_metadata", "tier": 1})
        self.assertEqual(result["status"], "done")
        self.assertEqual(result["result"][0]["sender"], "Alicia")

    def test_read_message_content_works_for_t2(self):
        result = self.agent.run_task({"capability": "read_message_content", "tier": 2, "message_id": "msg-1"})
        self.assertEqual(result["status"], "done")
        self.assertIn("milk", result["result"]["text"])

    def test_draft_message_uses_local_model_stub(self):
        result = self.agent.run_task({"capability": "draft_message", "tier": 3, "prompt": "Say hi."})
        self.assertEqual(result["status"], "done")
        self.assertIn("Draft:", result["result"]["draft"])

    def test_send_message_requires_t4_approval(self):
        with self.assertRaises(ApprovalRequired):
            self.agent.run_task({
                "capability": "send_message",
                "tier": 4,
                "requires_confirmation": True,
                "recipient": "+15550001111",
                "payload": "hello",
            })

    def test_draft_text_in_notepad_opens_and_types_without_logging_text(self):
        result = self.agent.run_task({
            "capability": "draft_text_in_notepad",
            "tier": 3,
            "app_name": "notepad.exe",
            "text": "Write this into Notepad.",
        })

        self.assertEqual(result["status"], "done")
        self.assertTrue(self.notepad.opened)
        self.assertEqual(self.notepad.text, "Write this into Notepad.")
        self.assertEqual(self.audit_events[-1].metadata["character_count"], 24)
        self.assertNotIn("Write this into Notepad.", repr(self.audit_events))

    def test_draft_text_in_notepad_rejects_empty_text(self):
        with self.assertRaises(ValueError):
            self.agent.run_task({
                "capability": "draft_text_in_notepad",
                "tier": 3,
                "text": "   ",
            })

    def test_draft_text_in_notepad_enforces_length_limit(self):
        with self.assertRaises(ValueError):
            self.agent.run_task({
                "capability": "draft_text_in_notepad",
                "tier": 3,
                "text": "x" * (MAX_NOTEPAD_TEXT_CHARACTERS + 1),
            })
        self.assertFalse(self.notepad.opened)


if __name__ == "__main__":
    unittest.main()
