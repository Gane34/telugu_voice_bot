import os

from app.voice.tts.base import TTSProvider


class IndicF5TTS(TTSProvider):
    def __init__(self, model_path: str | None = None, reference_audio: str | None = None) -> None:
        self.model_path = model_path or os.getenv("INDICF5_MODEL_PATH")
        self.reference_audio = reference_audio or os.getenv("TTS_REFERENCE_AUDIO")
        self._model = None

    def _ensure_model(self):
        if not self.model_path:
            raise RuntimeError(
                "IndicF5 model is not configured. Download the Telugu checkpoint and set INDICF5_MODEL_PATH. "
                "Example: export INDICF5_MODEL_PATH=/path/to/indicf5-te"
            )
        if not os.path.exists(self.model_path):
            raise RuntimeError(f"IndicF5 model not found at {self.model_path}")

        try:
            from f5_tts.api import F5TTS
        except ImportError as exc:  # pragma: no cover - environment-dependent
            raise RuntimeError(
                "IndicF5 dependencies are missing. Install the repo under IndicF5/ and ensure the `f5_tts` package is importable."
            ) from exc

        if self._model is None:
            self._model = F5TTS(model_path=self.model_path)
        return self._model

    async def synthesize(self, text: str) -> bytes:
        if not text or not str(text).strip():
            raise ValueError("IndicF5TTS requires a non-empty Telugu text prompt.")

        model = self._ensure_model()
        try:
            wav = model.synthesize(str(text).strip())
        except Exception as exc:  # pragma: no cover - backend-dependent
            raise RuntimeError(f"IndicF5 synthesis failed for text: {text[:80]} ... {exc}") from exc

        if isinstance(wav, (bytes, bytearray)):
            return bytes(wav)
        if hasattr(wav, "read"):
            return wav.read()

        raise RuntimeError("IndicF5 synthesis returned an unsupported payload type.")
