import os

import httpx


DIFY_API_URL = os.environ.get("DIFY_API_URL", "").strip()
DIFY_API_KEY = os.environ.get("DIFY_API_KEY", "").strip()


def run_workflow(keyword: str, provider: str) -> dict:
    """第3回で公開したDify Workflowをblockingモードで実行する。"""
    if not DIFY_API_URL:
        raise RuntimeError("DIFY_API_URL is not set")

    if not DIFY_API_KEY:
        raise RuntimeError("DIFY_API_KEY is not set")

    url = f"{DIFY_API_URL.rstrip('/')}/workflows/run"

    headers = {
        "Authorization": f"Bearer {DIFY_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "inputs": {
            "keyword": keyword,
            "provider": provider,
        },
        "response_mode": "blocking",
        "user": "affiliate-agent-harness",
    }

    with httpx.Client(timeout=120.0) as client:
        response = client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
