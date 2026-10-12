from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4
import logging
import shutil
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import JSONResponse
from mysql.connector import Error as DatabaseError
from PIL import Image, UnidentifiedImageError
from app.modele import cnn
from app.config import UPLOAD_FOLDER
from app.bdd.service import Service_Prediction
from app.bdd.prediction import Prediction

@asynccontextmanager
async def lifespan(app):
    Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)
    cnn.get_model()
    yield


app = FastAPI(lifespan=lifespan)


@app.exception_handler(DatabaseError)
async def database_error(request: Request, exc: DatabaseError):
    logging.getLogger(__name__).error("Erreur MySQL : %s", exc)
    return JSONResponse(status_code=503, content={"detail": "Base de données indisponible"})


@app.get("/")
def index():
    return "API Prediction!"

@app.post("/predictions/satellite/")
def upload_image(file: UploadFile = File(...)):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png"}:
        file.file.close()
        raise HTTPException(status_code=400, detail="Format non supporté")
    file_path = Path(UPLOAD_FOLDER) / f"{uuid4().hex}{suffix}"
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        try:
            with Image.open(file_path) as image:
                image.verify()
        except (UnidentifiedImageError, OSError, SyntaxError, Image.DecompressionBombError) as exc:
            raise HTTPException(status_code=400, detail="Image invalide") from exc
        label = cnn.predict_image(file_path)
        prediction = Prediction(image=str(file_path), label=label, commentaire="OK", modele="CNN")
        Service_Prediction.sauvegarder_prediction(prediction)
        return {"prediction": prediction}
    except Exception:
        file_path.unlink(missing_ok=True)
        raise
    finally:
        file.file.close()


@app.get("/predictions/", response_model=list[Prediction])
def list_predictions():
    return Service_Prediction.lister_predictions()
