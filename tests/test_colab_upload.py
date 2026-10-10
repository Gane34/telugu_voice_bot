import os
import wave
from pathlib import Path

import requests
from dotenv import load_dotenv


def main() -> None:
    load_dotenv()
    url = os.getenv("VOICE_WORKER_URL", "").rstrip("/")
    token = os.getenv("VOICE_WORKER_TOKEN", "")
    if not url:
        raise RuntimeError("VOICE_WORKER_URL is missing in .env")
    if not token:
        raise RuntimeError("VOICE_WORKER_TOKEN is missing in .env")

    audio_path = Path("tests/audio/telugu_test.wav")
    if not audio_path.is_file():
        raise FileNotFoundError(f"Telugu WAV not found: {audio_path}")

    file_size = audio_path.stat().st_size
    with wave.open(str(audio_path), "rb") as wav_file:
        print(f"Channels: {wav_file.getnchannels()}")
        print(f"Sample rate: {wav_file.getframerate()}")
        print(f"Sample width: {wav_file.getsampwidth()}")
        print(f"Duration: {wav_file.getnframes() / wav_file.getframerate():.2f} sec")
    print(f"File size: {file_size} bytes")

    try:
        with audio_path.open("rb") as audio_file:
            response = requests.post(
                f"{url}/upload-test",
                headers={"X-Voice-Worker-Token": token},
                files={"file": (audio_path.name, audio_file, "audio/wav")},
                timeout=120,
            )
    except requests.exceptions.RequestException as exc:
        print(f"Classification: HTTP/network failure ({type(exc).__name__})")
        raise SystemExit(1) from exc

    print(f"Status: {response.status_code}")
    try:
        result = response.json()
    except requests.exceptions.JSONDecodeError:
        print(f"Response: {response.text}")
        if response.status_code == 404:
            print("Classification: route 404")
        elif response.status_code in (401, 403):
            print("Classification: authentication failure")
        else:
            print("Classification: upload failure (non-JSON response)")
        raise SystemExit(1)
    print(f"Response: {result}")
    if response.status_code == 404:
        print("Classification: route 404")
        raise SystemExit(1)
    if response.status_code in (401, 403):
        print("Classification: authentication failure")
        raise SystemExit(1)
    if not response.ok:
        print("Classification: upload failure")
        raise SystemExit(1)
    if (
        set(result) != {"status", "filename", "bytes"}
        or result.get("status") != "ok"
        or result.get("filename") != audio_path.name
        or result.get("bytes") != file_size
    ):
        print("Classification: upload failure (unexpected response)")
        raise SystemExit(1)
    print("Classification: successful upload")


if __name__ == "__main__":
    main()