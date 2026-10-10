# Google Colab IndicConformer STT Worker

This stage runs only Telugu IndicConformer speech-to-text on a Google Colab GPU. Gym OS business logic and Ollama/Qwen remain on the Windows machine.

## Architecture

- Local Windows laptop: Gym OS business logic, prompt orchestration, Ollama/Qwen, app control
- Google Colab: Telugu IndicConformer STT on GPU
- Local client: authenticated HTTPS calls to the remote worker

## Recommended runtime

1. Open Google Colab.
2. Runtime → Change runtime type → GPU.
3. Verify CUDA is available in the first notebook cell.

## Notebook

The notebook is in `notebooks/gym_os_voice_worker.ipynb`.

## Colab notebook and verification order

Run `notebooks/gym_os_voice_worker.ipynb` from top to bottom and stop on the first failure:

1. Confirm the GPU with `nvidia-smi`.
2. Confirm `torch.cuda.is_available()` and record Python/PyTorch versions.
3. Locate the existing Telugu `.nemo` checkpoint. The notebook uses `INDICCONFORMER_MODEL_PATH` when set; otherwise it searches the known checkpoint locations under `/content` and fails if none exists. It does not download another checkpoint.
4. Install AI4Bharat NeMo using the IndicConformer repository's documented `nemo-v2` checkout and `bash reinstall.sh` procedure. Record the resulting `nemo_toolkit` and PyTorch versions.
5. Restore the checkpoint as `nemo.collections.asr.models.hybrid_rnnt_ctc_bpe_models.EncDecHybridRNNTCTCBPEModel` and run its `transcribe([audio_path])` API on a 16 kHz mono Telugu WAV.
6. Only after direct transcription succeeds, start the FastAPI worker.
7. Verify authenticated `GET /health`, including `gpu`, `gpu_name`, and `stt_model_loaded`.
8. Verify authenticated multipart `POST /stt`.
9. From the Windows project root, run `python tests/test_colab_stt.py`.

The checkpoint embeds a 16 kHz `EncDecHybridRNNTCTCBPEModel` configuration. The local notebook prints the actual Python, PyTorch, NeMo, model path, and GPU details at runtime. This guide does not prescribe speculative package version pins.

## Environment variables

Set these values in the Colab environment:

```bash
VOICE_WORKER_TOKEN=your_secure_token
```

If the checkpoint is not found automatically, set `INDICCONFORMER_MODEL_PATH` in the Colab runtime to the actual existing `.nemo` file path. Do not set it to a placeholder.

On the Windows laptop, add to `.env`:

```env
VOICE_COMPUTE=colab
VOICE_WORKER_URL=https://your-existing-tunnel-url
VOICE_WORKER_TOKEN=your_secure_token
```

## Health check

```bash
curl -H "X-Voice-Worker-Token: $VOICE_WORKER_TOKEN" "$VOICE_WORKER_URL/health"
```

`POST /stt` accepts multipart form data in the `file` field. It only accepts valid mono 16 kHz WAV audio up to 25 MB, writes it to a unique temporary file, and removes the file after transcription. Responses contain Telugu text, `language: "te"`, and GPU/model diagnostics.

## Local test

```bash
python -m app.main --mode=remote-voice-test
```

This expects a valid `VOICE_WORKER_URL`, `VOICE_WORKER_TOKEN`, and Telugu WAV file. Set `TELUGU_AUDIO_PATH` if the file is not at `tests/audio/telugu_test.wav`.

## Important notes

- Keep using the existing tunnel/network configuration; Colab may disconnect or its public URL may change.
- Colab is appropriate for development and experimentation; it is not yet a production telephony endpoint.
- Do not expose the worker publicly without a token or a restricted tunnel.
- Do not move the verified Ollama/Qwen business logic to Colab; keep it local.
