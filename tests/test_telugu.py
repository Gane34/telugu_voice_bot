import pytest

from app.agent.gym_os_agent import normalize_telugu_text
from app.voice.stt.indicconformer import IndicConformerSTT
from app.voice.tts.indicf5 import IndicF5TTS


def test_telugu_normalization_handles_mixed_input():
    text = "mee gym lo members entha mandi unnaru? members attendance ela manage chestunnaru?"
    normalized = normalize_telugu_text(text)
    assert "members" in normalized.lower()
    assert "attendance" in normalized.lower()
    assert "gym" in normalized.lower()


def test_telugu_intro_is_readable():
    text = "నమస్కారం సార్. నేను Gym OS నుంచి AI assistant గా మాట్లాడుతున్నాను."
    normalized = normalize_telugu_text(text)
    assert "gym os" in normalized.lower()


def test_missing_indicconformer_model_raises_clear_error():
    stt = IndicConformerSTT(model_path="")
    with pytest.raises(RuntimeError, match="IndicConformer"):
        import asyncio
        asyncio.run(stt.transcribe(b"fake-audio"))


def test_missing_indicf5_model_raises_clear_error():
    tts = IndicF5TTS(model_path="")
    with pytest.raises(RuntimeError, match="IndicF5"):
        import asyncio
        asyncio.run(tts.synthesize("నమస్కారం సార్"))
