# Production-ready Jobber OAuth 2.0 Server
import os
import time
import requests
from flask import Flask, redirect, request, jsonify
from dotenv import load_dotenv

load_dotenv()

# Your credentials
CLIENT_ID = os.getenv("JOBBER_CLIENT_ID", "6c6a5fb3-9c6b-4887-80cb-c65f1cc2825a")
CLIENT_SECRET = os.getenv("JOBBER_CLIENT_SECRET", "dddff56b393da10a8519f36e4d7b13e273c83a80c1044f6d41e4d16aa92645b4")
REDIRECT_URI = os.getenv("JOBBER_REDIRECT_URI", "http://localhost:5001/api/jobber/callback")

TOKEN_URL = "https://api.getjobber.com/api/oauth/token"

def exchange_token(data: dict):
    """Exchange authorization code for access token"""
    resp = requests.post(TOKEN_URL, data=data)
    resp.raise_for_status()
    return resp.json()

def store_tokens(tokens):
    """Store tokens in .env file"""
    with open(".env", "a") as f:
        f.write(f"\nJOBBER_ACCESS_TOKEN={tokens['access_token']}")
        if tokens.get('refresh_token'):
            f.write(f"\nJOBBER_REFRESH_TOKEN={tokens['refresh_token']}")
        expires = time.time() + int(tokens.get("expires_in", 3600))
        f.write(f"\nJOBBER_TOKEN_EXPIRES_AT={int(expires)}")

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <h1>🔐 Jobber OAuth 2.0 Server</h1>
    <p>Click the button below to authorize with Jobber:</p>
    <a href="/jobber/auth" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
        Connect to Jobber
    </a>
    <br><br>
    <p><strong>Status:</strong> Ready to authorize</p>
    """

@app.route("/jobber/auth")
def auth():
    """Step 1: Redirect user to Jobber authorization page"""
    auth_url = (
        f"https://api.getjobber.com/api/oauth/authorize"
        f"?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
    )
    return redirect(auth_url)

@app.route("/jobber/callback")
def callback():
    """Step 2: Handle the redirect from Jobber with authorization code"""
    code = request.args.get("code")
    if not code:
        return "Error: No authorization code provided.", 400

    try:
        # Step 3: Exchange the code for an access token
        tokens = exchange_token({
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code",
            "code": code
        })
        
        # Store tokens in .env file
        store_tokens(tokens)
        
        return f"""
        <h1>✅ Authorization Successful!</h1>
        <p><strong>Access Token:</strong> <code>{tokens['access_token']}</code></p>
        <p><strong>Token Type:</strong> {tokens.get('token_type', 'Bearer')}</p>
        <p><strong>Expires In:</strong> {tokens.get('expires_in', 'Unknown')} seconds</p>
        <p><strong>Refresh Token:</strong> {tokens.get('refresh_token', 'None')}</p>
        <br>
        <p>✅ Tokens have been saved to your .env file!</p>
        <p>You can now:</p>
        <ul>
            <li>Stop this OAuth server (Ctrl+C)</li>
            <li>Start your main Flask app: <code>python3 app.py</code></li>
            <li>Test Jobber endpoints in Swagger UI</li>
        </ul>
        """
    except Exception as e:
        return f"Error exchanging code for token: {str(e)}", 500

@app.route("/jobber/refresh")
def refresh():
    """Refresh access token using refresh token"""
    refresh_token = os.getenv("JOBBER_REFRESH_TOKEN")
    if not refresh_token:
        return "No refresh token found. Please re-authorize.", 400

    try:
        tokens = exchange_token({
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        })
        store_tokens(tokens)
        return jsonify({"success": True, "message": "Token refreshed successfully", "tokens": tokens})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    print("🚀 Starting Jobber OAuth Server on port 5002...")
    print("📱 Visit: http://localhost:5002/ to authorize with Jobber")
    app.run(debug=True, port=5002)
