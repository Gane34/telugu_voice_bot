import os
import tempfile

from app.voice.stt.base import STTProvider


class WhisperSTT(STTProvider):
    def __init__(self, model: str = "small", device: str = "auto") -> None:
        self.model = model or os.getenv("WHISPER_MODEL", "small")
        self.device = device or os.getenv("STT_DEVICE", "auto")
        self._model = None

    def _ensure_model(self):
        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:  # pragma: no cover - environment-dependent
            raise RuntimeError(
                "Whisper fallback is unavailable because faster-whisper is not installed. "
                "Install faster-whisper and ffmpeg to use the STT fallback."
            ) from exc

        if self._model is None:
            selected_device = "cuda" if self.device == "auto" and os.name != "nt" else "cpu"
            self._model = WhisperModel(self.model, device=selected_device, compute_type="int8")
        return self._model

    @staticmethod
    def _normalize_audio_input(audio):
        if isinstance(audio, (str, os.PathLike)):
            return str(audio)
        if isinstance(audio, (bytes, bytearray)):
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as handle:
                handle.write(audio)
                return handle.name
        raise TypeError("WhisperSTT expects a WAV file path or raw WAV bytes.")

    async def transcribe(self, audio) -> str:
        model = self._ensure_model()
        audio_path = self._normalize_audio_input(audio)

        try:
            segments, _ = model.transcribe(audio_path, language="te")
            transcript = " ".join(segment.text.strip() for segment in segments if segment.text and segment.text.strip())
        except Exception as exc:  # pragma: no cover - backend-dependent
            raise RuntimeError(f"Whisper transcription failed for {audio_path}: {exc}") from exc

        if not transcript:
            raise RuntimeError("Whisper produced an empty transcript.")
        return transcript.strip()
