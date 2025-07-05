import os
from app import create_app
from app.extensions import db, migrate

# Set Flask app environment variable
os.environ['FLASK_APP'] = 'app:create_app'

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
