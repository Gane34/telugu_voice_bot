from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class LeadRecord:
    lead_id: str
    gym_name: str = ""
    contact_name: str = ""
    phone: str = ""
    location: str = ""
    language: str = "te"
    interest: str = "COLD"
    current_management_method: str = ""
    pain_points: List[str] = field(default_factory=list)
    features_of_interest: List[str] = field(default_factory=list)
    pricing_reaction: str = ""
    demo_requested: bool = False
    callback_requested: bool = False
    callback_time: str = ""
    decision_maker: bool = False
    summary: str = ""
    next_action: str = ""
    do_not_call: bool = False
    source: str = "manual"

    def to_dict(self) -> dict:
        return {
            "lead_id": self.lead_id,
            "gym_name": self.gym_name,
            "contact_name": self.contact_name,
            "phone": self.phone,
            "location": self.location,
            "language": self.language,
            "interest": self.interest,
            "current_management_method": self.current_management_method,
            "pain_points": self.pain_points,
            "features_of_interest": self.features_of_interest,
            "pricing_reaction": self.pricing_reaction,
            "demo_requested": self.demo_requested,
            "callback_requested": self.callback_requested,
            "callback_time": self.callback_time,
            "decision_maker": self.decision_maker,
            "summary": self.summary,
            "next_action": self.next_action,
            "do_not_call": self.do_not_call,
            "source": self.source,
        }
