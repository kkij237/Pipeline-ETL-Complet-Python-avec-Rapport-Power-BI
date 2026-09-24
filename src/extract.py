import requests
import pandas as pd
from pathlib import Path


CITIES_FILE = Path("data/cities.csv")
OUTPUT_FILE = Path("data/raw/weather_raw.csv")

API_URL = "https://api.open-meteo.com/v1/forecast"


def extract_weather():
    # Lecture du fichier CSV
    cities = pd.read_csv(CITIES_FILE)

    all_weather = []

    # Extraction pour chaque ville
    for _, city in cities.iterrows():

        params = {
            "latitude": city["latitude"],
            "longitude": city["longitude"],
            "daily": (
                "temperature_2m_mean,"
                "temperature_2m_max,"
                "temperature_2m_min"
            ),
            "timezone": "auto",
            "forecast_days": 7,
        }

        print(f"Récupération des données pour {city['city']}...")

        try:
            response = requests.get(
                API_URL,
                params=params,
                timeout=30
            )

            # Déclenche une erreur si l'API retourne 4xx/5xx
            response.raise_for_status()

            data = response.json()

            daily = data["daily"]

            # Transformation de la réponse JSON en DataFrame
            weather_df = pd.DataFrame({
                "date": daily["time"],
                "temperature_mean": daily["temperature_2m_mean"],
                "temperature_max": daily["temperature_2m_max"],
                "temperature_min": daily["temperature_2m_min"],
            })

            # Ajout des informations de notre CSV
            weather_df["city"] = city["city"]
            weather_df["country"] = city["country"]
            weather_df["latitude"] = city["latitude"]
            weather_df["longitude"] = city["longitude"]

            all_weather.append(weather_df)

        except requests.RequestException as error:
            print(
                f"Erreur pour {city['city']} : {error}"
            )

    # Vérification
    if not all_weather:
        raise RuntimeError(
            "Aucune donnée météo n'a été récupérée."
        )

    # Fusion des données des 5 villes
    result = pd.concat(
        all_weather,
        ignore_index=True
    )

    # Création du dossier si nécessaire
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Sauvegarde
    result.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print()
    print("Extraction terminée avec succès.")
    print(f"Fichier : {OUTPUT_FILE}")
    print(f"Nombre de lignes : {len(result)}")


if __name__ == "__main__":
    extract_weather()
