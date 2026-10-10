import json
import os
from urllib import error, request

from app.llm.base import LLMProvider


class OllamaProvider(LLMProvider):
    def __init__(self, model: str | None = None, base_url: str | None = None, timeout: int = 30) -> None:
        self.model = model or os.getenv("OLLAMA_MODEL") or os.getenv("LLM_MODEL", "qwen2.5:3b-instruct")
        self.base_url = (base_url or os.getenv("OLLAMA_BASE_URL") or os.getenv("OLLAMA_HOST", "http://localhost:11434")).rstrip("/")
        self.timeout = timeout

    def _fallback_response(self, messages):
        prompt = "\n".join(item.get("content", "") for item in messages if isinstance(item, dict))
        lowered = prompt.lower()
        if "not interested" in lowered or "remove my number" in lowered:
            return "సరే, మీకు మళ్లీ కాల్ చేయము. మీ నంబర్ డో నాట్ కాల్ లిస్టులో ఉంచుతాను."
        if "demo" in lowered:
            return "మా founder మీకు చిన్న demo చూపించగలరు. ఎప్పుడు convenient గా ఉందో చెప్పండి."
        if "price" in lowered or "3000" in lowered or "₹3,000" in lowered:
            return "ప్రస్తుతం early-access setup fee ₹3,000. మీకు suitable అయితే demo arrange చేయవచ్చు."
        return "నమస్కారం. Gym OS లో member management, attendance, payments and follow-ups ఒకే system లో easy గా work చేస్తాయి. మీ current process గురించి చెప్పగలరా?"

    async def health_check(self) -> bool:
        try:
            req = request.Request(f"{self.base_url}/api/tags", method="GET")
            with request.urlopen(req, timeout=self.timeout) as resp:
                body = resp.read().decode("utf-8", errors="ignore")
                return "models" in body or body.strip() != ""
        except (error.URLError, error.HTTPError, TimeoutError, OSError):
            return False

    async def model_available(self) -> bool:
        try:
            req = request.Request(f"{self.base_url}/api/tags", method="GET")
            with request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8", errors="ignore"))
            models = []
            for item in data.get("models", []):
                name = item.get("name", "")
                if name:
                    models.append(name)
            return self.model in models or any(self.model in name for name in models)
        except (error.URLError, error.HTTPError, TimeoutError, OSError, json.JSONDecodeError):
            return False

    async def generate(self, messages):
        try:
            if not await self.health_check():
                return "Ollama is not running. Start Ollama and retry."
            if not await self.model_available():
                return f"Required Ollama model '{self.model}' is not installed. Run: ollama pull {self.model}"

            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
            }
            data = json.dumps(payload).encode("utf-8")
            endpoint = f"{self.base_url}/api/chat"
            req = request.Request(endpoint, data=data, headers={"Content-Type": "application/json"}, method="POST")
            with request.urlopen(req, timeout=self.timeout) as resp:
                response = json.loads(resp.read().decode("utf-8"))
                content = response.get("message", {}).get("content", "")
                if content:
                    return content.strip()
        except (error.URLError, error.HTTPError, TimeoutError, OSError, json.JSONDecodeError):
            pass
        return self._fallback_response(messages)
