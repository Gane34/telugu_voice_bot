import os
import tempfile
from pathlib import Path

from app.voice.stt.base import STTProvider


class IndicConformerSTT(STTProvider):
    def __init__(self, model_path: str | None = None, device: str = "auto") -> None:
        self.model_path = model_path or os.getenv("INDICCONFORMER_MODEL_PATH")
        self.device = device or os.getenv("STT_DEVICE", "auto")
        self._model = None

    def _ensure_model(self):
        if not self.model_path:
            raise RuntimeError(
                "IndicConformer model is not configured. Download the Telugu checkpoint and set INDICCONFORMER_MODEL_PATH. "
                "Example: export INDICCONFORMER_MODEL_PATH=/path/to/indicconformer_stt_te_hybrid_rnnt_large.nemo"
            )
        if not os.path.exists(self.model_path):
            raise RuntimeError(f"IndicConformer model not found at {self.model_path}")

        try:
            import nemo.collections.asr  # noqa: F401
            from nemo.collections.asr.models import ASRModel
        except ImportError as exc:  # pragma: no cover - environment-dependent
            raise RuntimeError(
                "IndicConformer dependencies are missing. Install the requirements from IndicConformerASR/requirements.txt "
                "before using the Telugu STT model."
            ) from exc

        if self._model is None:
            self._model = ASRModel.restore_from(self.model_path, map_location=self.device)
        return self._model

    @staticmethod
    def _normalize_audio_input(audio):
        if isinstance(audio, (str, os.PathLike)):
            return str(audio)
        if isinstance(audio, (bytes, bytearray)):
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as handle:
                handle.write(audio)
                return handle.name
        raise TypeError("IndicConformerSTT expects a WAV file path or raw WAV bytes.")

    async def transcribe(self, audio) -> str:
        model = self._ensure_model()
        audio_path = self._normalize_audio_input(audio)

        try:
            result = model.transcribe([audio_path])
        except Exception as exc:  # pragma: no cover - backend-dependent
            raise RuntimeError(f"IndicConformer transcription failed for {audio_path}: {exc}") from exc

        if isinstance(result, list):
            if not result:
                raise RuntimeError("IndicConformer produced an empty transcript.")
            first = result[0]
            if isinstance(first, dict):
                text = first.get("text") or first.get("transcript") or ""
            else:
                text = str(first)
        elif isinstance(result, dict):
            text = result.get("text") or result.get("transcript") or ""
        else:
            text = str(result)

        if not text or not str(text).strip():
            raise RuntimeError("IndicConformer produced an empty transcript.")
        return str(text).strip()
