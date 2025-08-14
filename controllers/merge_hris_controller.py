# controllers/merge_hris_controller.py
from flask import Blueprint, request, jsonify
from models import MergeLinkedAccount
from services.merge_service import (
    MergeServiceError,
    hris_list_employees, hris_get_employee,
    hris_list_employments, hris_list_locations, hris_list_groups,
    hris_list_time_off, hris_get_time_off, hris_create_time_off,
    hris_list_timesheet_entries, hris_get_timesheet_entry, hris_create_timesheet_entry,
    hris_passthrough
)

hris_bp = Blueprint("merge_hris", __name__, url_prefix="/api/merge/hris")

def _resolve_account_token(client_id: int, explicit: str | None):
    if explicit:
        return explicit
    rec = MergeLinkedAccount.query.filter_by(client_id=client_id, status="active").first()
    if not rec:
        return None
    return rec.account_token

# ---------- READS ----------
@hris_bp.route("/clients/<int:client_id>/employees", methods=["GET"])
def hris_employees(client_id: int):
    token = _resolve_account_token(client_id, request.args.get("account_token"))
    if not token:
        return jsonify({"error": "No Merge linked account found for client"}), 404
    params = {k: v for k, v in request.args.items() if k not in ("account_token",)}
    try:
        return jsonify(hris_list_employees(token, params)), 200
    except MergeServiceError as e:
        return jsonify({"error": str(e)}), 502

@hris_bp.route("/clients/<int:client_id>/employees/<string:employee_id>", methods=["GET"])
def hris_employee_detail(client_id: int, employee_id: str):
    token = _resolve_account_token(client_id, request.args.get("account_token"))
    if not token:
        return jsonify({"error": "No Merge linked account found for client"}), 404
    try:
        return jsonify(hris_get_employee(token, employee_id)), 200
    except MergeServiceError as e:
        return jsonify({"error": str(e)}), 502

@hris_bp.route("/clients/<int:client_id>/employments", methods=["GET"])
def hris_employments(client_id: int):
    token = _resolve_account_token(client_id, request.args.get("account_token"))
    if not token:
        return jsonify({"error": "No Merge linked account found for client"}), 404
    params = {k: v for k, v in request.args.items() if k not in ("account_token",)}
    try:
        return jsonify(hris_list_employments(token, params)), 200
    except MergeServiceError as e:
        return jsonify({"error": str(e)}), 502

@hris_bp.route("/clients/<int:client_id>/locations", methods=["GET"])
def hris_locations(client_id: int):
    token = _resolve_account_token(client_id, request.args.get("account_token"))
    if not token:
        return jsonify({"error": "No Merge linked account found for client"}), 404
    params = {k: v for k, v in request.args.items() if k not in ("account_token",)}
    try:
        return jsonify(hris_list_locations(token, params)), 200
    except MergeServiceError as e:
        return jsonify({"error": str(e)}), 502

@hris_bp.route("/clients/<int:client_id>/groups", methods=["GET"])
def hris_groups(client_id: int):
    token = _resolve_account_token(client_id, request.args.get("account_token"))
    if not token:
        return jsonify({"error": "No Merge linked account found for client"}), 404
    params = {k: v for k, v in request.args.items() if k not in ("account_token",)}
    try:
        return jsonify(hris_list_groups(token, params)), 200
    except MergeServiceError as e:
        return jsonify({"error": str(e)}), 502

# ---------- WRITES (Unified) ----------
@hris_bp.route("/clients/<int:client_id>/time-off", methods=["GET", "POST"])
def hris_time_off(client_id: int):
    token = _resolve_account_token(client_id, request.args.get("account_token") or (request.json or {}).get("account_token"))
    if not token:
        return jsonify({"error": "No Merge linked account found for client"}), 404

    if request.method == "GET":
        params = {k: v for k, v in request.args.items() if k not in ("account_token",)}
        try:
            return jsonify(hris_list_time_off(token, params)), 200
        except MergeServiceError as e:
            return jsonify({"error": str(e)}), 502

    # POST create time off
    body = request.get_json(force=True) or {}
    model = body.get("model") or body.get("time_off") or {}
    qs = body.get("query") or {}
    if not model:
        return jsonify({"error": "Provide a 'model' body with time off fields"}), 400
    try:
        return jsonify(hris_create_time_off(token, model, qs)), 201
    except MergeServiceError as e:
        return jsonify({"error": str(e)}), 502

@hris_bp.route("/clients/<int:client_id>/time-off/<string:id_>", methods=["GET"])
def hris_time_off_detail(client_id: int, id_: str):
    token = _resolve_account_token(client_id, request.args.get("account_token"))
    if not token:
        return jsonify({"error": "No Merge linked account found for client"}), 404
    try:
        return jsonify(hris_get_time_off(token, id_)), 200
    except MergeServiceError as e:
        return jsonify({"error": str(e)}), 502

@hris_bp.route("/clients/<int:client_id>/timesheet-entries", methods=["GET", "POST"])
def hris_timesheet_entries(client_id: int):
    token = _resolve_account_token(client_id, request.args.get("account_token") or (request.json or {}).get("account_token"))
    if not token:
        return jsonify({"error": "No Merge linked account found for client"}), 404

    if request.method == "GET":
        params = {k: v for k, v in request.args.items() if k not in ("account_token",)}
        try:
            return jsonify(hris_list_timesheet_entries(token, params)), 200
        except MergeServiceError as e:
            return jsonify({"error": str(e)}), 502

    body = request.get_json(force=True) or {}
    model = body.get("model") or body.get("timesheet_entry") or {}
    qs = body.get("query") or {}
    if not model:
        return jsonify({"error": "Provide a 'model' body with timesheet entry fields"}), 400
    try:
        return jsonify(hris_create_timesheet_entry(token, model, qs)), 201
    except MergeServiceError as e:
        return jsonify({"error": str(e)}), 502

@hris_bp.route("/clients/<int:client_id>/timesheet-entries/<string:id_>", methods=["GET"])
def hris_timesheet_entry_detail(client_id: int, id_: str):
    token = _resolve_account_token(client_id, request.args.get("account_token"))
    if not token:
        return jsonify({"error": "No Merge linked account found for client"}), 404
    try:
        return jsonify(hris_get_timesheet_entry(token, id_)), 200
    except MergeServiceError as e:
        return jsonify({"error": str(e)}), 502

# ---------- PASSTHROUGH (use for PATCH/DELETE or vendor-specific CRUD) ----------
@hris_bp.route("/clients/<int:client_id>/passthrough", methods=["POST"])
def hris_passthrough_proxy(client_id: int):
    """
    Body:
    {
      "account_token": "...",           # optional; falls back to first active for client
      "method": "PATCH|DELETE|POST|GET",
      "path": "/employees/123",         # vendor relative path
      "data": {...},                    # optional body
      "request_format": "JSON",         # or XML, MULTIPART
      "headers": {...},                 # optional extra headers
      "base_url_override": "https://api.vendor.com",  # optional if Merge knows it
      "run_async": false
    }
    """
    body = request.get_json(force=True) or {}
    token = _resolve_account_token(client_id, body.get("account_token"))
    if not token:
        return jsonify({"error": "No Merge linked account found for client"}), 404
    try:
        result = hris_passthrough(
            token,
            method=body.get("method", "GET"),
            path=body.get("path", "/"),
            data=body.get("data"),
            request_format=body.get("request_format", "JSON"),
            headers=body.get("headers"),
            base_url_override=body.get("base_url_override"),
            run_async=bool(body.get("run_async", False)),
        )
        return jsonify(result), 200
    except MergeServiceError as e:
        return jsonify({"error": str(e)}), 502 