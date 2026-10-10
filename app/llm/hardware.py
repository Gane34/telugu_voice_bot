import os
from dataclasses import dataclass


try:
    import torch
except Exception:  # pragma: no cover
    torch = None


@dataclass
class HardwareInfo:
    cpu_count: int
    ram_gb: float
    has_gpu: bool
    cuda_available: bool
    vram_gb: float
    recommended_llm_model: str


def _detect_ram_gb() -> float:
    try:
        import psutil
    except Exception:
        return 8.0
    try:
        return round(psutil.virtual_memory().total / (1024 ** 3), 1)
    except Exception:
        return 8.0


def _detect_vram_gb() -> float:
    if torch is None:
        return 0.0
    if not torch.cuda.is_available():
        return 0.0
    try:
        total = 0.0
        for index in range(torch.cuda.device_count()):
            props = torch.cuda.get_device_properties(index)
            total += props.total_memory / (1024 ** 3)
        return round(total, 1)
    except Exception:
        return 0.0


def detect_hardware() -> HardwareInfo:
    ram_gb = _detect_ram_gb()
    has_gpu = False
    cuda_available = False
    vram_gb = 0.0
    if torch is not None:
        cuda_available = torch.cuda.is_available()
        has_gpu = cuda_available
        vram_gb = _detect_vram_gb()

    recommended = "qwen2.5:3b-instruct"
    if has_gpu and vram_gb >= 8:
        recommended = "qwen2.5:7b-instruct"
    elif ram_gb >= 24:
        recommended = "qwen2.5:7b-instruct"
    elif ram_gb >= 12:
        recommended = "qwen2.5:3b-instruct"
    return HardwareInfo(
        cpu_count=os.cpu_count() or 1,
        ram_gb=ram_gb,
        has_gpu=has_gpu,
        cuda_available=cuda_available,
        vram_gb=vram_gb,
        recommended_llm_model=os.getenv("LLM_MODEL", recommended),
    )


def recommend_llm_model() -> str:
    hw = detect_hardware()
    if hw.has_gpu and hw.vram_gb >= 8:
        return "qwen2.5:7b-instruct"
    if hw.ram_gb >= 16:
        return "qwen2.5:3b-instruct"
    return "qwen2.5:1.5b-instruct"
