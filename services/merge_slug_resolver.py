# services/merge_slug_resolver.py
import os
import re
import requests
from typing import Dict, List, Optional, Tuple
from services.merge_service import _headers, MergeServiceError

def normalize_vendor_name(name: str) -> str:
    """Normalize vendor name for matching (remove spaces, special chars, lowercase)"""
    return re.sub(r"[^a-z0-9]", "", name.lower())

def resolve_vendor_slugs(pretty_names: List[str]) -> Dict[str, str]:
    """
    Resolve vendor display names to Merge slugs using Integration Metadata API.
    Returns mapping of original_name -> slug (None if not found)
    """
    try:
        url = "https://api.merge.dev/api/integrations"
        response = requests.get(url, headers=_headers(), timeout=30)
        response.raise_for_status()
        
        catalog = response.json().get("data", [])
        
        # Create normalized lookup
        by_normalized = {normalize_vendor_name(i.get("name", "")): i.get("slug") for i in catalog}
        
        # Map original names to slugs
        resolved = {}
        for name in pretty_names:
            normalized = normalize_vendor_name(name)
            resolved[name] = by_normalized.get(normalized)
            
        return resolved
        
    except Exception as e:
        raise MergeServiceError(f"Failed to resolve vendor slugs: {e}")

def validate_and_resolve_allowlist() -> Tuple[List[str], Dict[str, str], List[str]]:
    """
    Validate the MERGE_CRM_ALLOWED_SLUGS environment variable.
    Returns (valid_slugs, name_to_slug_mapping, unresolved_names)
    """
    # Get the allowlist from environment
    allowlist_str = os.getenv("MERGE_CRM_ALLOWED_SLUGS", "")
    if not allowlist_str:
        return [], {}, []
    
    # Parse the comma-separated list
    vendor_names = [name.strip() for name in allowlist_str.split(",") if name.strip()]
    
    if not vendor_names:
        return [], {}, []
    
    # Resolve vendor names to slugs
    name_to_slug = resolve_vendor_slugs(vendor_names)
    
    # Separate resolved and unresolved
    valid_slugs = []
    unresolved_names = []
    
    for name, slug in name_to_slug.items():
        if slug:
            valid_slugs.append(slug)
        else:
            unresolved_names.append(name)
    
    return valid_slugs, name_to_slug, unresolved_names

def get_crm_integrations_catalog() -> Dict[str, any]:
    """
    Get CRM integrations catalog with additional metadata for allowlist validation.
    Returns catalog with resolved status for each vendor.
    """
    try:
        url = "https://api.merge.dev/api/integrations"
        response = requests.get(url, headers=_headers(), timeout=30)
        response.raise_for_status()
        
        catalog = response.json()
        
        # Add allowlist status to each integration
        valid_slugs, name_to_slug, unresolved = validate_and_resolve_allowlist()
        
        for integration in catalog.get("data", []):
            slug = integration.get("slug")
            if slug:
                integration["in_allowlist"] = slug in valid_slugs
            else:
                integration["in_allowlist"] = False
        
        # Add allowlist summary
        catalog["allowlist_summary"] = {
            "total_vendors": len(vendor_names) if 'vendor_names' in locals() else 0,
            "resolved_slugs": len(valid_slugs),
            "unresolved_names": unresolved,
            "valid_slugs": valid_slugs
        }
        
        return catalog
        
    except Exception as e:
        raise MergeServiceError(f"Failed to get integrations catalog: {e}")

def auto_update_allowlist() -> str:
    """
    Automatically update the allowlist by resolving all vendor names.
    Returns the new allowlist string to set in environment.
    """
    try:
        # Get current allowlist
        current_allowlist = os.getenv("MERGE_CRM_ALLOWED_SLUGS", "")
        if not current_allowlist:
            return ""
        
        vendor_names = [name.strip() for name in current_allowlist.split(",") if name.strip()]
        
        # Resolve all names
        name_to_slug = resolve_vendor_slugs(vendor_names)
        
        # Build new allowlist with resolved slugs
        resolved_slugs = []
        unresolved_names = []
        
        for name, slug in name_to_slug.items():
            if slug:
                resolved_slugs.append(slug)
            else:
                unresolved_names.append(name)
        
        # Create new allowlist string
        new_allowlist = ",".join(sorted(resolved_slugs))
        
        # Log results
        print(f"✅ Resolved {len(resolved_slugs)} vendor slugs")
        if unresolved_names:
            print(f"⚠️  Unresolved vendors: {unresolved_names}")
        
        return new_allowlist
        
    except Exception as e:
        print(f"❌ Failed to auto-update allowlist: {e}")
        return "" 