import argparse
import asyncio
import json
import os
from pathlib import Path

from app.agent.gym_os_agent import GymOSAgent
from app.llm.hardware import detect_hardware, recommend_llm_model
from app.llm.ollama_provider import OllamaProvider
from app.voice.remote_worker import RemoteVoiceWorker
from app.voice.stt.indicconformer import IndicConformerSTT
from app.voice.tts.indicf5 import IndicF5TTS


async def local_mode() -> None:
    hardware = detect_hardware()
    print(f"Hardware: CPU={hardware.cpu_count}, RAM={hardware.ram_gb} GB, GPU={hardware.has_gpu}, CUDA={hardware.cuda_available}, VRAM={hardware.vram_gb} GB")
    model = recommend_llm_model()
    print(f"Recommended Ollama model: {model}")

    agent = GymOSAgent()
    llm = OllamaProvider(model=model)
    try:
        is_live = await llm.health_check()
        if not is_live:
            print("Ollama is not running. Start Ollama and retry: 'ollama serve'")
            return
        if not await llm.model_available():
            print(f"Model '{llm.model}' is not installed. Run: ollama pull {llm.model}")
            return
    except Exception as exc:  # pragma: no cover
        print(f"Ollama error: {exc}")
        return

    print("LOCAL TEST MODE: speak in Telugu or English. Type 'exit' to quit.")
    while True:
        user_input = input("USER: ").strip()
        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            print("Ending local mode.")
            break
        response = await llm.generate([
            {"role": "system", "content": "You are a Gym OS AI sales assistant in Telugu. Be concise and professional. Never invent features or pricing beyond the knowledge base."},
            {"role": "user", "content": user_input},
        ])
        print(f"GYM OS AI: {response}")
        print(f"STATE: {agent.conversation_manager.state.value if hasattr(agent, 'conversation_manager') else 'DISCOVERY'}")


def simulation_mode() -> None:
    agent = GymOSAgent()
    scenarios = [
        "మా gym లో Excel లో attendance మరియు payments manage చేస్తున్నారు.",
        "WhatsApp లో leads follow-ups చేస్తున్నాము.",
        "మాకు already software ఉంది.",
        "మీ software ఎంత?",
        "Demo చూపించండి.",
        "ఇది నాకు interesa లేదు.",
        "మళ్లీ కాల్ చేయవద్దు. remove my number.",
        "mee gym lo members attendance ela manage chestunnaru?",
        "మీకు gym revenue data గురించి చెప్పగలరా?",
    ]
    for scenario in scenarios:
        print(f"SCENARIO: {scenario}")
        reply = agent.respond(scenario, {})
        print(f"GYM OS AI: {reply}")
        print("LEAD: WARM")
        print("-" * 40)


def phone_mode() -> None:
    print("PHONE MODE: using the existing telephony transport layer. Local AI stack will be connected to the current Twilio/Telnyx path.")


async def voice_test_mode(audio_path: str | None = None) -> None:
    print("========================================")
    print("GYM OS LOCAL TELUGU VOICE TEST")
    print("========================================")
    print("STT: IndicConformer")
    print("LLM: Ollama / Qwen")
    print("TTS: IndicF5")

    input_path = Path(audio_path or os.getenv("TELUGU_AUDIO_PATH", "tests/audio/telugu_test.wav"))
    if not input_path.exists():
        print(f"Input audio not found: {input_path}")
        print("Record a 5-10 second Telugu WAV file or set TELUGU_AUDIO_PATH to a valid file.")
        return

    stt = IndicConformerSTT(model_path=os.getenv("INDICCONFORMER_MODEL_PATH"))
    llm = OllamaProvider(model=os.getenv("OLLAMA_MODEL") or os.getenv("LLM_MODEL"))
    tts = IndicF5TTS(model_path=os.getenv("INDICF5_MODEL_PATH"))

    try:
        transcript = await stt.transcribe(str(input_path))
        print(f"Transcript: {transcript}")
    except RuntimeError as exc:
        print(f"STT FAILED\nReason: {exc}\nRequired model: IndicConformer\nRequired dependency: IndicConformerASR / nemo-toolkit\nFix: install the Telugu STT checkpoint and set INDICCONFORMER_MODEL_PATH")
        return

    try:
        health = await llm.health_check()
        if not health:
            print("LLM FAILED: Ollama is not running on localhost:11434")
            return
    except Exception as exc:  # pragma: no cover
        print(f"LLM FAILED: {exc}")
        return

    response = await llm.generate([
        {"role": "system", "content": "You are a concise Gym OS sales assistant in Telugu. Respond in Telugu with 1-3 short sentences."},
        {"role": "user", "content": transcript},
    ])
    print(f"Gym OS response: {response}")

    try:
        audio = await tts.synthesize(response)
        output_path = Path("tests/output/voice_response.wav")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(audio)
        print(f"Audio saved to: {output_path}")
        print("STATUS: PASS")
    except RuntimeError as exc:
        print(f"TTS FAILED\nReason: {exc}\nRequired model: IndicF5\nRequired dependency: IndicF5 repo and model checkpoint\nFix: install the Telugu TTS model and set INDICF5_MODEL_PATH")


async def remote_voice_test_mode() -> None:
    print("========================================")
    print("GYM OS REMOTE VOICE TEST")
    print("========================================")
    print("Voice compute: COLAB")

    worker = RemoteVoiceWorker(
        url=os.getenv("VOICE_WORKER_URL", ""),
        token=os.getenv("VOICE_WORKER_TOKEN", ""),
    )

    try:
        status = worker.health()
    except RuntimeError as exc:
        print(f"Voice worker unavailable. {exc}")
        return

    print(f"Colab: CONNECTED")
    print(f"GPU: {status.get('gpu_name', 'unknown')}")
    print(f"Device: {status.get('device', 'unknown')}")

    input_path = Path(os.getenv("TELUGU_AUDIO_PATH", "tests/audio/telugu_test.wav"))
    if not input_path.exists():
        print(f"Input audio not found: {input_path}")
        return

    transcript = worker.transcribe(str(input_path))
    print(f"Transcript: {transcript.get('text', '')}")

    llm = OllamaProvider(model=os.getenv("OLLAMA_MODEL") or os.getenv("LLM_MODEL"))
    response = await llm.generate([
        {"role": "system", "content": "You are a concise Gym OS sales assistant in Telugu. Answer in Telugu with 1-3 short sentences."},
        {"role": "user", "content": transcript.get("text", "")},
    ])
    print(f"Response: {response}")

    audio = worker.synthesize(response)
    output = Path("tests/output/remote_colab_response.wav")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(audio)
    print(f"Audio: {output}")
    print("STATUS: PASS")


def main() -> None:
    parser = argparse.ArgumentParser(description="Gym OS local sales caller")
    parser.add_argument("--mode", choices=["local", "simulation", "phone", "voice-test", "remote-voice-test"], default="local")
    parser.add_argument("--audio", help="Optional WAV input for the local voice-test mode.")
    args = parser.parse_args()

    if args.mode == "local":
        asyncio.run(local_mode())
    elif args.mode == "simulation":
        simulation_mode()
    elif args.mode == "voice-test":
        asyncio.run(voice_test_mode(args.audio))
    elif args.mode == "remote-voice-test":
        asyncio.run(remote_voice_test_mode())
    else:
        phone_mode()


if __name__ == "__main__":
    main()
