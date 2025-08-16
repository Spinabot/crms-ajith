# controllers/bitrix24_controller.py
import os
from flask import Blueprint, request, jsonify
from models import db, ClientCRMAuth
from services.bitrix24_service import (
    CRM_NAME, BITRIX_OUTBOUND_TOKEN,
    contact_add, contact_get, contact_update, contact_delete, contact_list,
    deal_add, deal_get, deal_update, deal_delete, deal_list,
    lead_add, lead_get, lead_update, lead_delete, lead_list
)

bitrix_bp = Blueprint("bitrix", __name__, url_prefix="/api/bitrix")

# --- config for a client (save the webhook base + outbound token) ---
@bitrix_bp.route("/clients/<int:client_id>/config", methods=["POST"])
def bitrix_save_config(client_id: int):
    """
    Body: { webhook_base: "<https://.../rest/1/<token>/>", outbound_token?: "<token>" }
    """
    data = request.get_json(force=True) or {}
    wb = (data.get("webhook_base") or "").strip()
    if not wb:
        return jsonify({"error": "webhook_base is required"}), 400

    # For now, we'll store Bitrix24 config in a special way since we don't have a CRM entry yet
    # You can either create a Bitrix24 entry in the CRMs table or use this approach
    row = ClientCRMAuth.query.filter_by(client_id=client_id, crm_id=999).first()  # Temporary ID
    if not row:
        row = ClientCRMAuth(client_id=client_id, crm_id=999, credentials={})  # Temporary ID
        db.session.add(row)
    row.credentials = row.credentials or {}
    row.credentials["webhook_base"] = wb
    if data.get("outbound_token"):
        row.credentials["outbound_token"] = data.get("outbound_token")
    db.session.commit()
    return jsonify({"ok": True}), 200

@bitrix_bp.route("/clients/<int:client_id>/config/debug", methods=["GET"])
def bitrix_config_debug(client_id: int):
    row = ClientCRMAuth.query.filter_by(client_id=client_id, crm_id=999).first()  # Temporary ID
    creds = (row.credentials if row else {}) or {}
    masked = {**creds}
    if "webhook_base" in masked:
        masked["webhook_base"] = masked["webhook_base"][:30] + "...(masked)"
    if "outbound_token" in masked and masked["outbound_token"]:
        masked["outbound_token"] = "***"
    return jsonify({"client_id": client_id, "creds": masked}), 200

# --- contacts ---
@bitrix_bp.route("/clients/<int:client_id>/contacts", methods=["POST"])
def create_contact(client_id: int):
    body = request.get_json(force=True) or {}
    fields = body.get("fields") or body  # allow plain fields body
    return jsonify(contact_add(client_id, fields)), 201

@bitrix_bp.route("/clients/<int:client_id>/contacts", methods=["GET"])
def list_contacts(client_id: int):
    filter_ = request.args.to_dict(flat=True)
    select = request.args.getlist("select") or None
    # simple pass-through of filter/order/start
    order = None
    if "ORDER_BY" in filter_:
        order = {"ID": filter_.pop("ORDER_BY")}
    start = filter_.pop("start", None)
    start = int(start) if start is not None else None
    return jsonify(contact_list(client_id, filter_, select, order, start)), 200

@bitrix_bp.route("/clients/<int:client_id>/contacts/<int:contact_id>", methods=["GET"])
def get_contact(client_id: int, contact_id: int):
    return jsonify(contact_get(client_id, contact_id)), 200

@bitrix_bp.route("/clients/<int:client_id>/contacts/<int:contact_id>", methods=["PATCH"])
def update_contact(client_id: int, contact_id: int):
    body = request.get_json(force=True) or {}
    return jsonify(contact_update(client_id, contact_id, body.get("fields") or body)), 200

@bitrix_bp.route("/clients/<int:client_id>/contacts/<int:contact_id>", methods=["DELETE"])
def delete_contact(client_id: int, contact_id: int):
    return jsonify(contact_delete(client_id, contact_id)), 200

# --- deals ---
@bitrix_bp.route("/clients/<int:client_id>/deals", methods=["POST"])
def create_deal(client_id: int):
    body = request.get_json(force=True) or {}
    return jsonify(deal_add(client_id, body.get("fields") or body)), 201

@bitrix_bp.route("/clients/<int:client_id>/deals", methods=["GET"])
def list_deals(client_id: int):
    filter_ = request.args.to_dict(flat=True)
    select = request.args.getlist("select") or None
    order = None
    start = filter_.pop("start", None)
    start = int(start) if start is not None else None
    return jsonify(deal_list(client_id, filter_, select, order, start)), 200

@bitrix_bp.route("/clients/<int:client_id>/deals/<int:deal_id>", methods=["GET"])
def get_deal(client_id: int, deal_id: int):
    return jsonify(deal_get(client_id, deal_id)), 200

@bitrix_bp.route("/clients/<int:client_id>/deals/<int:deal_id>", methods=["PATCH"])
def update_deal(client_id: int, deal_id: int):
    body = request.get_json(force=True) or {}
    return jsonify(deal_update(client_id, deal_id, body.get("fields") or body)), 200

@bitrix_bp.route("/clients/<int:client_id>/deals/<int:deal_id>", methods=["DELETE"])
def delete_deal(client_id: int, deal_id: int):
    return jsonify(deal_delete(client_id, deal_id)), 200

# --- leads (optional if your Bitrix is in "simple CRM" mode) ---
@bitrix_bp.route("/clients/<int:client_id>/leads", methods=["POST"])
def create_lead(client_id: int):
    body = request.get_json(force=True) or {}
    return jsonify(lead_add(client_id, body.get("fields") or body)), 201

@bitrix_bp.route("/clients/<int:client_id>/leads", methods=["GET"])
def list_leads(client_id: int):
    filter_ = request.args.to_dict(flat=True)
    select = request.args.getlist("select") or None
    order = None
    start = filter_.pop("start", None)
    start = int(start) if start is not None else None
    return jsonify(lead_list(client_id, filter_, select, order, start)), 200

@bitrix_bp.route("/clients/<int:client_id>/leads/<int:lead_id>", methods=["GET"])
def get_lead(client_id: int, lead_id: int):
    return jsonify(lead_get(client_id, lead_id)), 200

@bitrix_bp.route("/clients/<int:client_id>/leads/<int:lead_id>", methods=["PATCH"])
def update_lead(client_id: int, lead_id: int):
    body = request.get_json(force=True) or {}
    return jsonify(lead_update(client_id, lead_id, body.get("fields") or body)), 200

@bitrix_bp.route("/clients/<int:client_id>/leads/<int:lead_id>", methods=["DELETE"])
def delete_lead(client_id: int, lead_id: int):
    return jsonify(lead_delete(client_id, lead_id)), 200

# --- outbound webhook receiver (Bitrix -> your API) ---
@bitrix_bp.route("/webhook", methods=["POST"])
def outbound_webhook():
    """
    Bitrix24 sends event payloads here.
    Verify 'application_token' against the one you configured.
    """
    payload = request.get_json(silent=True) or {}
    # Bitrix can also send form-encoded; merge in request.form if needed
    if not payload and request.form:
        payload = request.form.to_dict(flat=True)

    incoming_token = payload.get("application_token") or payload.get("auth", {}).get("application_token")
    configured = BITRIX_OUTBOUND_TOKEN or os.getenv("BITRIX_OUTBOUND_TOKEN")
    if not configured:
        # allow per-client storage too
        configured = None

    if configured and incoming_token != configured:
        return jsonify({"error": "invalid application_token"}), 401

    # Example event fields:
    # payload['event'], payload['data'], payload['ts'], payload['auth']...
    # You can route on payload.get("event") (e.g., "ONCRMCONTACTADD", "ONCRMDEALUPDATE")
    return ("", 204) 