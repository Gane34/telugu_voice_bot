# Architecture

This repository still preserves the existing Pipecat + FastAPI outbound phone-calling server, but the AI decision layer is being converted to a local, open-source Gym OS sales flow.

## Request flow

PHONE -> Pipecat transport -> STT -> local LLM -> TTS -> PHONE

The business workflow is intentionally controlled by the application state machine, not by the LLM. The LLM is responsible for natural speech, while the application enforces the sales policy.

## Current repository layout

- server/server.py: FastAPI API and Twilio webhook endpoints.
- server/bot.py: Pipecat voice pipeline for Twilio media streams.
- app/agent: Gym OS sales logic and state machine.
- app/llm: provider interfaces and local LLM runtimes.
- app/voice: STT/TTS provider interfaces and local implementations.
- app/telephony: abstraction around the phone transport.
- app/knowledge: verified product knowledge for Gym OS.
- data: corpus and lead storage.

## AI stack

- STT: IndicConformer preferred; Whisper fallback.
- LLM: Ollama with local Qwen Instruct model.
- TTS: IndicF5 preferred; Indic-TTS fallback.
- Telephony: Twilio or Telnyx remains transport only.

## Design rule

Open-source/local AI components are required where technically feasible. Proprietary telecom transport remains optional and separate from the AI logic.
