from agent.core import AndroidAgent
from models.mock import MockModelProvider

def test_agent_open_calculator():
    model = MockModelProvider()
    agent = AndroidAgent(model_provider=model, dry_run=True)
    res = agent.run_goal("Open Calculator")
    assert res["success"] is True
    assert "Calculator" in res["message"]
