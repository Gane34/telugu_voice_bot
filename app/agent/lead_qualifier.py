from enum import Enum


class LeadQualification(str, Enum):
    HOT = "HOT"
    WARM = "WARM"
    COLD = "COLD"
    DO_NOT_CALL = "DO_NOT_CALL"


def classify_lead(lead: dict) -> LeadQualification:
    if lead.get("interest") in {LeadQualification.DO_NOT_CALL.value, "DO_NOT_CALL"}:
        return LeadQualification.DO_NOT_CALL
    if lead.get("do_not_call"):
        return LeadQualification.DO_NOT_CALL
    if lead.get("interest") == "HOT" or (
        lead.get("demo_requested")
        and lead.get("decision_maker")
        and lead.get("current_management_method")
    ):
        return LeadQualification.HOT
    if lead.get("interest") == "WARM" or lead.get("callback_requested"):
        return LeadQualification.WARM
    return LeadQualification.COLD
