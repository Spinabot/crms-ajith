# routes/merge_crm.py
from flask import Blueprint, request, jsonify
from services.merge_client import call

crm_bp = Blueprint("crm_bp", __name__, url_prefix="/api/merge/crm")

# --- ACCOUNTS (GET, POST, GET{id}, PATCH{id})
@crm_bp.get("/accounts")
def crm_accounts_list():
    return jsonify(call("crm", "GET", "/accounts", params=request.args))

@crm_bp.post("/accounts")
def crm_accounts_create():
    body = {"model": request.json or {}}
    return jsonify(call("crm", "POST", "/accounts", json=body)), 201

@crm_bp.get("/accounts/<uuid:id>")
def crm_accounts_get(id):
    return jsonify(call("crm", "GET", f"/accounts/{id}", params=request.args))

@crm_bp.patch("/accounts/<uuid:id>")
def crm_accounts_update(id):
    body = {"model": request.json or {}}
    return jsonify(call("crm", "PATCH", f"/accounts/{id}", json=body))

# --- CONTACTS (GET, POST, GET{id}, PATCH{id}, IGNORE)
@crm_bp.get("/contacts")
def crm_contacts_list():
    return jsonify(call("crm", "GET", "/contacts", params=request.args))

@crm_bp.post("/contacts")
def crm_contacts_create():
    body = {"model": request.json or {}}
    return jsonify(call("crm", "POST", "/contacts", json=body)), 201

@crm_bp.get("/contacts/<uuid:id>")
def crm_contacts_get(id):
    return jsonify(call("crm", "GET", f"/contacts/{id}", params=request.args))

@crm_bp.patch("/contacts/<uuid:id>")
def crm_contacts_update(id):
    body = {"model": request.json or {}}
    return jsonify(call("crm", "PATCH", f"/contacts/{id}", json=body))

@crm_bp.post("/contacts/ignore/<string:model_id>")
def crm_contacts_ignore(model_id):
    # Marks a remote record as ignored so Merge won't sync it again.
    return jsonify(call("crm", "POST", f"/contacts/ignore/{model_id}", json={"reason": "ignored via API"}))

# --- LEADS (GET, POST, GET{id})
@crm_bp.get("/leads")
def crm_leads_list():
    return jsonify(call("crm", "GET", "/leads", params=request.args))

@crm_bp.post("/leads")
def crm_leads_create():
    body = {"model": request.json or {}}
    return jsonify(call("crm", "POST", "/leads", json=body)), 201

@crm_bp.get("/leads/<uuid:id>")
def crm_leads_get(id):
    return jsonify(call("crm", "GET", f"/leads/{id}", params=request.args))

# --- OPPORTUNITIES (GET, POST, GET{id}, PATCH{id})
@crm_bp.get("/opportunities")
def crm_opps_list():
    return jsonify(call("crm", "GET", "/opportunities", params=request.args))

@crm_bp.post("/opportunities")
def crm_opps_create():
    body = {"model": request.json or {}}
    return jsonify(call("crm", "POST", "/opportunities", json=body)), 201

@crm_bp.get("/opportunities/<uuid:id>")
def crm_opps_get(id):
    return jsonify(call("crm", "GET", f"/opportunities/{id}", params=request.args))

@crm_bp.patch("/opportunities/<uuid:id>")
def crm_opps_update(id):
    body = {"model": request.json or {}}
    return jsonify(call("crm", "PATCH", f"/opportunities/{id}", json=body))

# --- TASKS (GET, POST, GET{id}, PATCH{id})
@crm_bp.get("/tasks")
def crm_tasks_list():
    return jsonify(call("crm", "GET", "/tasks", params=request.args))

@crm_bp.post("/tasks")
def crm_tasks_create():
    body = {"model": request.json or {}}
    return jsonify(call("crm", "POST", "/tasks", json=body)), 201

@crm_bp.get("/tasks/<uuid:id>")
def crm_tasks_get(id):
    return jsonify(call("crm", "GET", f"/tasks/{id}", params=request.args))

@crm_bp.patch("/tasks/<uuid:id>")
def crm_tasks_update(id):
    body = {"model": request.json or {}}
    return jsonify(call("crm", "PATCH", f"/tasks/{id}", json=body))

# --- NOTES (GET, POST, GET{id})  (no PATCH in unified)
@crm_bp.get("/notes")
def crm_notes_list():
    return jsonify(call("crm", "GET", "/notes", params=request.args))

@crm_bp.post("/notes")
def crm_notes_create():
    body = {"model": request.json or {}}
    return jsonify(call("crm", "POST", "/notes", json=body)), 201

@crm_bp.get("/notes/<uuid:id>")
def crm_notes_get(id):
    return jsonify(call("crm", "GET", f"/notes/{id}", params=request.args))

# --- ENGAGEMENTS (GET, POST, GET{id}, PATCH{id})
@crm_bp.get("/engagements")
def crm_eng_list():
    return jsonify(call("crm", "GET", "/engagements", params=request.args))

@crm_bp.post("/engagements")
def crm_eng_create():
    body = {"model": request.json or {}}
    return jsonify(call("crm", "POST", "/engagements", json=body)), 201

@crm_bp.get("/engagements/<uuid:id>")
def crm_eng_get(id):
    return jsonify(call("crm", "GET", f"/engagements/{id}", params=request.args))

@crm_bp.patch("/engagements/<uuid:id>")
def crm_eng_update(id):
    body = {"model": request.json or {}}
    return jsonify(call("crm", "PATCH", f"/engagements/{id}", json=body))

# --- USERS (GET, GET{id}, IGNORE)
@crm_bp.get("/users")
def crm_users_list():
    return jsonify(call("crm", "GET", "/users", params=request.args))

@crm_bp.get("/users/<uuid:id>")
def crm_users_get(id):
    return jsonify(call("crm", "GET", f"/users/{id}", params=request.args))

@crm_bp.post("/users/ignore/<string:model_id>")
def crm_users_ignore(model_id):
    return jsonify(call("crm", "POST", f"/users/ignore/{model_id}", json={"reason": "ignored via API"}))

# --- DELETE LINKED ACCOUNT (official endpoint)
@crm_bp.post("/delete-account")
def crm_delete_account():
    return jsonify(call("crm", "POST", "/delete-account", json=request.json or {}))

# --- PASSTHROUGH (to enable DELETE or provider-specific fields)
@crm_bp.post("/passthrough")
def crm_passthrough():
    """
    Body example:
    {
      "method": "DELETE",
      "path": "/crm/v3/objects/contacts/12345",  # provider-relative path
      "request_format": "JSON",
      "headers": {"Content-Type":"application/json"},
      "data": {"archived": true},
      "normalize_response": True
    }
    """
    return jsonify(call("crm", "POST", "/passthrough", json=request.json or {})) 