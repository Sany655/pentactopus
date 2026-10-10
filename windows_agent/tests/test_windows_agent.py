import unittest
from pathlib import Path

from windows_agent.agent import ApprovalRequired, WindowsAgent
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
        self.agent = WindowsAgent(policy=policy, whatsapp_reader=whatsapp)

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


if __name__ == "__main__":
    unittest.main()
