import pytest

from app.voice import remote_worker
from app.voice.remote_worker import RemoteVoiceWorker


def test_remote_worker_requires_url():
    worker = RemoteVoiceWorker(url="", token="")
    with pytest.raises(RuntimeError, match="VOICE_WORKER_URL"):
        worker.health()


def test_remote_worker_requires_token_for_auth():
    worker = RemoteVoiceWorker(url="https://example.com", token="")
    with pytest.raises(RuntimeError, match="VOICE_WORKER_TOKEN"):
        worker.health()


def test_transcribe_sends_authenticated_multipart(monkeypatch):
    captured = {}

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def read(self):
            return b'{"text":"నమస్కారం","language":"te"}'

    def fake_urlopen(req, timeout):
        captured["request"] = req
        captured["timeout"] = timeout
        return Response()

    monkeypatch.setattr(remote_worker.request, "urlopen", fake_urlopen)
    worker = RemoteVoiceWorker(url="https://example.com", token="test-token")

    result = worker.transcribe(b"RIFF-test-wav")

    headers = {key.lower(): value for key, value in captured["request"].header_items()}
    assert headers["x-voice-worker-token"] == "test-token"
    assert headers["content-type"].startswith("multipart/form-data; boundary=")
    assert b'name="file"; filename="audio.wav"' in captured["request"].data
    assert b"RIFF-test-wav" in captured["request"].data
    assert result == {"text": "నమస్కారం", "language": "te"}
