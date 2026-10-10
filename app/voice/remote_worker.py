import json
import os
import secrets
from pathlib import Path
from typing import Any
from urllib import error, request


class RemoteVoiceWorker:
    """Simple HTTPS client for a remote Colab GPU voice-processing worker."""

    def __init__(self, url: str | None = None, token: str | None = None, timeout: int = 30) -> None:
        self.url = (url or os.getenv("VOICE_WORKER_URL", "")).rstrip("/")
        self.token = token or os.getenv("VOICE_WORKER_TOKEN", "")
        self.timeout = timeout

    def _require_config(self) -> None:
        if not self.url:
            raise RuntimeError(
                "VOICE_WORKER_URL is not configured. Set the Colab worker URL before calling the remote voice worker."
            )
        if not self.token:
            raise RuntimeError(
                "VOICE_WORKER_TOKEN is not configured. Add the bearer token for the Colab voice worker."
            )

    def _headers(self, extra: dict[str, str] | None = None) -> dict[str, str]:
        headers = {"X-Voice-Worker-Token": self.token}
        if extra:
            headers.update(extra)
        return headers

    def _request_json(self, method: str, path: str, payload: dict[str, Any] | None = None, content_type: str | None = None) -> Any:
        self._require_config()
        body = None
        headers = self._headers()
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = content_type or "application/json"
        req = request.Request(f"{self.url}{path}", data=body, headers=headers, method=method)
        try:
            with request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read()
                if not raw:
                    return {}
                try:
                    return json.loads(raw.decode("utf-8"))
                except json.JSONDecodeError:
                    return raw
        except (error.URLError, error.HTTPError, TimeoutError, OSError) as exc:
            raise RuntimeError(f"Voice worker unavailable. Start the Colab runtime and verify the worker URL. Details: {exc}") from exc

    def _request_multipart(self, method: str, path: str, payload: bytes) -> dict[str, Any]:
        self._require_config()
        boundary = f"GymOSBoundary{secrets.token_hex(16)}"
        body = (
            f"--{boundary}\r\n"
            'Content-Disposition: form-data; name="file"; filename="audio.wav"\r\n'
            "Content-Type: audio/wav\r\n\r\n"
        ).encode("ascii") + payload + f"\r\n--{boundary}--\r\n".encode("ascii")
        headers = self._headers({"Content-Type": f"multipart/form-data; boundary={boundary}"})
        req = request.Request(f"{self.url}{path}", data=body, headers=headers, method=method)
        try:
            with request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read()
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Voice worker returned HTTP {exc.code}: {detail}") from exc
        except (error.URLError, TimeoutError, OSError) as exc:
            raise RuntimeError(f"Voice worker unavailable. Start the Colab runtime and verify the worker URL. Details: {exc}") from exc
        try:
            result = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RuntimeError("Remote STT returned invalid JSON.") from exc
        if not isinstance(result, dict):
            raise RuntimeError("Remote STT returned an unexpected response.")
        return result

    def health(self) -> dict[str, Any]:
        return self._request_json("GET", "/health")

    def transcribe(self, audio_path: str | os.PathLike[str] | bytes | bytearray) -> dict[str, Any]:
        if isinstance(audio_path, (bytes, bytearray)):
            return self._request_multipart("POST", "/stt", bytes(audio_path))

        if isinstance(audio_path, (str, os.PathLike)):
            source = Path(audio_path)
            if not source.exists():
                raise FileNotFoundError(f"Audio file not found: {source}")
            return self._request_multipart("POST", "/stt", source.read_bytes())

        raise TypeError("RemoteVoiceWorker.transcribe expects a WAV file path, bytes, or bytearray input.")

    def synthesize(self, text: str) -> bytes:
        result = self._request_json("POST", "/tts", payload={"text": text}, content_type="application/json")
        if isinstance(result, (bytes, bytearray)):
            return bytes(result)
        if isinstance(result, dict):
            if "audio" in result and isinstance(result["audio"], (bytes, bytearray)):
                return bytes(result["audio"])
            if "audio_path" in result:
                path = Path(result["audio_path"])
                if path.exists():
                    return path.read_bytes()
        raise RuntimeError("Remote TTS did not return a valid WAV payload.")
