# %% [markdown]
# # Gym OS Colab IndicConformer STT Worker
# 
# This notebook runs Telugu IndicConformer speech-to-text on the Colab GPU while Gym OS business logic and Ollama/Qwen remain local.
# 
# Before deploying the FastAPI worker, use **Runtime → Restart session** in Colab to clear stale app objects and Uvicorn threads. Then execute only the worker dependency, application, startup, and local verification cells listed at the bottom. Do not run the direct transcription or `/stt` cells for the upload-route deployment check.

# %%
!nvidia-smi

import sys
import torch

print('Python version:', sys.version)
print('PyTorch:', torch.__version__)
print('CUDA available:', torch.cuda.is_available())
if torch.cuda.is_available():
    print('GPU:', torch.cuda.get_device_name(0))
else:
    raise RuntimeError('CUDA is unavailable. Stop here and select a Colab GPU runtime.')

# %%
from pathlib import Path

nemo_path = Path('/content/NeMo')
if not nemo_path.exists():
    !git clone --depth 1 --branch nemo-v2 https://github.com/AI4Bharat/NeMo.git /content/NeMo

%cd /content/NeMo
!bash reinstall.sh
%cd /content

from importlib.metadata import version
print('NeMo toolkit:', version('nemo_toolkit'))
print('PyTorch:', __import__('torch').__version__)

# %%
import os
from pathlib import Path

MODEL_FILENAME = 'indicconformer_stt_te_hybrid_rnnt_large.nemo'
configured_path = os.getenv('INDICCONFORMER_MODEL_PATH')
if configured_path:
    MODEL_PATH = Path(configured_path).expanduser()
else:
    known_paths = [
        Path('/content/models') / MODEL_FILENAME,
        Path('/content/IndicConformerASR') / MODEL_FILENAME,
    ]
    matches = [path for path in known_paths if path.is_file()]
    if not matches:
        matches = list(Path('/content').rglob(MODEL_FILENAME))
    if not matches:
        raise FileNotFoundError(
            f'{MODEL_FILENAME} was not found under /content. Set INDICCONFORMER_MODEL_PATH to the existing checkpoint.'
        )
    MODEL_PATH = matches[0]
    os.environ['INDICCONFORMER_MODEL_PATH'] = str(MODEL_PATH)

if not MODEL_PATH.is_file():
    raise FileNotFoundError(f'INDICCONFORMER_MODEL_PATH does not exist: {MODEL_PATH}')
print('IndicConformer checkpoint:', MODEL_PATH)

# %%
import os
import time

import torch

DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
asr_model = None
model_load_error = None
try:
    from nemo.collections.asr.models.hybrid_rnnt_ctc_bpe_models import EncDecHybridRNNTCTCBPEModel

    asr_model = EncDecHybridRNNTCTCBPEModel.restore_from(
        str(MODEL_PATH), map_location=torch.device(DEVICE)
    )
    asr_model = asr_model.to(DEVICE)
    asr_model.eval()
except Exception as exc:
    model_load_error = exc
    print(f'IndicConformer model load failed: {exc}')


def transcribe_telugu(audio_path):
    if asr_model is None:
        raise RuntimeError(f'IndicConformer model is not loaded: {model_load_error}') from model_load_error
    start = time.time()
    results = asr_model.transcribe([str(audio_path)])
    if not results:
        raise RuntimeError('IndicConformer returned no transcription result.')
    first = results[0]
    text = first.get('text', '') if isinstance(first, dict) else str(first)
    if not text or not text.strip():
        raise RuntimeError('IndicConformer produced an empty transcript.')
    return {
        'text': text.strip(),
        'language': 'te',
        'device': DEVICE,
        'model': MODEL_PATH.name,
        'latency_seconds': round(time.time() - start, 3),
    }

print('Loaded model:', type(asr_model).__name__ if asr_model is not None else 'not loaded')
print('Device:', DEVICE)
print('Model file:', MODEL_PATH)
print('Python:', __import__('sys').version)
print('PyTorch:', torch.__version__)
from importlib.metadata import version
print('NeMo toolkit:', version('nemo_toolkit'))

# %%
import os
from pathlib import Path

TEST_WAV = Path(os.getenv('TELUGU_AUDIO_PATH', '/content/sample_telugu.wav'))
if not TEST_WAV.is_file():
    raise FileNotFoundError(
        f'Telugu WAV not found: {TEST_WAV}. Upload a WAV and set TELUGU_AUDIO_PATH to its path.'
    )

direct_result = transcribe_telugu(TEST_WAV)
print('Direct model transcription succeeded')
print('Language:', direct_result['language'])
print('Device:', direct_result['device'])
print('Text:', direct_result['text'])

# %%
# Install the FastAPI worker dependencies in this Colab runtime.
%pip install --quiet fastapi uvicorn python-multipart requests

# %%
import hmac
import io
import os
import tempfile
import wave
from pathlib import Path

import torch
from fastapi import FastAPI, File, Header, HTTPException, UploadFile

MAX_AUDIO_BYTES = 25 * 1024 * 1024
DEVICE = globals().get('DEVICE') or ('cuda' if torch.cuda.is_available() else 'cpu')
asr_model = globals().get('asr_model')
app = FastAPI(title='Gym OS IndicConformer STT Worker')


def require_worker_token(token: str | None) -> None:
    expected = os.getenv('VOICE_WORKER_TOKEN', '')
    if not expected:
        raise HTTPException(status_code=500, detail='Worker authentication is not configured.')
    if not token or not hmac.compare_digest(token, expected):
        raise HTTPException(status_code=401, detail='Invalid worker token.')


async def save_valid_wav(file: UploadFile):
    if not file.filename:
        raise HTTPException(status_code=400, detail='Audio file is required.')

    content = await file.read(MAX_AUDIO_BYTES + 1)
    if not content or len(content) > MAX_AUDIO_BYTES:
        raise HTTPException(status_code=400, detail='Audio is empty or exceeds the 25 MB limit.')

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_file.write(content)
            temp_path = Path(temp_file.name)

        try:
            with wave.open(str(temp_path), 'rb') as wav_file:
                metadata = {
                    'bytes': len(content),
                    'channels': wav_file.getnchannels(),
                    'sample_rate': wav_file.getframerate(),
                    'frames': wav_file.getnframes(),
                }
        except (wave.Error, EOFError) as exc:
            raise HTTPException(status_code=400, detail='Uploaded file is not a valid WAV audio file.') from exc

        if metadata['frames'] < 1:
            raise HTTPException(status_code=400, detail='WAV contains no audio frames.')
        if metadata['sample_rate'] != 16000:
            raise HTTPException(status_code=400, detail='IndicConformer requires 16 kHz WAV audio.')
        if metadata['channels'] != 1:
            raise HTTPException(status_code=400, detail='IndicConformer requires mono WAV audio.')
        return temp_path, metadata
    except Exception:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
        raise


@app.get('/health')
async def health(x_voice_worker_token: str | None = Header(default=None)):
    require_worker_token(x_voice_worker_token)
    gpu_available = torch.cuda.is_available()
    gpu_name = torch.cuda.get_device_name(0) if gpu_available else None
    return {
        'status': 'ok',
        'gpu': gpu_available,
        'gpu_name': gpu_name,
        'device': DEVICE,
        'stt_model_loaded': asr_model is not None,
    }


@app.get('/upload-test-ping')
async def upload_test_ping(x_voice_worker_token: str | None = Header(default=None)):
    require_worker_token(x_voice_worker_token)
    return {'status': 'ok'}


@app.post('/upload-test')
async def upload_test(
    file: UploadFile = File(...),
    x_voice_worker_token: str | None = Header(default=None),
):
    print('UPLOAD_TEST: request received', flush=True)
    require_worker_token(x_voice_worker_token)
    print('UPLOAD_TEST: authentication passed', flush=True)
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail='Audio file is required.')
        print('UPLOAD_TEST: file received', flush=True)
        content = await file.read(MAX_AUDIO_BYTES + 1)
        print(f'UPLOAD_TEST: bytes={len(content)}', flush=True)
        if not content or len(content) > MAX_AUDIO_BYTES:
            raise HTTPException(status_code=400, detail='Audio is empty or exceeds the 25 MB limit.')
        try:
            with wave.open(io.BytesIO(content), 'rb') as wav_file:
                if wav_file.getnframes() < 1:
                    raise HTTPException(status_code=400, detail='WAV contains no audio frames.')
        except (wave.Error, EOFError) as exc:
            raise HTTPException(status_code=400, detail='Uploaded file is not a valid WAV audio file.') from exc
        print('UPLOAD_TEST: returning 200', flush=True)
        return {
            'status': 'ok',
            'filename': file.filename,
            'bytes': len(content),
        }
    finally:
        await file.close()


@app.post('/stt')
async def stt_route(
    file: UploadFile = File(...),
    x_voice_worker_token: str | None = Header(default=None),
):
    require_worker_token(x_voice_worker_token)
    temp_path = None
    try:
        temp_path, _metadata = await save_valid_wav(file)
        if asr_model is None:
            raise HTTPException(status_code=500, detail='STT model is not loaded.')
        result = transcribe_telugu(temp_path)
        return {
            'text': result['text'],
            'language': 'te',
            'device': DEVICE,
            'model': MODEL_PATH.name,
        }
    except HTTPException:
        raise
    except Exception as exc:
        print(f'STT transcription failed ({type(exc).__name__}).')
        raise HTTPException(status_code=500, detail='Transcription failed.') from exc
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
        await file.close()


print('REGISTERED ROUTES:')
for route in app.routes:
    print(route.path, sorted(route.methods or []))

# %%
import threading
import uvicorn

existing_thread = globals().get('server_thread')
if existing_thread is not None and existing_thread.is_alive():
    raise RuntimeError('A tracked worker is already running. Restart the Colab session before deploying.')

server = uvicorn.Server(
    uvicorn.Config(app, host='0.0.0.0', port=8000, workers=1, log_level='info')
)
server_thread = threading.Thread(target=server.run, daemon=True)
server_thread.start()
server_thread.join(timeout=2)
if not server_thread.is_alive():
    raise RuntimeError('FastAPI worker failed to start on port 8000; inspect the server output.')
print('Started the current FastAPI app on 0.0.0.0:8000 with one Uvicorn worker.')

# %%
import os
import requests

worker_token = os.getenv('VOICE_WORKER_TOKEN', '')
if not worker_token:
    raise RuntimeError('Set the existing VOICE_WORKER_TOKEN in the Colab environment; do not print it.')


def verify_local_route(path: str) -> None:
    response = requests.get(
        f'http://127.0.0.1:8000{path}',
        headers={'X-Voice-Worker-Token': worker_token},
        timeout=30,
    )
    print(f'LOCAL {path} → {response.status_code}')
    if response.status_code == 404:
        raise RuntimeError('DEPLOYMENT ERROR: current Uvicorn process is not serving the current FastAPI app.')
    response.raise_for_status()
    if response.status_code != 200:
        raise RuntimeError(f'Local route check failed for {path}: HTTP {response.status_code}')
    if path == '/upload-test-ping' and response.json() != {'status': 'ok'}:
        raise RuntimeError('Local upload-test-ping returned an unexpected response.')


verify_local_route('/health')
verify_local_route('/upload-test-ping')

# %%
with TEST_WAV.open('rb') as audio_file:
    stt_response = requests.post(
        'http://127.0.0.1:8000/stt',
        headers={'X-Voice-Worker-Token': worker_token},
        files={'file': (TEST_WAV.name, audio_file, 'audio/wav')},
        timeout=300,
    )
print('STT HTTP status:', stt_response.status_code)
stt_response.raise_for_status()
stt_result = stt_response.json()
print('Language:', stt_result.get('language'))
print('Device:', stt_result.get('device'))
print('Text:', stt_result.get('text'))

# %% [markdown]
# ## Clean Runtime Deployment
# 
# 1. In Colab select **Runtime → Restart session**. This is required to clear the stale FastAPI app and worker; the notebook does not kill arbitrary processes.
# 2. Make the existing `VOICE_WORKER_TOKEN` available in the Colab runtime without printing it.
# 3. Execute only cells 7 through 10, in order:
#    - Cell 7 installs the FastAPI worker dependencies.
#    - Cell 8 creates the single FastAPI `app`, registers `/health`, `/upload-test-ping`, `/upload-test`, and `/stt`, then prints `REGISTERED ROUTES`.
#    - Cell 9 starts one Uvicorn worker from that `app` on `0.0.0.0:8000`. It refuses to start if a tracked worker is already alive.
#    - Cell 10 calls local authenticated `/health` and `/upload-test-ping`. Continue only when both print HTTP 200.
# 
# No notebook cell creates an ngrok tunnel. Leave the existing tunnel configuration unchanged and ensure its forward target is port 8000. Do not run the direct-transcription or `/stt` cells during this deployment check.


