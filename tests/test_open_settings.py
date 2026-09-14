from agent.core import AndroidAgent
from models.mock import MockModelProvider

def test_agent_open_settings():
    model = MockModelProvider()
    agent = AndroidAgent(model_provider=model, dry_run=True)
    res = agent.run_goal("Open Android Settings")
    assert res["success"] is True
    assert "Settings" in res["message"]
