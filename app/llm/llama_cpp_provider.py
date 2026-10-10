from app.llm.base import LLMProvider


class LlamaCppProvider(LLMProvider):
    def __init__(self, model_path: str | None = None) -> None:
        self.model_path = model_path

    async def generate(self, messages) -> str:
        text = ""
        for item in messages:
            text += str(item.get("content", "")) + "\n"
        return text.strip() or "Gym OS demo interest is positive."
