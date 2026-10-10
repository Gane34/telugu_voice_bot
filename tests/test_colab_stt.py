import os
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

    audio_path = Path(os.getenv("TELUGU_AUDIO_PATH", "tests/audio/telugu_test.wav"))
    if not audio_path.is_file():
        raise FileNotFoundError(
            f"Telugu WAV not found: {audio_path}. Set TELUGU_AUDIO_PATH to an existing WAV file."
        )

    with audio_path.open("rb") as audio_file:
        response = requests.post(
            f"{url}/stt",
            headers={"X-Voice-Worker-Token": token},
            files={"file": (audio_path.name, audio_file, "audio/wav")},
            timeout=300,
        )

    print(f"Status: {response.status_code}")
    response.raise_for_status()
    result = response.json()
    print(f"Language: {result.get('language', '')}")
    if "device" in result:
        print(f"Device: {result['device']}")
    print(f"Text: {result.get('text', '')}")


if __name__ == "__main__":
    main()