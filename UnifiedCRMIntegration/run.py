import os
from app import create_app
from app.config import Config

app = create_app()

if __name__ == '__main__':
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=False if Config.FLASK_ENV == "production" else True
    )