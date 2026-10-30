# Mini-Projet S3 : Pipeline ETL Complet Python & Rapport Power BI (Marché Crypto)

Description du Projet
Ce projet a été réalisé dans le cadre du sprint S3 du stage Formuloo. L'objectif est de concevoir et déployer un pipeline de données complet (ETL) de bout en bout : extraction de données financières depuis une API publique, transformation via Python, chargement dans une base de données relationnelle, et création d'un tableau de bord interactif pour la prise de décision.

Lien vers le rapport Power BI publié : https://app.fabric.microsoft.com/links/bawBDKzU_o?ctid=0007c922-8e7e-431d-a477-5e4ba82077e9&pbi_source=linkShare

## Architecture & Technologies
Extraction (API) : CoinGecko API
Transformation & Traitement : Python, Pandas, Requests
Chargement (Base de données) : PostgreSQL, SQLAlchemy, Microsoft Fabric
Visualisation (BI) : Power BI Desktop & Power BI Service
Orchestration & Versioning : Script Python personnalisé, Git / GitLab

## Modélisation des Données (Star Schema)
Les données ont été modélisées selon un schéma en étoile pour optimiser les requêtes analytiques sur Power BI :
dim_crypto (Dimension) : Informations de base sur les cryptomonnaies étudiées (ID, nom, symbole).
dim_temps (Dimension) : Calendrier détaillé (date, année, trimestre, mois, jour) pour l'analyse temporelle.
fact_marche_crypto (Table de faits) : Indicateurs de marché quotidiens (prix en USD, volume, variation quotidienne, prix le plus haut/bas).

Note analytique : Pour ce projet, le jeu de données s'est concentré exclusivement sur le Bitcoin (BTC) sur une période de 10 ans. Cette approche permet de privilégier une analyse temporelle approfondie (comparaison des performances annuelles et mensuelles) au lieu d'une comparaison inter-actifs. L'architecture ETL reste cependant complètement reproductible et scalable pour intégrer n'importe quelle autre cryptomonnaie.

Note technique : la base PostgreSQL est hébergée dans le cloud (Neon), ce qui permet à Power BI Service de s'y connecter directement sans passerelle (gateway) dédiée, celle-ci n'étant disponible que sous Windows.

## Tableau de Bord Power BI
Le rapport se compose de 3 pages interactives :
 Vue d'ensemble : 4 KPIs majeurs (Prix actuel, Prix moyen, Volatilité, Record historique) et une courbe d'évolution globale sur 10 ans.
 Analyse temporelle : Graphique à barres montrant le prix moyen par année et tableau récapitulatif mensuel, incluant des filtres croisés.
 Détail Période (Drill-through) : Page d'exploration accessible depuis la page 2, offrant un zoom détaillé (KPIs et tendance) sur l'année sélectionnée.

## Comment exécuter le projet localement
1. Cloner le dépôt :
   ```bash
   git clone git@gitlab.formuloo.com:formuloo-data/mini-projets/s3-pipeline-etl.git
   cd s3-pipeline-etl
   ```
2. Créer et activer l'environnement virtuel :
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```
4. Configurer la connexion à la base de données : créer un fichier `.env` à la racine du projet avec les identifiants de connexion PostgreSQL (hôte, port, nom de la base, utilisateur, mot de passe), ou renseigner directement ces variables en tête de `main.py` selon la configuration du script.
5. Lancer le pipeline ETL :
   ```bash
   python main.py
   ```

## Livrables inclus
*   Code source complet du pipeline ETL (Python).
*   Fichier d'orchestration et logs d'exécution.
*   Le rapport PDF de fin de stage.
*   Captures d'écran des 3 pages du dashboard Power BI.
