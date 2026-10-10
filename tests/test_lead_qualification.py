from app.agent.lead_qualifier import classify_lead, LeadQualification


def test_hot_lead_detection():
    lead = {
        "current_management_method": "Excel",
        "pain_points": ["pending payments", "attendance tracking"],
        "interest": "HOT",
        "demo_requested": True,
        "decision_maker": True,
    }
    result = classify_lead(lead)
    assert result == LeadQualification.HOT


def test_warm_lead_detection():
    lead = {
        "current_management_method": "WhatsApp",
        "pain_points": ["follow-ups"],
        "interest": "WARM",
        "demo_requested": False,
        "decision_maker": False,
    }
    result = classify_lead(lead)
    assert result == LeadQualification.WARM


def test_cold_lead_detection():
    lead = {
        "current_management_method": "Already using software",
        "pain_points": [],
        "interest": "COLD",
        "demo_requested": False,
        "decision_maker": True,
    }
    result = classify_lead(lead)
    assert result == LeadQualification.COLD
