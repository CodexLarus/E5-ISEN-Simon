import os
from pathlib import Path

from dotenv import load_dotenv

API_DIR = Path(__file__).resolve().parents[1]
# Chemin explicite : le chargement ne dépend pas du répertoire courant.
# Les variables injectées par Docker restent prioritaires.
load_dotenv(API_DIR.parent / ".env", override=False)

UPLOAD_FOLDER = Path(os.getenv("UPLOAD_FOLDER", "satelite_images"))
if not UPLOAD_FOLDER.is_absolute():
    UPLOAD_FOLDER = API_DIR / UPLOAD_FOLDER

LABELS = {0: "nuageux", 1: "désert", 2: "forêt", 3: "mer"}

DB_NAME = os.environ["MYSQL_DATABASE"]
DB_USER = os.environ["MYSQL_USER"]
DB_PASSWORD = os.environ["MYSQL_PASSWORD"]
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
