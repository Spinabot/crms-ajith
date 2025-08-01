from flask import jsonify, request
from services.jobber_service import fetch_clients, fetch_jobs, create_client

def get_jobber_clients():
    """
    Get all clients from Jobber
    
    ---
    tags:
      - Jobber
    responses:
      200:
        description: A list of Jobber clients
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: string
                description: Client ID
              first_name:
                type: string
                description: Client's first name
              last_name:
                type: string
                description: Client's last name
              email:
                type: string
                description: Client's email address
      500:
        description: Internal server error
    """
    try:
        data = fetch_clients()
        if data and "clients" in data and "nodes" in data["clients"]:
            # Transform the data to ensure it's JSON serializable
            clients = []
            for client in data["clients"]["nodes"]:
                client_data = {
                    "id": str(client.get("id", "")),
                    "first_name": client.get("firstName", ""),
                    "last_name": client.get("lastName", ""),
                    "email": "",
                    "company_name": client.get("companyName", "")
                }
                # Extract email from the emails array
                if client.get("emails") and len(client["emails"]) > 0:
                    for email in client["emails"]:
                        if email.get("primary"):
                            client_data["email"] = email.get("address", "")
                            break
                    if not client_data["email"] and client["emails"]:
                        client_data["email"] = client["emails"][0].get("address", "")
                
                clients.append(client_data)
            
            return {"success": True, "message": "Clients retrieved successfully", "data": clients}, 200
        else:
            return {"success": False, "message": "No client data found", "data": []}, 200
    except Exception as e:
        return {"success": False, "message": f"Error fetching clients: {str(e)}", "data": None}, 500

def get_jobber_jobs():
    """
    Get all jobs from Jobber
    
    ---
    tags:
      - Jobber
    responses:
      200:
        description: A list of Jobber jobs
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: string
                description: Job ID
              title:
                type: string
                description: Job title
              status:
                type: string
                description: Job status
      500:
        description: Internal server error
    """
    try:
        data = fetch_jobs()
        if data and "jobs" in data and "nodes" in data["jobs"]:
            # Transform the data to ensure it's JSON serializable
            jobs = []
            for job in data["jobs"]["nodes"]:
                job_data = {
                    "id": str(job.get("id", "")),
                    "job_number": job.get("jobNumber", ""),
                    "title": job.get("title", ""),
                    "status": job.get("status", "")
                }
                jobs.append(job_data)
            
            return {"success": True, "message": "Jobs retrieved successfully", "data": jobs}, 200
        else:
            return {"success": False, "message": "No job data found", "data": []}, 200
    except Exception as e:
        return {"success": False, "message": f"Error fetching jobs: {str(e)}", "data": None}, 500

def post_jobber_client():
    """
    Create a new client in Jobber
    
    ---
    tags:
      - Jobber
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - first_name
            - last_name
            - email
          properties:
            first_name:
              type: string
              description: Client's first name
            last_name:
              type: string
              description: Client's last name
            email:
              type: string
              description: Client's email address
            company_name:
              type: string
              description: Client's company name (optional)
    responses:
      201:
        description: Client created successfully
        schema:
          type: object
          properties:
            id:
              type: string
              description: Created client ID
            first_name:
              type: string
            last_name:
              type: string
            email:
              type: string
      400:
        description: Bad request - validation error
    """
    try:
        body = request.json
        if not body:
            return {"success": False, "message": "Request body is required", "data": None}, 400
        
        # Validate required fields
        required_fields = ["first_name", "last_name", "email"]
        for field in required_fields:
            if field not in body or not body[field]:
                return {"success": False, "message": f"Field '{field}' is required", "data": None}, 400
        
        client = create_client(
            first_name=body["first_name"],
            last_name=body["last_name"],
            email=body["email"],
            company_name=body.get("company_name")
        )
        
        # Transform the response to ensure it's JSON serializable
        client_data = {
            "id": str(client.get("id", "")),
            "first_name": client.get("firstName", ""),
            "last_name": client.get("lastName", "")
        }
        
        return {"success": True, "message": "Client created successfully", "data": client_data}, 201
    except Exception as e:
        return {"success": False, "message": f"Error creating client: {str(e)}", "data": None}, 400
