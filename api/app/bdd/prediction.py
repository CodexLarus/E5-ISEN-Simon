from pydantic import BaseModel

class Prediction(BaseModel) :
    id: int | None = None
    image : str
    label : str
    confiance : float | None = None
    commentaire : str
    modele : str
