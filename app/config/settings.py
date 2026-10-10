import os
from dataclasses import dataclass


@dataclass
class Settings:
    app_env: str = "development"
    llm_provider: str = "ollama"
    llm_model: str = "qwen2.5:7b-instruct"
    stt_provider: str = "indicconformer"
    tts_provider: str = "indicf5"
    voice_compute: str = "local"
    voice_worker_url: str = ""
    voice_worker_token: str = ""
    local_test_mode: bool = True
    log_level: str = "INFO"
    database_url: str = "sqlite:///data/gym_os.db"

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            app_env=os.getenv("APP_ENV", "development"),
            llm_provider=os.getenv("LLM_PROVIDER", "ollama").lower(),
            llm_model=os.getenv("LLM_MODEL", "qwen2.5:7b-instruct"),
            stt_provider=os.getenv("STT_PROVIDER", "indicconformer").lower(),
            tts_provider=os.getenv("TTS_PROVIDER", "indicf5").lower(),
            voice_compute=os.getenv("VOICE_COMPUTE", "local").lower(),
            voice_worker_url=os.getenv("VOICE_WORKER_URL", ""),
            voice_worker_token=os.getenv("VOICE_WORKER_TOKEN", ""),
            local_test_mode=os.getenv("LOCAL_TEST_MODE", "true").lower() == "true",
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
            database_url=os.getenv("DATABASE_URL", "sqlite:///data/gym_os.db"),
        )


SETTINGS = Settings.from_env()
