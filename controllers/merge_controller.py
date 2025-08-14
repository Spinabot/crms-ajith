# controllers/merge_controller.py
from flask import Blueprint, request, jsonify
from models import db, MergeLinkedAccount, Clients
from services.merge_service import (
    create_link_token, list_contacts, create_contact, list_linked_accounts, MergeServiceError
)

merge_bp = Blueprint("merge", __name__, url_prefix="/api/merge")

@merge_bp.route("/clients/<int:client_id>/link-token", methods=["POST"])
def merge_create_link_token(client_id: int):
    """
    Body: { end_user_email, end_user_org_name, end_user_origin_id, integration_slug? }
    Returns: { link_token, magic_link_url?, ... }
    """
    data = request.get_json(force=True) or {}
    end_user_email = data.get("end_user_email")
    end_user_org_name = data.get("end_user_org_name")
    end_user_origin_id = data.get("end_user_origin_id")
    integration_slug = data.get("integration_slug")

    if not all([end_user_email, end_user_org_name, end_user_origin_id]):
        return jsonify({"error": "end_user_email, end_user_org_name, end_user_origin_id are required"}), 400

    try:
        token_resp = create_link_token(
            end_user_email=end_user_email,
            end_user_org_name=end_user_org_name,
            end_user_origin_id=end_user_origin_id,
            categories=["crm"],
            should_create_magic_link_url=True,
            integration_slug=integration_slug
        )
        # Do not persist anything yet; account_token arrives after user completes Link.
        return jsonify(token_resp), 200
    except MergeServiceError as e:
        return jsonify({"error": str(e)}), 502

@merge_bp.route("/clients/<int:client_id>/linked-accounts", methods=["POST"])
def merge_save_linked_account(client_id: int):
    """
    After user finishes Merge Link, you WILL have an account_token (via your UI or webhook).
    Body: { account_token, integration_slug?, end_user_origin_id?, end_user_email?, end_user_org_name?, raw? }
    """
    data = request.get_json(force=True) or {}
    account_token = data.get("account_token")
    if not account_token:
        return jsonify({"error": "account_token is required"}), 400

    mla = MergeLinkedAccount(
        client_id=client_id,
        account_token=account_token,
        integration_slug=data.get("integration_slug"),
        end_user_origin_id=data.get("end_user_origin_id"),
        end_user_email=data.get("end_user_email"),
        end_user_org_name=data.get("end_user_org_name"),
        raw=data.get("raw"),
    )
    db.session.add(mla)
    db.session.commit()
    return jsonify({"id": mla.id, "account_token": mla.account_token}), 201

@merge_bp.route("/clients/<int:client_id>/crm/contacts", methods=["GET"])
def merge_list_contacts(client_id: int):
    """
    Query: account_token=<token> (optional). If absent, uses the first active linked account for this client.
    Supports standard Merge filters (e.g., modified_after).
    """
    account_token = request.args.get("account_token")
    if not account_token:
        mla = MergeLinkedAccount.query.filter_by(client_id=client_id, status="active").first()
        if not mla:
            return jsonify({"error": "No Merge linked account found for client"}), 404
        account_token = mla.account_token

    params = {}
    if "modified_after" in request.args:
        params["modified_after"] = request.args["modified_after"]
    if "cursor" in request.args:
        params["cursor"] = request.args["cursor"]
    if "page_size" in request.args:
        params["page_size"] = request.args.get("page_size", type=int)

    try:
        data = list_contacts(account_token, params=params)
        return jsonify(data), 200
    except MergeServiceError as e:
        return jsonify({"error": str(e)}), 502

@merge_bp.route("/clients/<int:client_id>/crm/contacts", methods=["POST"])
def merge_create_contact(client_id: int):
    """
    Body: { account_token, contact: {...Merge Contact common model...} }
    If account_token omitted, use first active for client.
    """
    data = request.get_json(force=True) or {}
    account_token = data.get("account_token")
    if not account_token:
        mla = MergeLinkedAccount.query.filter_by(client_id=client_id, status="active").first()
        if not mla:
            return jsonify({"error": "No Merge linked account found for client"}), 404
        account_token = mla.account_token

    contact_body = data.get("contact") or {}
    if not contact_body:
        return jsonify({"error": "contact body is required"}), 400

    try:
        resp = create_contact(account_token, contact_body)
        return jsonify(resp), 201
    except MergeServiceError as e:
        return jsonify({"error": str(e)}), 502

@merge_bp.route("/linked-accounts", methods=["GET"])
def merge_linked_accounts_admin():
    """Admin/debug endpoint: list all Merge linked accounts (category=crm) from Merge itself."""
    try:
        data = list_linked_accounts(category="crm")
        return jsonify(data), 200
    except MergeServiceError as e:
        return jsonify({"error": str(e)}), 502

@merge_bp.route("/webhook", methods=["POST"])
def merge_webhook():
    """
    Merge -> Your API
    Verifies X-Merge-Webhook-Signature, then (best-effort) updates MergeLinkedAccount.
    """
    from services.merge_service import verify_webhook_signature
    sig = request.headers.get("X-Merge-Webhook-Signature")
    raw = request.get_data(cache=False, as_text=False)

    if not verify_webhook_signature(raw, sig):
        return jsonify({"error": "invalid signature"}), 401

    payload = request.get_json(silent=True) or {}
    hook = (payload.get("hook") or {})
    event_type = (hook.get("event_type") or "").lower()
    la = (payload.get("linked_account") or {})

    # Try to upsert MergeLinkedAccount using account_token or end_user_origin_id
    account_token = la.get("account_token") or payload.get("account_token")
    end_user_origin_id = la.get("end_user_origin_id") or la.get("end_user_id")
    integration_slug = la.get("integration_slug") or la.get("integration") or None

    # Update existing records if we can find them
    updated = False
    if account_token:
        rec = MergeLinkedAccount.query.filter_by(account_token=account_token).first()
        if rec:
            # Reflect lifecycle events
            if "deleted" in event_type:
                rec.status = "disabled"
            elif "linked" in event_type or "synced" in event_type or "changed" in event_type:
                rec.status = "active"
            if integration_slug and not rec.integration_slug:
                rec.integration_slug = integration_slug
            rec.raw = payload
            db.session.commit()
            updated = True

    if not updated and end_user_origin_id:
        rec = MergeLinkedAccount.query.filter_by(end_user_origin_id=end_user_origin_id).first()
        if rec:
            if account_token and rec.account_token != account_token:
                rec.account_token = account_token
            if "deleted" in event_type:
                rec.status = "disabled"
            else:
                rec.status = "active"
            rec.raw = payload
            db.session.commit()
            updated = True

    # If we can't match anything, just accept and return 204 so Merge doesn't retry.
    return ("", 204)

@merge_bp.route("/webhook/debug", methods=["GET"])
def merge_webhook_debug():
    """Debug endpoint to check webhook configuration and latest webhook data"""
    from services.merge_service import MERGE_WEBHOOK_SECRET
    
    debug_info = {
        "webhook_secret_configured": bool(MERGE_WEBHOOK_SECRET),
        "webhook_secret_length": len(MERGE_WEBHOOK_SECRET) if MERGE_WEBHOOK_SECRET else 0,
        "latest_webhook_data": None
    }
    
    # Try to get the most recent webhook data from any linked account
    latest_account = MergeLinkedAccount.query.order_by(MergeLinkedAccount.updated_at.desc()).first()
    if latest_account and latest_account.raw:
        debug_info["latest_webhook_data"] = latest_account.raw
    
    return jsonify(debug_info), 200 