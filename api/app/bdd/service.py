from app.bdd.connexion import Connexion
from app.bdd.prediction import Prediction


class Service_Prediction(Connexion):
    @classmethod
    def sauvegarder_prediction(cls, prediction: Prediction):
        with cls.ouvrir_connexion() as (bdd, cursor):
            cursor.execute("SELECT id FROM labels WHERE label = %s", [prediction.label])
            label_row = cursor.fetchone()

            if label_row is None:
                raise ValueError(f"Label absent de la base : {prediction.label}")

            cursor.execute(
                "INSERT INTO predictions (image, label, confiance, commentaire, modele) VALUES (%s, %s, %s, %s, %s)",
                [prediction.image, label_row["id"], prediction.confiance, prediction.commentaire, prediction.modele],
            )

            bdd.commit()
            prediction.id = cursor.lastrowid
        return prediction

    @classmethod
    def lister_predictions(cls):
        with cls.ouvrir_connexion() as (_, cursor):
            cursor.execute(
                "SELECT predictions.id as id, predictions.image as image, labels.label as label, predictions.confiance as confiance, predictions.commentaire as commentaire, predictions.modele as modele FROM predictions JOIN labels ON predictions.label = labels.id"
            )

            rows = cursor.fetchall()

            return [Prediction(**row) for row in rows]
