# Installation Guide

## 1. Python version

Use Python 3.11 or 3.12 on Windows.

```powershell
python --version
```

## 2. Git

```powershell
git --version
```

## 3. FFmpeg

Install FFmpeg for audio processing.

```powershell
winget install Gyan.Dev.FFmpeg
```

## 4. Ollama installation

```powershell
winget install Ollama.Ollama
```

Then start Ollama:

```powershell
ollama serve
```

## 5. Local LLM download

Recommended starting model:

```powershell
ollama pull qwen2.5:3b-instruct
```

If GPU and VRAM are sufficient, use:

```powershell
ollama pull qwen2.5:7b-instruct
```

## 6. PyTorch installation

If CUDA is available:

```powershell
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

Otherwise:

```powershell
pip install torch
```

## 7. IndicConformer installation

Clone the repository and follow its local model instructions:

```powershell
git clone https://github.com/AI4Bharat/IndicConformerASR.git
```

Then configure the model path in `.env` with `INDICCONFORMER_MODEL_PATH`.

## 8. IndicF5 installation

```powershell
git clone https://github.com/AI4Bharat/IndicF5.git
```

Set `INDICF5_MODEL_PATH` and optionally `TTS_REFERENCE_AUDIO` in `.env`.

## 9. Audio dependencies

```powershell
pip install -r requirements.txt
```

## 10. Telephony setup

This remains optional for local testing. Twilio/Telnyx credentials are required only in phone mode.

## 11. Environment configuration

```powershell
copy .env.example .env
```

Then edit `.env` and set:

- `LLM_PROVIDER=ollama`
- `LLM_MODEL=qwen2.5:3b-instruct`
- `STT_PROVIDER=indicconformer`
- `TTS_PROVIDER=indicf5`
- `LOCAL_TEST_MODE=true`

## 12. Local microphone test

```powershell
python -m app.main --mode=local
```

## 13. Full agent test

```powershell
python -m app.main --mode=simulation
```

## 14. Phone test

```powershell
python -m app.main --mode=phone
```
