import re
from typing import Any, Dict


class SafetyPolicy:
    DO_NOT_CALL_PATTERNS = [
        "do not call",
        "dont call",
        "don't call",
        "remove my number",
        "not interested",
        "not interested anymore",
        "stop calling",
        "never call again",
        "do not contact",
        "remove from list",
        "not a decision maker",
    ]

    @staticmethod
    def should_do_not_call(text: str) -> bool:
        value = (text or "").lower()
        return any(pattern in value for pattern in SafetyPolicy.DO_NOT_CALL_PATTERNS)

    @staticmethod
    def validate_claims(claim: str, facts: Dict[str, Any]) -> bool:
        if not claim:
            return True
        normalized = claim.lower()
        if "customer" in normalized or "revenue" in normalized or "partnership" in normalized or "testimonial" in normalized:
            return False
        if "₹3,000" in claim or "3000" in claim:
            if "setup" in normalized or "early access" in normalized or "price" in normalized:
                return True
        if "gym os" in normalized and "₹3,000" in normalized:
            return True
        if "we have" in normalized or "our" in normalized and "customers" in normalized:
            return False
        if "does not have" in normalized and "information" in normalized:
            return True
        return True

    @staticmethod
    def is_valid_phone_number(phone: str) -> bool:
        if not phone:
            return False
        return bool(re.fullmatch(r"\+?[0-9()\-\s]{7,20}", phone.strip()))
