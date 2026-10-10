import argparse
import asyncio
import os
from pathlib import Path

from app.voice.remote_worker import RemoteVoiceWorker
from app.voice.stt.indicconformer import IndicConformerSTT


async def main() -> None:
    parser = argparse.ArgumentParser(description="Telugu STT test")
    parser.add_argument("--remote", action="store_true", help="Call the Colab voice worker instead of the local model")
    args = parser.parse_args()

    print("================================")
    print("TELUGU STT TEST")
    print("================================")

    audio_path = Path(os.getenv("TELUGU_AUDIO_PATH", "tests/audio/telugu_test.wav"))
    provider = os.getenv("STT_PROVIDER", "indicconformer").lower()

    if args.remote:
        worker = RemoteVoiceWorker(url=os.getenv("VOICE_WORKER_URL", ""), token=os.getenv("VOICE_WORKER_TOKEN", ""))
        print("Provider: Colab / IndicConformer")
        print(f"Input: {audio_path}")
        if not audio_path.exists():
            print("Status: FAIL")
            print("Record a 5-10 second Telugu WAV file at tests/audio/telugu_test.wav before running this test.")
            return
        try:
            result = worker.transcribe(str(audio_path))
            print("COLAB STT")
            print("---------")
            print(f"Status: PASS")
            print(f"Transcript: {result.get('text', '')}")
        except RuntimeError as exc:
            print("COLAB STT")
            print("---------")
            print("Status: FAIL")
            print(f"Reason: {exc}")
        return

    model_path = os.getenv("INDICCONFORMER_MODEL_PATH", "")
    print(f"Provider: {provider}")
    print(f"Device: {os.getenv('STT_DEVICE', 'auto')}")
    print(f"Model: {model_path or 'not configured'}")
    print(f"Input: {audio_path}")

    if not audio_path.exists():
        print("Status: FAIL")
        print("Record a 5-10 second Telugu WAV file at tests/audio/telugu_test.wav before running this test.")
        return

    try:
        stt = IndicConformerSTT(model_path=model_path)
        transcript = await stt.transcribe(str(audio_path))
        print(f"Transcript: {transcript}")
        print("Status: PASS")
    except RuntimeError as exc:
        print(f"Status: FAIL")
        print(f"Reason: {exc}")
        print("Fix: download the IndicConformer Telugu checkpoint and set INDICCONFORMER_MODEL_PATH.")


if __name__ == "__main__":
    asyncio.run(main())
