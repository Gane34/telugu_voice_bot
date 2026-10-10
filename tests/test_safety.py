from app.agent.safety import SafetyPolicy


def test_do_not_call_flag_triggers():
    text = "don't call me again remover my number"
    assert SafetyPolicy.should_do_not_call(text) is True


def test_hallucination_protection():
    policy = SafetyPolicy()
    facts = {"product": "Gym OS", "pricing": {"early_access_setup": "₹3,000"}}
    assert policy.validate_claims("Gym OS costs ₹3,000 setup", facts) is True
    assert policy.validate_claims("We have 50,000 customers", facts) is False
