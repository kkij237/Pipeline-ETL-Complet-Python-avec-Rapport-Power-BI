import os
import json
import logging
from datetime import datetime
import pandas as pd
import numpy as np

# Configuration des logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Chemins des dossiers
TODAY = datetime.now().strftime("%Y-%m-%d")
RAW_DIR = f"data/raw/{TODAY}"
PROCESSED_DIR = "data/processed"
os.makedirs(PROCESSED_DIR, exist_ok=True)

def load_raw_data():
    """
    Chargement des données brutes depuis le dossier raw horodaté.
    """
    json_path = os.path.join(RAW_DIR, "raw_coingecko_market.json")
    csv_path = os.path.join(RAW_DIR, "raw_bitcoin_history.csv")

    if not os.path.exists(json_path) or not os.path.exists(csv_path):
        raise FileNotFoundError("Fichiers bruts introuvables. Exécutez d'abord src/extract.py.")

    with open(json_path, "r", encoding="utf-8") as f:
        data_json = json.load(f)
    df_api = pd.DataFrame(data_json)
    
    df_csv = pd.read_csv(csv_path)
    logging.info(f"Chargement réussi : {len(df_api)} cryptos (API) et {len(df_csv)} lignes historiques (CSV).")
    return df_api, df_csv

def transform_and_build_star_schema(df_api, df_csv):
    """
    Nettoyage, enrichissement et construction du Star Schema.
    """
    logging.info("Nettoyage et transformation des données...")

    # 1. Nettoyage de la source API (Marché actuel)
    df_api = df_api.drop_duplicates(subset=['id']).copy()
    cols_api_needed = ['id', 'symbol', 'name', 'current_price', 'market_cap', 'total_volume', 
                       'high_24h', 'low_24h', 'price_change_percentage_24h']
    df_api = df_api[cols_api_needed]
    df_api['symbol'] = df_api['symbol'].str.upper()
    df_api.fillna({'market_cap': 0, 'total_volume': 0, 'price_change_percentage_24h': 0.0}, inplace=True)

    # 2. Nettoyage de la source CSV (Historique Bitcoin FRED)
    # Renommage robuste par position (Col 0 = date, Col 1 = prix_btc_usd)
    df_csv.columns = ['date', 'prix_btc_usd']
    df_csv.drop_duplicates(subset=['date'], inplace=True)
    
    # Remplacement des valeurs non numériques (ex: '.') par NaN puis conversion en float
    df_csv['prix_btc_usd'] = pd.to_numeric(df_csv['prix_btc_usd'], errors='coerce')
    df_csv['prix_btc_usd'] = df_csv['prix_btc_usd'].ffill().bfill() # Comblement des trous
    
    df_csv['date'] = pd.to_datetime(df_csv['date'])

    # 3. Construction de la DIMENSION TEMPORELLE (dim_temps)
    df_temps = pd.DataFrame({'date': df_csv['date'].unique()})
    df_temps['date_key'] = df_temps['date'].dt.strftime('%Y%m%d').astype(int)
    df_temps['annee'] = df_temps['date'].dt.year
    df_temps['trimestre'] = df_temps['date'].dt.quarter
    df_temps['mois'] = df_temps['date'].dt.month
    df_temps['nom_mois'] = df_temps['date'].dt.strftime('%B')
    df_temps['semaine'] = df_temps['date'].dt.isocalendar().week
    df_temps['jour_semaine'] = df_temps['date'].dt.day_name()
    
    # Relecture format texte pour les exports
    df_temps['date'] = df_temps['date'].dt.strftime('%Y-%m-%d')

    # 4. Enrichissement : Calculs sur l'historique
    df_csv['date_key'] = df_csv['date'].dt.strftime('%Y%m%d').astype(int)
    df_csv['variation_quotidienne_pct'] = df_csv['prix_btc_usd'].pct_change() * 100
    df_csv['moyenne_mobile_7j'] = df_csv['prix_btc_usd'].rolling(window=7, min_periods=1).mean()
    df_csv['date'] = df_csv['date'].dt.strftime('%Y-%m-%d')

    # 5. Jointure entre les sources (Table de Faits)
    df_csv['crypto_id'] = 'bitcoin'
    
    # Construction de la TABLE DE FAITS (fact_marche_crypto)
    fact_marche = df_csv[['date_key', 'crypto_id', 'prix_btc_usd', 'variation_quotidienne_pct', 'moyenne_mobile_7j']].copy()
    fact_marche.fillna({'variation_quotidienne_pct': 0.0}, inplace=True)

    # DIMENSION CRYPTO (dim_crypto)
    dim_crypto = df_api.rename(columns={'id': 'crypto_id'}).copy()

    # 6. Sauvegarde dans /data/processed/
    dim_crypto.to_csv(f"{PROCESSED_DIR}/dim_crypto.csv", index=False)
    df_temps.to_csv(f"{PROCESSED_DIR}/dim_temps.csv", index=False)
    fact_marche.to_csv(f"{PROCESSED_DIR}/fact_marche_crypto.csv", index=False)

    logging.info(f"Sauvegarde réussie dans {PROCESSED_DIR} :")
    logging.info(f"   - dim_crypto.csv ({len(dim_crypto)} entités)")
    logging.info(f"   - dim_temps.csv ({len(df_temps)} dates)")
    logging.info(f"   - fact_marche_crypto.csv ({len(fact_marche)} faits enregistrés)")

if __name__ == "__main__":
    logging.info("DÉMARRAGE DE L'ÉTAPE T : TRANSFORMATION")
    df_api_raw, df_csv_raw = load_raw_data()
    transform_and_build_star_schema(df_api_raw, df_csv_raw)
    logging.info("Étape T (TRANSFORM) terminée avec succès !")
