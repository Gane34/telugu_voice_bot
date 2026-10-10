# Gym OS Migration Plan

## Scope

This migration updates the existing outbound caller into a local-led Gym OS sales voice assistant without throwing away the working telephony code.

## Files retained

- server/server.py
- server/bot.py
- server/docker-compose.yml
- server/Dockerfile
- server/requirements.txt
- scripts/*

These files remain in place because they already define the transport and call infrastructure.

## Files modified

- app/agent/gym_os_agent.py
- app/agent/conversation_manager.py
- app/agent/lead_qualifier.py
- app/agent/safety.py
- app/llm/ollama_provider.py
- app/llm/hardware.py
- app/voice/stt/base.py
- app/voice/stt/indicconformer.py
- app/voice/stt/whisper.py
- app/voice/tts/base.py
- app/voice/tts/indicf5.py
- app/voice/tts/indic_tts.py
- app/telephony/base.py
- app/telephony/current_provider.py
- app/config/settings.py
- .env.example
- requirements.txt

## Files created

- app/main.py
- app/knowledge/gym_os_knowledge.json
- app/llm/base.py
- app/llm/llama_cpp_provider.py
- app/agent/conversation_manager.py
- docs/ARCHITECTURE.md
- docs/GYM_OS_MIGRATION.md
- docs/INSTALLATION.md
- docs/LOCAL_TELUGU_TEST.md
- docs/PHONE_MODE.md
- docs/OPEN_SOURCE_AUDIT.md
- models/README.md

## Migration strategy

1. Keep the current Twilio/Telnyx layer intact for outbound calls.
2. Remove mandatory third-party AI dependencies from the core flow.
3. Replace default LLM/STT/TTS with local providers.
4. Add the Gym OS knowledge file as the single source of truth for product claims.
5. Enforce state-machine-driven sales flow.
6. Keep local microphone mode for testing without phone calls.
