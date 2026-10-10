from app.agent.gym_os_agent import GymOSAgent


def test_agent_generates_telugu_intro():
    agent = GymOSAgent()
    response = agent.respond("hello", {
        "lead_id": "L-1",
        "gym_name": "Power Fitness",
        "language": "te",
        "decision_maker": True,
    })
    assert "నమస్కారం" in response or "Gym OS" in response
    assert len(response) < 500


def test_agent_handles_code_switching():
    agent = GymOSAgent()
    response = agent.respond("members attendance ela manage chestunnaru?", {
        "lead_id": "L-2",
        "language": "te",
        "decision_maker": True,
    })
    assert "attendance" in response.lower() or "members" in response.lower()
