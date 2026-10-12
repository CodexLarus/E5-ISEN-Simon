import json

import streamlit as st
import requests

# Configuration des URLs de l'API
from config import API_UPLOAD_URL, API_PREDICTIONS_URL

# Titre de l'application
st.title("🛰️ Application CNN - Classification d'Images Satellites")

# Ajout de la **sidebar** pour la navigation
st.sidebar.title("🔍 Navigation")
menu = st.sidebar.radio("Navigation", ["📤 Upload d'image", "📋 Voir les prédictions"])

# Télécharger les prédictions indépendamment de la page affichée.
try:
    pourfichier = requests.post(API_PREDICTIONS_URL, timeout=(5, 30))
    pourfichier.raise_for_status()
    predictionsjson = pourfichier.json()
    st.sidebar.download_button(
        label="Télécharger le JSON",
        data=json.dumps(predictionsjson, ensure_ascii=False, indent=2).encode("utf-8"),
        file_name="predictions.json",
        mime="application/json",
    )
except requests.exceptions.RequestException as e:
    st.sidebar.error(f"Erreur lors du chargement du JSON : {e}")

# Page : Upload d'image
if menu == "📤 Upload d'image":
    st.header("📤 Upload d'une image et envoi vers l'API")

    # Formulaire de dépôt de fichier
    with st.form("upload_form"):
        uploaded_file = st.file_uploader("Choisissez une image", type=["jpg", "jpeg", "png"])
        submit_button = st.form_submit_button("Envoyer")

    # Si le formulaire est soumis
    if submit_button:
        if uploaded_file is not None:
            # Afficher l'image uploadée
            st.image(uploaded_file, caption="Image envoyée", use_container_width=True)

            # Préparer le fichier pour l'envoi à l'API
            files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}

            # Envoie la requête POST à l'API
            try:
                response = requests.post(API_UPLOAD_URL, files=files, timeout=(5, 120))
                response.raise_for_status()  # Vérifie si l'API retourne une erreur HTTP

                # Affiche la réponse de l'API
                st.success("✅ Réponse de l'API :")
                st.json(response.json())

            except requests.exceptions.RequestException as e:
                st.error(f"❌ Erreur lors de la communication avec l'API : {e}")
        else:
            st.warning("⚠️ Veuillez sélectionner une image avant d'envoyer.")

# Page : Voir les prédictions enregistrées
elif menu == "📋 Voir les prédictions":
    st.header("📋 Liste des prédictions enregistrées")

    # Récupérer les prédictions depuis l'API
    try:
        response = requests.get(API_PREDICTIONS_URL, timeout=(5, 30))
        response.raise_for_status()
        predictions = response.json()

        # Vérifier s'il y a des prédictions
        if predictions:
            for prediction in predictions:
                with st.expander(f"📌 Prédiction {prediction['id']}"):
                    st.write(prediction["image"])
                    st.write(f"🔹 **Label prédit** : {prediction['label']}")
                    st.write(f"📝 **Commentaire** : {prediction['commentaire']}")
                    st.write(f"🛠️ **Modèle utilisé** : {prediction['modele']}")
        else:
            st.info("Aucune prédiction enregistrée pour le moment.")
    
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Erreur lors de la récupération des prédictions : {e}")
