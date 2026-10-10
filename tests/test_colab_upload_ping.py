import os

import requests
from dotenv import load_dotenv


def main() -> None:
    load_dotenv()
    url = os.getenv("VOICE_WORKER_URL", "").rstrip("/")
    token = os.getenv("VOICE_WORKER_TOKEN", "")
    if not url:
        raise RuntimeError("VOICE_WORKER_URL is missing in .env")
    if not token:
        raise RuntimeError("VOICE_WORKER_TOKEN is missing in .env")

    try:
        response = requests.get(
            f"{url}/upload-test-ping",
            headers={"X-Voice-Worker-Token": token},
            timeout=30,
        )
    except requests.exceptions.Timeout as exc:
        print(f"Classification: TIMEOUT ({type(exc).__name__})")
        raise SystemExit(1) from exc
    except requests.exceptions.ConnectionError as exc:
        print(f"Classification: NETWORK_CONNECTION_FAILURE ({type(exc).__name__})")
        raise SystemExit(1) from exc
    except requests.exceptions.RequestException as exc:
        print(f"Classification: NETWORK_CONNECTION_FAILURE ({type(exc).__name__})")
        raise SystemExit(1) from exc

    print(f"HTTP status: {response.status_code}")
    try:
        result = response.json()
    except requests.exceptions.JSONDecodeError:
        result = {"response": response.text}
    print(f"Response: {result}")

    if response.status_code == 200:
        print("PING_OK")
    elif response.status_code in (401, 403):
        print("AUTH_FAILURE")
        raise SystemExit(1)
    elif response.status_code == 404:
        print("ROUTE_NOT_DEPLOYED")
        raise SystemExit(1)
    else:
        print("HTTP_FAILURE")
        raise SystemExit(1)


if __name__ == "__main__":
    main()