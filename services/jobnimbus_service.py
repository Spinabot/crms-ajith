import os
import time
import json
import logging
from typing import Any, Dict, Optional, List, Tuple

import requests
from dotenv import load_dotenv

# Load environment from .env if present
load_dotenv()

logger = logging.getLogger(__name__)

BASE_URL = os.getenv("JOBNIMBUS_BASE_URL", "https://api.jobnimbus.com").rstrip("/")
API_PREFIX = os.getenv("JOBNIMBUS_API_PREFIX", "v1").strip("/")


class JobNimbusError(Exception):
    pass


def _get_api_key() -> str:
    """Return API key from database first, then env, then incoming Flask request headers."""
    # 1) Try database first (if USE_JOBNIMBUS_DB_KEY is set or default behavior)
    if os.getenv("USE_JOBNIMBUS_DB_KEY", "true").lower() == "true":
        try:
            from models import db, JobNimbusCredentials
            from flask import current_app
            
            with current_app.app_context():
                # Get the active credentials from database
                credentials = db.session.query(JobNimbusCredentials).filter_by(is_active=True).first()
                if credentials and credentials.api_key:
                    logger.info("Using JobNimbus API key from database")
                    return credentials.api_key.strip()
        except Exception as e:
            logger.warning(f"Could not read from database: {e}")
            # Continue to fallback methods
    
    # 2) Try .env / environment
    key = os.getenv("JOBNIMBUS_API_KEY")
    if key:
        key = key.strip()
        if key:
            logger.info("Using JobNimbus API key from environment")
            return key

    # 3) Fallback to request headers (Swagger Authorize)
    try:
        from flask import request
        if request:
            auth = request.headers.get("Authorization", "").strip()
            if auth:
                parts = auth.split()
                if len(parts) == 2 and parts[0].lower() == "bearer":
                    logger.info("Using JobNimbus API key from Authorization header")
                    return parts[1].strip()
                # if not Bearer formatted, treat entire value as key
                logger.info("Using JobNimbus API key from Authorization header")
                return auth
            xkey = request.headers.get("x-api-key") or request.headers.get("X-API-KEY")
            if xkey:
                logger.info("Using JobNimbus API key from x-api-key header")
                return xkey.strip()
    except Exception:
        # If not in a request context, ignore
        pass

    raise JobNimbusError("Missing JOBNIMBUS_API_KEY")


def _get_config_from_db() -> Tuple[str, str]:
    """Get base URL and API prefix from database if available."""
    try:
        from models import db, JobNimbusCredentials
        from flask import current_app
        
        with current_app.app_context():
            credentials = db.session.query(JobNimbusCredentials).filter_by(is_active=True).first()
            if credentials:
                base_url = credentials.base_url or BASE_URL
                api_prefix = credentials.api_prefix or API_PREFIX
                return base_url.rstrip("/"), api_prefix.strip("/")
    except Exception as e:
        logger.warning(f"Could not read config from database: {e}")
    
    # Fallback to environment variables
    base_url = os.getenv("JOBNIMBUS_BASE_URL", BASE_URL).rstrip("/")
    api_prefix = (os.getenv("JOBNIMBUS_API_PREFIX", API_PREFIX) or "").strip("/")
    return base_url, api_prefix


def _headers() -> Dict[str, str]:
    key = _get_api_key()
    return {
        "Authorization": f"Bearer {key}",  # many setups accept Bearer
        "x-api-key": key,                  # some use x-api-key
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def _url(path: str) -> str:
    # Get config from database or environment
    base_url, api_prefix = _get_config_from_db()
    prefix_part = f"/{api_prefix}" if api_prefix else ""
    return f"{base_url}{prefix_part}/{path.lstrip('/')}"


def _request(
    method: str,
    path: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Any] = None,
    retries: int = 2,
) -> Tuple[int, Dict[str, Any]]:
    url = _url(path)
    payload = json.dumps(data) if isinstance(data, (dict, list)) else data
    backoff = 0.8

    for attempt in range(retries + 1):
        resp = requests.request(
            method,
            url,
            headers=_headers(),
            params=params,
            data=payload,
            timeout=30,
        )

        if resp.status_code in (429, 502, 503, 504) and attempt < retries:
            wait = backoff * (2 ** attempt)
            logger.warning(
                "JobNimbus %s %s -> %s. Retrying in %.1fs", method, path, resp.status_code, wait
            )
            time.sleep(wait)
            continue

        if resp.headers.get("content-type", "").startswith("application/json"):
            body = resp.json()
        else:
            body = {"raw": resp.text}

        if resp.ok:
            return resp.status_code, body

        raise JobNimbusError(f"JobNimbus API error {resp.status_code}: {body}")

    raise JobNimbusError("JobNimbus request failed after retries")


# Contacts

def list_contacts(page: int = 1, page_size: int = 100, query: Optional[str] = None) -> Dict[str, Any]:
    params: Dict[str, Any] = {"page": page, "pageSize": page_size}
    if query:
        params["q"] = query
    _, body = _request("GET", "/contacts", params=params)
    return body


def get_contact(contact_id: str) -> Dict[str, Any]:
    _, body = _request("GET", f"/contacts/{contact_id}")
    return body


def create_contact(contact: Dict[str, Any]) -> Dict[str, Any]:
    _, body = _request("POST", "/contacts", data=contact)
    return body


def update_contact(contact_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    _, body = _request("PUT", f"/contacts/{contact_id}", data=updates)
    return body


def delete_contact(contact_id: str) -> Dict[str, Any]:
    _, body = _request("DELETE", f"/contacts/{contact_id}")
    return body


# Jobs

def list_jobs(page: int = 1, page_size: int = 100, status: Optional[str] = None) -> Dict[str, Any]:
    params: Dict[str, Any] = {"page": page, "pageSize": page_size}
    if status:
        params["status"] = status
    _, body = _request("GET", "/jobs", params=params)
    return body


def create_job(job: Dict[str, Any]) -> Dict[str, Any]:
    _, body = _request("POST", "/jobs", data=job)
    return body 