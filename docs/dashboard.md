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

## Installation et configuration

Le suivi ne demande aucune dépendance supplémentaire. La journalisation utilise
le module logging de la bibliothèque standard Python, et le dashboard utilise
Streamlit, déjà présent dans les dépendances du client. Il suffit de lancer
l'application comme d'habitude :

```
docker compose up -d
```

Les seuils d'alerte sont réglables par variables d'environnement, transmises aux
conteneurs par docker-compose.yml :

- SEUIL_CONFIANCE : seuil de confiance, 0.60 par défaut (API et dashboard) ;
- SEUIL_DUREE_MS : durée maximale d'une prédiction en millisecondes, 1000 par
  défaut (API).

Pour modifier un seuil, on le définit au lancement, par exemple :

```
SEUIL_CONFIANCE=0.75 docker compose up -d
```

Les journaux de l'API se consultent avec :

```
docker compose logs -f web
```

## Choix de la technologie

Le dashboard est intégré directement dans le client Streamlit de l'application,
plutôt que dans un outil externe de type Grafana.

L'application utilise déjà Streamlit pour le client : garder la même technologie
évite d'ajouter un service, une base de métriques et une configuration
supplémentaires. Les données à afficher sont déjà exposées par l'API, via
l'endpoint GET /predictions/, donc le dashboard se contente de les lire et de
les agréger côté affichage. Pour les alertes, les avertissements écrits dans les
journaux de l'API suffisent à l'échelle de ce projet.

## Métriques et seuils

Le nombre de prédictions enregistrées suit l'activité de l'application. Il n'a
pas de seuil : c'est une information de contexte.

La confiance du modèle est la métrique de suivi du modèle. C'est la probabilité
de la classe prédite, obtenue en appliquant un softmax sur la sortie du réseau.
Seuil : 0.60. En dessous, la prédiction est considérée comme peu fiable.

La durée de traitement d'une prédiction suit la performance de l'API. Seuil :
1000 ms. Au-delà, la prédiction est considérée comme lente.

La répartition par classe et la confiance moyenne par classe permettent de
repérer un déséquilibre entre les classes, ou une classe sur laquelle le modèle
est systématiquement peu sûr. Elles n'ont pas de seuil automatique et se lisent
sur le dashboard.

## Mise à jour des indicateurs

Les indicateurs ne sont pas figés. À chaque affichage de la page, le client
appelle l'API, qui relit les prédictions en base de données. Les valeurs
reflètent donc l'état réel de la base au moment de la consultation.

## Alertes

Côté API, chaque prédiction est journalisée avec son label, sa confiance et sa
durée de traitement. Un avertissement de niveau WARNING est écrit dans les
journaux si la confiance passe sous SEUIL_CONFIANCE, ou si la durée dépasse
SEUIL_DUREE_MS.

Côté dashboard, si la confiance moyenne du modèle passe sous le seuil, un
bandeau rouge invite à vérifier le modèle. Sinon, un bandeau vert confirme que
le modèle est sain.

## Tester les alertes

Avec les images de test, le modèle répond avec une confiance proche de 100 %,
donc l'alerte de confiance ne se déclenche pas en usage normal. Pour vérifier la
chaîne d'alerte, on relance l'application avec des seuils volontairement
stricts :

```
SEUIL_CONFIANCE=0.999 SEUIL_DUREE_MS=5 docker compose up -d
```

On envoie une image depuis le client, puis on constate les avertissements dans
`docker compose logs web` et le bandeau rouge sur le dashboard. On relance
ensuite sans ces variables pour revenir aux seuils normaux.

## Limite constatée

Le modèle se montre très sûr de lui, même sur des images qui ne sont pas des
paysages satellites (captures d'écran, bruit aléatoire) : la confiance reste
entre 99 et 100 %. La confiance seule est donc un indicateur faible pour ce
modèle. Elle détecte une dégradation franche, mais pas une image hors sujet.

## Données personnelles

Les journaux et la base ne contiennent aucune donnée personnelle : seulement le
label prédit, la confiance, la durée et un nom de fichier généré aléatoirement.
Les images satellites ne concernent pas des personnes.

## Amélioration du modèle

La confiance de chaque prédiction est conservée en base. Les prédictions peu
fiables peuvent ainsi être retrouvées, vérifiées puis réutilisées pour
réentraîner le modèle, ce qui alimente la boucle d'amélioration continue.
