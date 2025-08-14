# services/merge_service.py
import os
import logging
import hmac
import hashlib
import base64
from typing import Optional, Dict, Any
import requests

MERGE_API_KEY = os.getenv("MERGE_API_KEY")
MERGE_BASE_URL = os.getenv("MERGE_BASE_URL", "https://api.merge.dev")
MERGE_WEBHOOK_SECRET = os.getenv("MERGE_WEBHOOK_SECRET")

# CRM base (US)
MERGE_CRM_BASE = f"{MERGE_BASE_URL}/api/crm/v1"
# Link token endpoint is category-specific (CRM) per docs
MERGE_LINK_TOKEN_URL = f"{MERGE_BASE_URL}/api/crm/v1/link-token"

DEFAULT_TIMEOUT = (5, 30)  # (connect, read)
log = logging.getLogger(__name__)

class MergeServiceError(RuntimeError):
    pass

def verify_webhook_signature(raw_body: bytes, signature_header: str) -> bool:
    """
    Verify Merge webhook using HMAC-SHA256 over the EXACT raw request body.
    Compare against base64url digest from X-Merge-Webhook-Signature.
    """
    if not MERGE_WEBHOOK_SECRET or not signature_header:
        return False
    digest = hmac.new(
        key=MERGE_WEBHOOK_SECRET.encode("utf-8"),
        msg=raw_body,
        digestmod=hashlib.sha256,
    ).digest()
    computed = base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")
    supplied = signature_header.strip().rstrip("=")
    return hmac.compare_digest(computed, supplied)

def _headers(account_token: Optional[str] = None) -> Dict[str, str]:
    if not MERGE_API_KEY:
        raise MergeServiceError("MERGE_API_KEY is not set")
    h = {
        "Authorization": f"Bearer {MERGE_API_KEY}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    if account_token:
        h["X-Account-Token"] = account_token
    return h

def create_link_token(end_user_email: str,
                      end_user_org_name: str,
                      end_user_origin_id: str,
                      categories=None,
                      should_create_magic_link_url: bool = True,
                      integration_slug: Optional[str] = None) -> Dict[str, Any]:
    """
    Initialize a Merge Link session for CRM, returning a link_token and (optionally) a magic_link_url.
    """
    payload = {
        "end_user_email_address": end_user_email,
        "end_user_organization_name": end_user_org_name,
        "end_user_origin_id": end_user_origin_id,
        "categories": categories or ["crm"],
        "should_create_magic_link_url": should_create_magic_link_url,
        "link_expiry_mins": 10080,  # 7 days
    }
    if integration_slug:
        payload["integration"] = integration_slug

    try:
        resp = requests.post(MERGE_LINK_TOKEN_URL, json=payload, headers=_headers(), timeout=DEFAULT_TIMEOUT)
        if resp.status_code >= 400:
            raise MergeServiceError(f"Merge create_link_token failed: {resp.status_code} {resp.text}")
        return resp.json()
    except requests.RequestException as e:
        raise MergeServiceError(f"Merge create_link_token error: {e}") from e

def list_contacts(account_token: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    GET /contacts via Merge CRM Unified API for the linked account.
    """
    url = f"{MERGE_CRM_BASE}/contacts"
    try:
        resp = requests.get(url, headers=_headers(account_token), params=params or {}, timeout=DEFAULT_TIMEOUT)
        if resp.status_code >= 400:
            raise MergeServiceError(f"Merge list_contacts failed: {resp.status_code} {resp.text}")
        return resp.json()
    except requests.RequestException as e:
        raise MergeServiceError(f"Merge list_contacts error: {e}") from e

def create_contact(account_token: str, contact_body: Dict[str, Any]) -> Dict[str, Any]:
    """
    POST /contacts via Merge CRM Unified API for the linked account.
    Use Merge's common model for Contact.
    """
    url = f"{MERGE_CRM_BASE}/contacts"
    try:
        resp = requests.post(url, headers=_headers(account_token), json=contact_body, timeout=DEFAULT_TIMEOUT)
        if resp.status_code >= 400:
            raise MergeServiceError(f"Merge create_contact failed: {resp.status_code} {resp.text}")
        return resp.json()
    except requests.RequestException as e:
        raise MergeServiceError(f"Merge create_contact error: {e}") from e

def list_linked_accounts(category: str = "crm") -> Dict[str, Any]:
    """
    GET /linked-accounts — useful for debugging / admin views.
    """
    url = f"{MERGE_BASE_URL}/api/{category}/v1/linked-accounts"
    try:
        resp = requests.get(url, headers=_headers(), timeout=DEFAULT_TIMEOUT)
        if resp.status_code >= 400:
            raise MergeServiceError(f"Merge list_linked_accounts failed: {resp.status_code} {resp.text}")
        return resp.json()
    except requests.RequestException as e:
        raise MergeServiceError(f"Merge list_linked_accounts error: {e}") from e

# ---------- HRIS READS ----------
def hris_list_employees(account_token: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    url = f"{MERGE_HRIS_BASE}/employees"
    resp = requests.get(url, headers=_headers(account_token), params=params or {}, timeout=DEFAULT_TIMEOUT)
    if resp.status_code >= 400:
        raise MergeServiceError(f"Merge hris_list_employees failed: {resp.status_code} {resp.text}")
    return resp.json()

def hris_get_employee(account_token: str, employee_id: str) -> Dict[str, Any]:
    url = f"{MERGE_HRIS_BASE}/employees/{employee_id}"
    resp = requests.get(url, headers=_headers(account_token), timeout=DEFAULT_TIMEOUT)
    if resp.status_code >= 400:
        raise MergeServiceError(f"Merge hris_get_employee failed: {resp.status_code} {resp.text}")
    return resp.json()

def hris_list_employments(account_token: str, params: Optional[Dict[str, Any]]=None) -> Dict[str, Any]:
    url = f"{MERGE_HRIS_BASE}/employments"
    resp = requests.get(url, headers=_headers(account_token), params=params or {}, timeout=DEFAULT_TIMEOUT)
    if resp.status_code >= 400:
        raise MergeServiceError(f"Merge hris_list_employments failed: {resp.status_code} {resp.text}")
    return resp.json()

def hris_list_locations(account_token: str, params: Optional[Dict[str, Any]]=None) -> Dict[str, Any]:
    url = f"{MERGE_HRIS_BASE}/locations"
    resp = requests.get(url, headers=_headers(account_token), params=params or {}, timeout=DEFAULT_TIMEOUT)
    if resp.status_code >= 400:
        raise MergeServiceError(f"Merge hris_list_locations failed: {resp.status_code} {resp.text}")
    return resp.json()

def hris_list_groups(account_token: str, params: Optional[Dict[str, Any]]=None) -> Dict[str, Any]:
    url = f"{MERGE_HRIS_BASE}/groups"
    resp = requests.get(url, headers=_headers(account_token), params=params or {}, timeout=DEFAULT_TIMEOUT)
    if resp.status_code >= 400:
        raise MergeServiceError(f"Merge hris_list_groups failed: {resp.status_code} {resp.text}")
    return resp.json()

# ---------- HRIS WRITES (Unified endpoints) ----------
def hris_create_time_off(account_token: str, model: Dict[str, Any], qs: Optional[Dict[str, Any]]=None) -> Dict[str, Any]:
    # POST /time-off
    url = f"{MERGE_HRIS_BASE}/time-off"
    params = qs or {}
    resp = requests.post(url, headers=_headers(account_token), json={"model": model}, params=params, timeout=DEFAULT_TIMEOUT)
    if resp.status_code >= 400:
        raise MergeServiceError(f"Merge hris_create_time_off failed: {resp.status_code} {resp.text}")
    return resp.json()

def hris_list_time_off(account_token: str, params: Optional[Dict[str, Any]]=None) -> Dict[str, Any]:
    url = f"{MERGE_HRIS_BASE}/time-off"
    resp = requests.get(url, headers=_headers(account_token), params=params or {}, timeout=DEFAULT_TIMEOUT)
    if resp.status_code >= 400:
        raise MergeServiceError(f"Merge hris_list_time_off failed: {resp.status_code} {resp.text}")
    return resp.json()

def hris_get_time_off(account_token: str, id_: str) -> Dict[str, Any]:
    url = f"{MERGE_HRIS_BASE}/time-off/{id_}"
    resp = requests.get(url, headers=_headers(account_token), timeout=DEFAULT_TIMEOUT)
    if resp.status_code >= 400:
        raise MergeServiceError(f"Merge hris_get_time_off failed: {resp.status_code} {resp.text}")
    return resp.json()

def hris_create_timesheet_entry(account_token: str, model: Dict[str, Any], qs: Optional[Dict[str, Any]]=None) -> Dict[str, Any]:
    # POST /timesheet-entries
    url = f"{MERGE_HRIS_BASE}/timesheet-entries"
    params = qs or {}
    resp = requests.post(url, headers=_headers(account_token), json={"model": model}, params=params, timeout=DEFAULT_TIMEOUT)
    if resp.status_code >= 400:
        raise MergeServiceError(f"Merge hris_create_timesheet_entry failed: {resp.status_code} {resp.text}")
    return resp.json()

def hris_list_timesheet_entries(account_token: str, params: Optional[Dict[str, Any]]=None) -> Dict[str, Any]:
    url = f"{MERGE_HRIS_BASE}/timesheet-entries"
    resp = requests.get(url, headers=_headers(account_token), params=params or {}, timeout=DEFAULT_TIMEOUT)
    if resp.status_code >= 400:
        raise MergeServiceError(f"Merge hris_list_timesheet_entries failed: {resp.status_code} {resp.text}")
    return resp.json()

def hris_get_timesheet_entry(account_token: str, id_: str) -> Dict[str, Any]:
    url = f"{MERGE_HRIS_BASE}/timesheet-entries/{id_}"
    resp = requests.get(url, headers=_headers(account_token), timeout=DEFAULT_TIMEOUT)
    if resp.status_code >= 400:
        raise MergeServiceError(f"Merge hris_get_timesheet_entry failed: {resp.status_code} {resp.text}")
    return resp.json()

# ---------- Passthrough (for PATCH/DELETE or other vendor-specific writes) ----------
def hris_passthrough(account_token: str, method: str, path: str, data: Optional[Any]=None,
                     request_format: str = "JSON", headers: Optional[Dict[str, str]]=None,
                     base_url_override: Optional[str]=None, run_async: bool=False) -> Dict[str, Any]:
    """
    Use Merge Passthrough/Async Passthrough to call a third-party endpoint directly.
    Example: method="PATCH", path="/employees/123", data={"first_name": "New"}.
    """
    endpoint = "async-passthrough" if run_async else "passthrough"
    url = f"{MERGE_HRIS_BASE}/{endpoint}"
    body: Dict[str, Any] = {
        "method": method.upper(),
        "path": path,
        "request_format": request_format
    }
    if data is not None:
        body["data"] = data
    if headers:
        body["headers"] = headers
    if base_url_override:
        body["base_url_override"] = base_url_override

    resp = requests.post(url, headers=_headers(account_token), json=body, timeout=DEFAULT_TIMEOUT)
    if resp.status_code >= 400:
        raise MergeServiceError(f"Merge hris_passthrough failed: {resp.status_code} {resp.text}")
    return resp.json() 