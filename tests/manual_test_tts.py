import argparse
import asyncio
import os
from pathlib import Path

from app.voice.remote_worker import RemoteVoiceWorker
from app.voice.tts.indicf5 import IndicF5TTS


async def main() -> None:
    parser = argparse.ArgumentParser(description="Telugu TTS test")
    parser.add_argument("--remote", action="store_true", help="Call the Colab voice worker instead of the local model")
    args = parser.parse_args()

    print("================================")
    print("TELUGU TTS TEST")
    print("================================")

    text = "నమస్కారం సార్. నేను Gym OS నుంచి AI assistant గా మాట్లాడుతున్నాను."

    if args.remote:
        worker = RemoteVoiceWorker(url=os.getenv("VOICE_WORKER_URL", ""), token=os.getenv("VOICE_WORKER_TOKEN", ""))
        output_path = Path("tests/output/colab_telugu_tts.wav")
        print("Provider: Colab / IndicF5")
        print(f"Input: {text}")
        print(f"Output: {output_path}")
        try:
            audio = worker.synthesize(text)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(audio)
            print("COLAB TTS")
            print("---------")
            print("Status: PASS")
            print(f"Output: {output_path}")
        except RuntimeError as exc:
            print("COLAB TTS")
            print("---------")
            print("Status: FAIL")
            print(f"Reason: {exc}")
        return

    provider = os.getenv("TTS_PROVIDER", "indicf5").lower()
    model_path = os.getenv("INDICF5_MODEL_PATH", "")
    output_path = Path("tests/output/telugu_test.wav")

    print(f"Provider: {provider}")
    print(f"Device: {os.getenv('TTS_DEVICE', 'auto')}")
    print(f"Model: {model_path or 'not configured'}")
    print(f"Input: {text}")
    print(f"Output: {output_path}")

    try:
        tts = IndicF5TTS(model_path=model_path)
        audio = await tts.synthesize(text)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(audio)
        print(f"Sample rate: {16000}")
        print("Status: PASS")
    except RuntimeError as exc:
        print("Status: FAIL")
        print(f"Reason: {exc}")
        print("Fix: download the IndicF5 Telugu checkpoint and set INDICF5_MODEL_PATH.")


if __name__ == "__main__":
    asyncio.run(main())
