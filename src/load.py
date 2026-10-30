import os
import uuid
import logging
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine, text

# Configuration des logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Connexion PostgreSQL
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "postgres")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "crypto_db")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

PROCESSED_DIR = "data/processed"

def init_db_schema(engine):
    """
    Création des tables SQL avec contraintes (PK, FK, NOT NULL) et de la table de suivi ETL.
    """
    with engine.begin() as conn:
        # Table de logs d'exécution
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS etl_pipeline_logs (
                run_id VARCHAR(50) PRIMARY KEY,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP,
                status VARCHAR(20) NOT NULL,
                rows_inserted INT DEFAULT 0
            );
        """))

        # Dimension Crypto
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS dim_crypto (
                crypto_id VARCHAR(50) PRIMARY KEY,
                symbol VARCHAR(20) NOT NULL,
                name VARCHAR(100) NOT NULL,
                current_price NUMERIC(18, 6),
                market_cap NUMERIC(20, 2),
                total_volume NUMERIC(20, 2),
                high_24h NUMERIC(18, 6),
                low_24h NUMERIC(18, 6),
                price_change_percentage_24h NUMERIC(10, 4)
            );
        """))

        # Dimension Temps
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS dim_temps (
                date_key INT PRIMARY KEY,
                date DATE NOT NULL,
                annee INT NOT NULL,
                trimestre INT NOT NULL,
                mois INT NOT NULL,
                nom_mois VARCHAR(20) NOT NULL,
                semaine INT NOT NULL,
                jour_semaine VARCHAR(20) NOT NULL
            );
        """))

        # Table de Faits
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS fact_marche_crypto (
                id SERIAL PRIMARY KEY,
                date_key INT NOT NULL REFERENCES dim_temps(date_key),
                crypto_id VARCHAR(50) NOT NULL REFERENCES dim_crypto(crypto_id),
                prix_btc_usd NUMERIC(18, 6),
                variation_quotidienne_pct NUMERIC(10, 4),
                moyenne_mobile_7j NUMERIC(18, 6)
            );
        """))
    logging.info("Schéma SQL vérifié et initialisé avec succès.")

def load_data_to_postgres():
    run_id = str(uuid.uuid4())[:8]
    start_time = datetime.now()
    engine = create_engine(DATABASE_URL)
    
    # Initialisation du schéma EN PREMIER
    init_db_schema(engine)

    # Enregistrement du début de l'exécution
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO etl_pipeline_logs (run_id, start_time, status) VALUES (:id, :start, :status)"),
            {"id": run_id, "start": start_time, "status": "RUNNING"}
        )

    try:
        # Nettoyage des tables pour éviter la violation de clé primaire lors des réexécutions
        with engine.begin() as conn:
            conn.execute(text("TRUNCATE TABLE fact_marche_crypto, dim_crypto, dim_temps CASCADE;"))

        # Lecture des fichiers traités
        df_crypto = pd.read_csv(f"{PROCESSED_DIR}/dim_crypto.csv")
        df_temps = pd.read_csv(f"{PROCESSED_DIR}/dim_temps.csv")
        df_fact = pd.read_csv(f"{PROCESSED_DIR}/fact_marche_crypto.csv")

        # Chargement dans PostgreSQL
        logging.info("Chargement de dim_crypto...")
        df_crypto.to_sql('dim_crypto', engine, if_exists='append', index=False, method='multi')

        logging.info("Chargement de dim_temps...")
        df_temps.to_sql('dim_temps', engine, if_exists='append', index=False, method='multi')

        logging.info("Chargement de fact_marche_crypto...")
        df_fact.to_sql('fact_marche_crypto', engine, if_exists='append', index=False, method='multi')

        total_rows = len(df_crypto) + len(df_temps) + len(df_fact)
        end_time = datetime.now()

        # Mise à jour du log de succès
        with engine.begin() as conn:
            conn.execute(
                text("""
                    UPDATE etl_pipeline_logs 
                    SET end_time = :end, status = 'SUCCESS', rows_inserted = :rows
                    WHERE run_id = :id
                """),
                {"end": end_time, "rows": total_rows, "id": run_id}
            )

        logging.info(f"Chargement terminé avec succès ! ({total_rows} lignes insérées, Run ID: {run_id}).")

    except Exception as e:
        end_time = datetime.now()
        logging.error(f"Échec lors du chargement dans PostgreSQL : {e}")
        with engine.begin() as conn:
            conn.execute(
                text("""
                    UPDATE etl_pipeline_logs 
                    SET end_time = :end, status = 'FAILED'
                    WHERE run_id = :id
                """),
                {"end": end_time, "id": run_id}
            )
        raise e

if __name__ == "__main__":
    logging.info("DÉMARRAGE DE L'ÉTAPE L : CHARGEMENT (LOAD)")
    load_data_to_postgres()
