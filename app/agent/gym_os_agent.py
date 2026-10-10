import json
from pathlib import Path

from app.agent.conversation_manager import ConversationManager, ConversationState
from app.agent.safety import SafetyPolicy


def normalize_telugu_text(text: str) -> str:
    if not text:
        return ""
    value = text.strip()
    value = value.replace("\u200c", "")
    return value


class GymOSAgent:
    def __init__(self, knowledge_path: str | None = None) -> None:
        base = Path(__file__).resolve().parent.parent
        default_path = base / "knowledge" / "gym_os_knowledge.json"
        self.knowledge_path = Path(knowledge_path) if knowledge_path else default_path
        self.knowledge = self._load_knowledge()
        self.conversation_manager = ConversationManager()

    def _load_knowledge(self) -> dict:
        if not self.knowledge_path.exists():
            return {
                "product": "Gym OS",
                "description": "Gym management software",
                "pricing": {"early_access_setup": "₹3,000"},
                "features": ["member management", "attendance management", "payment tracking", "member follow-ups"],
            }
        with self.knowledge_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def respond(self, user_input: str, lead_context: dict | None = None) -> str:
        lead_context = lead_context or {}
        normalized = normalize_telugu_text(user_input)
        lowered = normalized.lower()

        if SafetyPolicy.should_do_not_call(normalized):
            self.conversation_manager.state = ConversationState.DO_NOT_CALL
            return "సరే, మీకు మళ్లీ కాల్ చేయము. మీ నంబర్ do-not-call list లో ఉంచుతాము."

        if "not interested" in lowered or "don't call" in lowered or "remove my number" in lowered:
            self.conversation_manager.state = ConversationState.DO_NOT_CALL
            return "సరే, మీరు చెప్పిన ప్రకారం మేము ఇక మళ్లీ కాల్ చేయము."

        if "hello" in lowered or "namaskaram" in lowered or "hallo" in lowered:
            self.conversation_manager.state = ConversationState.INTRO
            return "నమస్కారం సార్/మేడమ్. నేను Gym OS నుంచి AI assistant గా మాట్లాడుతున్నాను. మీకు 30 seconds మాట్లాడే అవకాశం ఉందా?"

        if "members" in lowered or "attendance" in lowered or "payment" in lowered or "fees" in lowered or "follow" in lowered:
            self.conversation_manager.state = ConversationState.PAIN_POINT
            return self.conversation_manager.next_prompt()

        if "demo" in lowered or "show" in lowered:
            self.conversation_manager.state = ConversationState.DEMO
            return self.conversation_manager.next_prompt()

        if "price" in lowered or "3000" in lowered or "₹3,000" in lowered or "setup fee" in lowered:
            self.conversation_manager.state = ConversationState.PRICING
            return self.conversation_manager.next_prompt()

        if "excel" in lowered or "whatsapp" in lowered or "notebook" in lowered or "software" in lowered:
            self.conversation_manager.state = ConversationState.DISCOVERY
            return "అర్థమైంది. ఆ process లో 어떤 pain point ఉంది? member follow-ups, attendance tracking, లేదా pending payments?"

        self.conversation_manager.state = ConversationState.DISCOVERY
        return self.conversation_manager.next_prompt()

    def get_product_knowledge(self) -> dict:
        return self.knowledge
