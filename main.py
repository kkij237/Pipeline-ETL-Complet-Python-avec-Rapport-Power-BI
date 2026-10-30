import logging
from datetime import datetime
from src.extract import extract_api_coingecko, extract_csv_opendata
from src.transform import load_raw_data, transform_and_build_star_schema
from src.load import load_data_to_postgres

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def run_pipeline():
    start_time = datetime.now()
    logging.info("DÉMARRAGE DU PIPELINE ETL COMPLET (MINI-PROJET S3)")
   
    # 1. ÉTAPE E (EXTRACT)
    logging.info("\n 1. ÉTAPE E : EXTRACTION ")
    extract_api_coingecko(pages=2, per_page=25)
    extract_csv_opendata()

    # 2. ÉTAPE T (TRANSFORM)
    logging.info("\n 2. ÉTAPE T : TRANSFORMATION ")
    df_api_raw, df_csv_raw = load_raw_data()
    transform_and_build_star_schema(df_api_raw, df_csv_raw)

    # 3. ÉTAPE L (LOAD)
    logging.info("\n 3. ÉTAPE L : CHARGEMENT ")
    load_data_to_postgres()

    duration = datetime.now() - start_time
    logging.info(f"PIPELINE ETL EXÉCUTÉ AVEC SUCCÈS EN {duration.total_seconds():.2f}s !")

if __name__ == "__main__":
    run_pipeline()
