from dotenv import load_dotenv
load_dotenv()
import os
from app import create_app
from app.database import init_db

print("Loading environment variables from .env file...")
print("JOBNIMBUS_API_KEY:", os.getenv("JOBNIMBUS_API_KEY"))

app = create_app()
init_db(app)

if __name__ == "__main__":
    app.run(debug=True)
