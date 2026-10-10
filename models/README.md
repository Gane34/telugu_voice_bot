# Model Registry

This project is designed to use local models where possible.

## Recommended local LLM

- Model: Qwen2.5 Instruct
- Source: Ollama registry
- License: open-weight; check current model card
- Approximate size: 1.5B to 7B parameters
- RAM: 8 GB minimum for 3B, 16 GB recommended for 7B
- VRAM: 8 GB recommended for 7B GPU use
- Telugu support: yes, via multilingual instruct tuning
- Install: `ollama pull qwen2.5:3b-instruct`

## Recommended STT

- Model: AI4Bharat IndicConformer
- Source: AI4Bharat repository
- License: check upstream licensing before deployment
- Approximate size: varies by checkpoint
- RAM/VRAM: depends on checkpoint and runtime
- Telugu support: strong

## Recommended TTS

- Model: AI4Bharat IndicF5
- Source: AI4Bharat repository
- License: check upstream licensing before deployment
- Approximate size: varies by checkpoint
- Telugu support: strong
