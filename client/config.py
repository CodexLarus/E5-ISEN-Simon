import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=False)

API_BASE_URL = os.getenv(
    "API_BASE_URL", f"http://127.0.0.1:{os.getenv('API_PORT', '8081')}"
).rstrip("/")
API_UPLOAD_URL = f"{API_BASE_URL}/predictions/satellite/"
API_PREDICTIONS_URL = f"{API_BASE_URL}/predictions/"
API_URL = API_UPLOAD_URL
