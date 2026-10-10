import os

from app.voice.tts.base import TTSProvider


class IndicTTSTTS(TTSProvider):
    def __init__(self, model_path: str | None = None, reference_audio: str | None = None) -> None:
        self.model_path = model_path or os.getenv("INDICTTS_MODEL_PATH")
        self.reference_audio = reference_audio or os.getenv("TTS_REFERENCE_AUDIO")

    async def synthesize(self, text: str) -> bytes:
        if not self.model_path:
            raise RuntimeError(
                "Indic-TTS model is not configured. Download the Telugu TTS checkpoint and set INDICTTS_MODEL_PATH."
            )
        if not os.path.exists(self.model_path):
            raise RuntimeError(f"Indic-TTS model not found at {self.model_path}")

        raise RuntimeError(
            "Indic-TTS fallback is configured but the model is not available in this environment. "
            "Use the IndicF5 provider instead, or install the required Indic-TTS checkpoint."
        )
