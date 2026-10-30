import os
import json
import time
import logging
from datetime import datetime
import requests
import pandas as pd

# Configuration des logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Création dynamique du dossier raw horodaté (Ex: data/raw/2026-10-28)
TODAY = datetime.now().strftime("%Y-%m-%d")
RAW_DIR = f"data/raw/{TODAY}"
os.makedirs(RAW_DIR, exist_ok=True)

def extract_api_coingecko(pages=2, per_page=25):
    """
    Source 1 : API Publique (CoinGecko)
    """
    base_url = "https://api.coingecko.com/api/v3/coins/markets"
    all_coins = []
    headers = {"Accept": "application/json"}

    for page in range(1, pages + 1):
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": per_page,
            "page": page,
            "sparkline": "false"
        }
        
        success = False
        for attempt in range(1, 4):
            try:
                logging.info(f"[API] Extraction CoinGecko - Page {page}/{pages} (Tentative {attempt})...")
                response = requests.get(base_url, params=params, headers=headers, timeout=15)
                
                if response.status_code == 429:
                    logging.warning("[API] Rate limit atteint. Pause de 10 secondes...")
                    time.sleep(10)
                    continue

                response.raise_for_status()
                data = response.json()
                all_coins.extend(data)
                success = True
                break
            except requests.exceptions.RequestException as e:
                logging.error(f"[API] Erreur : {e}. Nouvelle tentative dans 5s...")
                time.sleep(5)
        
        if not success:
            logging.error(f"[API] Échec définitif pour la page {page}.")

    api_dest_path = os.path.join(RAW_DIR, "raw_coingecko_market.json")
    with open(api_dest_path, "w", encoding="utf-8") as f:
        json.dump(all_coins, f, indent=4)

    logging.info(f"[API] Données sauvegardées : {api_dest_path} ({len(all_coins)} lignes).")
    return api_dest_path

def extract_csv_opendata():
    """
    Source 2 : Fichier CSV Open Data (FRED - Federal Reserve)
    """
    # URL de la FRED pour l'historique du Bitcoin (plus fiable)
    csv_url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=CBBTCUSD"
    csv_dest_path = os.path.join(RAW_DIR, "raw_bitcoin_history.csv")
    
    logging.info("[CSV] Téléchargement du fichier Open Data en cours...")
    try:
        # Utilisation de requests avec un User-Agent pour contourner l'erreur 403
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(csv_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Sauvegarde du contenu brut
        with open(csv_dest_path, "wb") as f:
            f.write(response.content)
            
        df_csv = pd.read_csv(csv_dest_path)
        logging.info(f"[CSV] Fichier Open Data téléchargé et sauvegardé : {csv_dest_path} ({len(df_csv)} lignes).")
        return csv_dest_path
    except Exception as e:
        logging.error(f"[CSV] Échec du téléchargement du fichier CSV : {e}")
        return None

if __name__ == "__main__":
    logging.info("DÉMARRAGE DE L'ÉTAPE E : EXTRACTION")
    
    api_file = extract_api_coingecko(pages=2, per_page=25)
    csv_file = extract_csv_opendata()
    
    if api_file and csv_file:
        logging.info("Étape E (EXTRACT) terminée avec succès. Toutes les sources sont sécurisées.")
    else:
        logging.warning("L'étape E s'est terminée avec des erreurs partielles.")
