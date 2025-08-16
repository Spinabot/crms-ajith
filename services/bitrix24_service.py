# services/bitrix24_service.py
import os
import logging
import requests
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin
from models import db, ClientCRMAuth  # you already have this

log = logging.getLogger(__name__)

BITRIX_DEFAULT_WEBHOOK_BASE = os.getenv(
    "BITRIX_WEBHOOK_BASE",  # e.g. https://b24-...bitrix24.com/rest/1/<token>/
    ""
).rstrip("/")

BITRIX_OUTBOUND_TOKEN = os.getenv("BITRIX_OUTBOUND_TOKEN", "")  # used to verify events

CRM_NAME = "bitrix24"

# -------- helpers --------

def _flatten_for_form(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Bitrix24 accepts x-www-form-urlencoded.
    Flatten top-level dicts like fields/filter/order/select/start into form keys:
      fields[NAME]=..., filter[EMAIL]=..., select[]=ID, select[]=NAME
    """
    out: Dict[str, Any] = {}
    for k, v in (payload or {}).items():
        if k in ("fields", "filter", "order") and isinstance(v, dict):
            for fk, fv in v.items():
                out[f"{k}[{fk}]"] = fv
        elif k == "select" and isinstance(v, (list, tuple)):
            # multiple select[]=FIELD
            for i, sv in enumerate(v):
                out[f"select[{i}]"] = sv
        else:
            out[k] = v
    return out

def _method_url(base: str, method: str) -> str:
    # Bitrix methods are like "crm.contact.add" – you can call .../crm.contact.add.json
    if not base.endswith("/"):
        base += "/"
    if not method.endswith(".json"):
        method = f"{method}.json"
    return urljoin(base, method)

def _get_client_webhook_base(client_id: int) -> str:
    """
    Read the Bitrix24 inbound webhook base URL from DB (ClientCRMAuth.credentials['webhook_base']),
    else fallback to env BITRIX_WEBHOOK_BASE.
    """
    rec: Optional[ClientCRMAuth] = ClientCRMAuth.query.filter_by(client_id=client_id, crm_id=999).first()  # Temporary ID
    if rec and isinstance(rec.credentials, dict):
        wb = (rec.credentials.get("webhook_base") or "").strip().rstrip("/")
        if wb:
            return wb
    if not BITRIX_DEFAULT_WEBHOOK_BASE:
        raise RuntimeError("No Bitrix24 webhook base configured (set in DB or BITRIX_WEBHOOK_BASE env).")
    return BITRIX_DEFAULT_WEBHOOK_BASE

def bx_call(client_id: int, method: str, payload: Optional[Dict[str, Any]] = None, timeout: Tuple[int, int] = (5, 30)) -> Dict[str, Any]:
    """
    Generic Bitrix24 call via inbound webhook URL.
    """
    base = _get_client_webhook_base(client_id)
    url = _method_url(base, method)
    data = _flatten_for_form(payload or {})
    resp = requests.post(url, data=data, timeout=timeout)  # form-encoded is safest across methods
    try:
        resp.raise_for_status()
    except requests.HTTPError:
        log.error("Bitrix24 error %s: %s", resp.status_code, resp.text)
        raise
    js = resp.json() if resp.headers.get("Content-Type", "").startswith("application/json") else {}
    # Bitrix wraps results in { "result": ... , "error": "...", "error_description": "..."}
    if "error" in js and js["error"]:
        raise RuntimeError(f"Bitrix24 error: {js.get('error')} {js.get('error_description')}")
    return js

# -------- high-level CRM helpers --------

# Contacts
def contact_add(client_id: int, fields: Dict[str, Any]) -> Dict[str, Any]:
    return bx_call(client_id, "crm.contact.add", {"fields": fields})

def contact_get(client_id: int, contact_id: int) -> Dict[str, Any]:
    return bx_call(client_id, "crm.contact.get", {"id": contact_id})

def contact_update(client_id: int, contact_id: int, fields: Dict[str, Any]) -> Dict[str, Any]:
    return bx_call(client_id, "crm.contact.update", {"id": contact_id, "fields": fields})

def contact_delete(client_id: int, contact_id: int) -> Dict[str, Any]:
    return bx_call(client_id, "crm.contact.delete", {"id": contact_id})

def contact_list(client_id: int, filter_: Optional[Dict[str, Any]] = None, select: Optional[List[str]] = None,
                 order: Optional[Dict[str, str]] = None, start: Optional[int] = None) -> Dict[str, Any]:
    payload = {}
    if filter_:
        payload["filter"] = filter_
    if select:
        payload["select"] = select
    if order:
        payload["order"] = order
    if start is not None:
        payload["start"] = start
    return bx_call(client_id, "crm.contact.list", payload)

# Deals
def deal_add(client_id: int, fields: Dict[str, Any]) -> Dict[str, Any]:
    return bx_call(client_id, "crm.deal.add", {"fields": fields})

def deal_get(client_id: int, deal_id: int) -> Dict[str, Any]:
    return bx_call(client_id, "crm.deal.get", {"id": deal_id})

def deal_update(client_id: int, deal_id: int, fields: Dict[str, Any]) -> Dict[str, Any]:
    return bx_call(client_id, "crm.deal.update", {"id": deal_id, "fields": fields})

def deal_delete(client_id: int, deal_id: int) -> Dict[str, Any]:
    return bx_call(client_id, "crm.deal.delete", {"id": deal_id})

def deal_list(client_id: int, filter_: Optional[Dict[str, Any]] = None, select: Optional[List[str]] = None,
              order: Optional[Dict[str, str]] = None, start: Optional[int] = None) -> Dict[str, Any]:
    payload = {}
    if filter_:
        payload["filter"] = filter_
    if select:
        payload["select"] = select
    if order:
        payload["order"] = order
    if start is not None:
        payload["start"] = start
    return bx_call(client_id, "crm.deal.list", payload)

# Leads (if your portal uses leads)
def lead_add(client_id: int, fields: Dict[str, Any]) -> Dict[str, Any]:
    return bx_call(client_id, "crm.lead.add", {"fields": fields})

def lead_get(client_id: int, lead_id: int) -> Dict[str, Any]:
    return bx_call(client_id, "crm.lead.get", {"id": lead_id})

def lead_update(client_id: int, lead_id: int, fields: Dict[str, Any]) -> Dict[str, Any]:
    return bx_call(client_id, "crm.lead.update", {"id": lead_id, "fields": fields})

def lead_delete(client_id: int, lead_id: int) -> Dict[str, Any]:
    return bx_call(client_id, "crm.lead.delete", {"id": lead_id})

def lead_list(client_id: int, filter_: Optional[Dict[str, Any]] = None, select: Optional[List[str]] = None,
              order: Optional[Dict[str, str]] = None, start: Optional[int] = None) -> Dict[str, Any]:
    payload = {}
    if filter_:
        payload["filter"] = filter_
    if select:
        payload["select"] = select
    if order:
        payload["order"] = order
    if start is not None:
        payload["start"] = start
    return bx_call(client_id, "crm.lead.list", payload) 