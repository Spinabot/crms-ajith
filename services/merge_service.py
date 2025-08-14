# services/merge_service.py
import os
import logging
from typing import Optional, Dict, Any
import requests

MERGE_API_KEY = os.getenv("MERGE_API_KEY")
MERGE_BASE_URL = os.getenv("MERGE_BASE_URL", "https://api.merge.dev")

# CRM base (US)
MERGE_CRM_BASE = f"{MERGE_BASE_URL}/api/crm/v1"
# Link token endpoint is category-specific (CRM) per docs
MERGE_LINK_TOKEN_URL = f"{MERGE_BASE_URL}/api/crm/v1/link-token"

DEFAULT_TIMEOUT = (5, 30)  # (connect, read)
log = logging.getLogger(__name__)

class MergeServiceError(RuntimeError):
    pass

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