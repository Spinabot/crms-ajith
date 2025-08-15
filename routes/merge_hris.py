# routes/merge_hris.py
from flask import Blueprint, request, jsonify
from services.merge_client import call

hris_bp = Blueprint("hris_bp", __name__, url_prefix="/api/merge/hris")

# --- EMPLOYEES (GET, GET{id}, IGNORE)
@hris_bp.get("/employees")
def hris_employees_list():
    return jsonify(call("hris", "GET", "/employees", params=request.args))

@hris_bp.get("/employees/<uuid:id>")
def hris_employees_get(id):
    return jsonify(call("hris", "GET", f"/employees/{id}", params=request.args))

@hris_bp.post("/employees/ignore/<string:model_id>")
def hris_employees_ignore(model_id):
    return jsonify(call("hris", "POST", f"/employees/ignore/{model_id}", json={"reason": "ignored via API"}))

# --- TIME OFF (GET, POST, GET{id})
@hris_bp.get("/time-off")
def hris_timeoff_list():
    return jsonify(call("hris", "GET", "/time-off", params=request.args))

@hris_bp.post("/time-off")
def hris_timeoff_create():
    # expects fields per Merge model (employee, amount, units, request_type, start_time, end_time, etc.)
    body = {"model": request.json or {}}
    return jsonify(call("hris", "POST", "/time-off", json=body)), 201

@hris_bp.get("/time-off/<uuid:id>")
def hris_timeoff_get(id):
    return jsonify(call("hris", "GET", f"/time-off/{id}", params=request.args))

# --- TIMESHEET ENTRIES (GET, POST, GET{id})
@hris_bp.get("/timesheet-entries")
def hris_timesheets_list():
    return jsonify(call("hris", "GET", "/timesheet-entries", params=request.args))

@hris_bp.post("/timesheet-entries")
def hris_timesheets_create():
    # expects fields per Merge model (employee, hours_worked, start_time, end_time)
    body = {"model": request.json or {}}
    return jsonify(call("hris", "POST", "/timesheet-entries", json=body)), 201

@hris_bp.get("/timesheet-entries/<uuid:id>")
def hris_timesheets_get(id):
    return jsonify(call("hris", "GET", f"/timesheet-entries/{id}", params=request.args))

# --- READ-ONLY convenience (optional; add any you need)
@hris_bp.get("/companies")
def hris_companies_list():
    return jsonify(call("hris", "GET", "/companies", params=request.args))

@hris_bp.get("/groups")
def hris_groups_list():
    return jsonify(call("hris", "GET", "/groups", params=request.args))

@hris_bp.get("/locations")
def hris_locations_list():
    return jsonify(call("hris", "GET", "/locations", params=request.args))

# --- DELETE LINKED ACCOUNT (official endpoint)
@hris_bp.post("/delete-account")
def hris_delete_account():
    return jsonify(call("hris", "POST", "/delete-account", json=request.json or {}))

# --- PASSTHROUGH (to enable updates/deletes on provider where supported)
@hris_bp.post("/passthrough")
def hris_passthrough():
    """
    Body example:
    {
      "method": "PATCH",
      "path": "/employees/12345",          # provider-relative path
      "request_format": "JSON",
      "headers": {"Content-Type":"application/json"},
      "data": {"work_email": "new@ex.com"},
      "normalize_response": True
    }
    """
    return jsonify(call("hris", "POST", "/passthrough", json=request.json or {})) 