import json
import os

import streamlit as st
import requests

# Configuration des URLs de l'API
from config import API_UPLOAD_URL, API_PREDICTIONS_URL

# Titre de l'application
st.title("🛰️ Application CNN - Classification d'Images Satellites")

# Ajout de la **sidebar** pour la navigation
st.sidebar.title("🔍 Navigation")
menu = st.sidebar.radio("Navigation", ["📤 Upload d'image", "📋 Voir les prédictions", "Dashboard"])

SEUIL_CONFIANCE = float(os.getenv("SEUIL_CONFIANCE", "0.60"))

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
                    confiance = prediction.get("confiance")
                    if confiance is not None:
                        st.write(f"Confiance : {confiance:.1%}")
                    st.write(f"📝 **Commentaire** : {prediction['commentaire']}")
                    st.write(f"🛠️ **Modèle utilisé** : {prediction['modele']}")
        else:
            st.info("Aucune prédiction enregistrée pour le moment.")

    except requests.exceptions.RequestException as e:
        st.error(f"❌ Erreur lors de la récupération des prédictions : {e}")

# Page : Dashboard de suivi
elif menu == "Dashboard":
    st.header("Dashboard de suivi de l'application")

    try:
        response = requests.get(API_PREDICTIONS_URL, timeout=(5, 30))
        response.raise_for_status()
        predictions = response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erreur lors de la récupération des prédictions : {e}")
        predictions = []

    if not predictions:
        st.info("Aucune prédiction enregistrée pour le moment.")
    else:
        confiances = [p["confiance"] for p in predictions if p.get("confiance") is not None]
        confiance_moyenne = sum(confiances) / len(confiances) if confiances else None
        nb_faibles = sum(1 for c in confiances if c < SEUIL_CONFIANCE)

        col1, col2, col3 = st.columns(3)
        col1.metric("Prédictions enregistrées", len(predictions))
        col2.metric(
            "Confiance moyenne du modèle",
            f"{confiance_moyenne:.1%}" if confiance_moyenne is not None else "N/A",
        )
        col3.metric("Prédictions peu fiables", nb_faibles)

        if confiance_moyenne is not None and confiance_moyenne < SEUIL_CONFIANCE:
            st.error(
                f"Alerte : la confiance moyenne du modèle ({confiance_moyenne:.1%}) "
                f"est passée sous le seuil de {SEUIL_CONFIANCE:.0%}. "
                "Le modèle pourrait nécessiter une vérification (dérive, images inhabituelles)."
            )
        elif confiance_moyenne is not None:
            st.success(f"Modèle sain : confiance moyenne de {confiance_moyenne:.1%}.")

        st.subheader("Répartition des prédictions par classe")
        repartition = {}
        for p in predictions:
            repartition[p["label"]] = repartition.get(p["label"], 0) + 1
        st.bar_chart(repartition)

        st.subheader("Confiance moyenne par classe")
        conf_par_classe = {}
        for p in predictions:
            c = p.get("confiance")
            if c is not None:
                conf_par_classe.setdefault(p["label"], []).append(c)
        if conf_par_classe:
            tableau = {
                label: [f"{sum(valeurs) / len(valeurs):.1%}", len(valeurs)]
                for label, valeurs in conf_par_classe.items()
            }
            st.table(
                {
                    "Classe": list(tableau.keys()),
                    "Confiance moyenne": [v[0] for v in tableau.values()],
                    "Nombre": [v[1] for v in tableau.values()],
                }
            )
        else:
            st.caption("Confiance non disponible pour les prédictions enregistrées.")
