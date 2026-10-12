from pydantic import BaseModel

class Prediction(BaseModel) :
    id: int | None = None
    image : str
    label : str
    commentaire : str
    modele : str
