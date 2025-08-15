# services/merge_client.py
import os
import requests

MERGE_PROD_KEY = os.environ.get("MERGE_PROD_KEY", "placeholder_key")  # your Production Access Key
MERGE_ACCOUNT_TOKEN = os.environ.get("MERGE_ACCOUNT_TOKEN")  # per-linked-account token

BASES = {
    "crm":  os.getenv("MERGE_CRM_BASE",  "https://api.merge.dev/api/crm/v1"),
    "hris": os.getenv("MERGE_HRIS_BASE", "https://api.merge.dev/api/hris/v1"),
}

def _headers(extra=None):
    h = {
        "Accept": "application/json",
        "Authorization": f"Bearer {MERGE_PROD_KEY}",
    }
    if MERGE_ACCOUNT_TOKEN:
        h["X-Account-Token"] = MERGE_ACCOUNT_TOKEN
    if extra:
        h.update(extra)
    return h

def call(domain: str, method: str, path: str, **kwargs):
    url = f"{BASES[domain]}{path}"
    resp = requests.request(method, url, headers=_headers(kwargs.pop("headers", None)),
                            timeout=45, **kwargs)
    # Bubble up Merge errors to the client
    resp.raise_for_status()
    if resp.content and resp.headers.get("Content-Type","").startswith("application/json"):
        return resp.json()
    return {"ok": True} 