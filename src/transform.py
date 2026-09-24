import pandas as pd
from pathlib import Path


INPUT_FILE = Path("data/raw/weather_raw.csv")
OUTPUT_FILE = Path("data/processed/weather_processed.csv")


def transform_weather():
    # Lecture des données brutes
    df = pd.read_csv(INPUT_FILE)

    print("Données brutes :", df.shape)

    # Conversion de la date
    df["date"] = pd.to_datetime(df["date"])

    # Conversion des colonnes numériques
    numeric_columns = [
        "temperature_mean",
        "temperature_max",
        "temperature_min",
        "latitude",
        "longitude",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # Suppression des doublons
    df = df.drop_duplicates()

    # Création de nouvelles variables
    df["temperature_range"] = (
        df["temperature_max"] - df["temperature_min"]
    )

    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["day"] = df["date"].dt.day

    # Tri
    df = df.sort_values(
        by=["city", "date"]
    ).reset_index(drop=True)

    # Création du dossier de sortie
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Sauvegarde
    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("Transformation terminée.")
    print(f"Données finales : {df.shape}")
    print(f"Fichier : {OUTPUT_FILE}")

    print("\nTypes des colonnes :")
    print(df.dtypes)

    print("\nAperçu :")
    print(df.head())


if __name__ == "__main__":
    transform_weather()
