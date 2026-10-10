import os
import requests
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("VOICE_WORKER_URL")
token = os.getenv("VOICE_WORKER_TOKEN")

if not url:
    raise RuntimeError("VOICE_WORKER_URL is missing in .env")

if not token:
    raise RuntimeError("VOICE_WORKER_TOKEN is missing in .env")

print("Testing Colab worker...")
print("URL:", url)

response = requests.get(
    f"{url.rstrip('/')}/health",
    headers={
        "X-Voice-Worker-Token": token
    },
    timeout=30,
)

print("HTTP status:", response.status_code)
print("Response:", response.text)

response.raise_for_status()

data = response.json()

if data.get("status") == "ok" and data.get("gpu") is True:
    print("\n✅ COLAB GPU CONNECTION SUCCESSFUL")
else:
    print("\n❌ Colab responded, but GPU health check failed")