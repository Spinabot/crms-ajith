import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("[TEST] Starting app initialization test")
try:
    from app import create_app
    print("[TEST] Imported create_app successfully")
    app = create_app()
    print("[TEST] App created successfully: ", app)
except Exception as e:
    print(f"[TEST] Exception during app initialization: {e}")