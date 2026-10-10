# Local Telugu Test

## 1. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

## 2. Install Ollama

```powershell
winget install Ollama.Ollama
```

## 3. Download model

```powershell
ollama pull qwen2.5:3b-instruct
```

## 4. Configure .env

```powershell
copy .env.example .env
```

Example values:

```env
LOCAL_TEST_MODE=true
LLM_PROVIDER=ollama
LLM_MODEL=qwen2.5:3b-instruct
STT_PROVIDER=indicconformer
TTS_PROVIDER=indicf5
```

## 5. Run local test

```powershell
python -m app.main --mode=local
```

## 6. Test sample prompts

- నమస్కారం
- మీ gym members attendance ఎలా manage చేస్తున్నారు?
- Gym OS ఎంత?
- Demo కావాలా?
- మళ్లీ కాల్ చేయవద్దు
