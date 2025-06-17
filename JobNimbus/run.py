from app import create_app
from app.database import init_db

app = create_app()
init_db(app)

if __name__ == "__main__":
    app.run(debug=True)
