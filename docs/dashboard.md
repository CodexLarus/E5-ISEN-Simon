# Documentation du dashboard de suivi

## Objectif

Le dashboard permet de surveiller l'application de classification d'images
satellites après la correction du ticket 2. Il répond à la compétence C20
(surveiller une application d'intelligence artificielle) : il donne une vue
rapide de l'activité de l'application et de l'état de santé du modèle.

## Où le trouver

Le dashboard est une page du client Streamlit, accessible depuis le menu de
navigation, à l'entrée Dashboard (http://localhost:8501).

Il n'ajoute aucun composant d'infrastructure : il réutilise le client existant
et l'API déjà en place.

## Choix de la technologie

Le dashboard est intégré directement dans le client Streamlit de l'application,
plutôt que dans un outil externe de type Grafana. Les raisons de ce choix sont
les suivantes.

L'application utilise déjà Streamlit pour le client : garder la même technologie
évite d'ajouter un service, une base de métriques et une configuration
supplémentaires. Les données à afficher sont déjà exposées par l'API, via
l'endpoint GET /predictions/, donc le dashboard se contente de les lire et de
les agréger côté affichage. La mise en place et la maintenance restent simples
et proportionnées au besoin de l'exercice.

## Choix des métriques

Le dashboard affiche quatre informations.

Le nombre de prédictions enregistrées suit l'activité de l'application, c'est à
dire le volume d'utilisation. La confiance moyenne du modèle est la métrique de
suivi du modèle. Le nombre de prédictions peu fiables compte les prédictions
dont la confiance est sous le seuil. Enfin, la répartition par classe et la
confiance moyenne par classe permettent de repérer un déséquilibre entre les
classes, ou une classe sur laquelle le modèle est systématiquement peu sûr.

La confiance est la probabilité de la classe prédite, obtenue en appliquant un
softmax sur la sortie du réseau. C'est un bon indicateur de suivi : si la
confiance moyenne baisse dans le temps, cela peut signaler une dérive du modèle
ou des images en entrée différentes de celles vues à l'entraînement.

## Mise à jour des indicateurs

Les indicateurs ne sont pas figés. À chaque affichage de la page, le client
appelle l'API, qui relit les prédictions en base de données. Les valeurs
reflètent donc l'état réel de la base au moment de la consultation. Une nouvelle
prédiction envoyée depuis la page d'upload apparaît dès le rechargement du
dashboard.

## Alertes

Un seuil de confiance est fixé à 0,60 (60 %), partagé entre l'API et le
dashboard.

Côté API, chaque prédiction est journalisée avec son label, sa confiance et sa
durée de traitement. Si la confiance est inférieure au seuil, un avertissement
de niveau WARNING est écrit dans les logs. Ces logs constituent les contrôles
qui remontent des informations sur le fonctionnement du code.

Côté dashboard, si la confiance moyenne du modèle passe sous le seuil, un
bandeau d'alerte rouge invite à vérifier le modèle. Sinon, un bandeau vert
confirme que le modèle est sain.
