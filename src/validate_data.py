import pandas as pd
import great_expectations as gx

DATA_FILE = "data/processed/weather_processed.csv"


def validate_weather_data():

    # Charger les données
    df = pd.read_csv(DATA_FILE)

    print("Dataset chargé :", df.shape)
    print()

    # Créer le contexte GX
    context = gx.get_context()

    # Créer la source pandas
    data_source = context.data_sources.add_pandas(
        name="weather_pandas_source"
    )

    # Créer l'asset
    data_asset = data_source.add_dataframe_asset(
        name="weather_data"
    )

    # Créer le Batch Definition
    batch_definition = data_asset.add_batch_definition_whole_dataframe(
        "weather_batch"
    )

    # Récupérer le Batch
    batch = batch_definition.get_batch(
        batch_parameters={"dataframe": df}
    )

    print("Batch GX créé avec succès.")
    print()

    # Liste des Expectations
    expectations = [

        # 1. Colonnes obligatoires
        gx.expectations.ExpectTableColumnsToMatchSet(
            column_set=[
                "date",
                "temperature_mean",
                "temperature_max",
                "temperature_min",
                "city",
                "country",
                "latitude",
                "longitude",
                "temperature_range",
                "year",
                "month",
                "day",
            ],
            exact_match=True,
        ),

        # 2. Pas de valeurs nulles
        gx.expectations.ExpectColumnValuesToNotBeNull(
            column="date"
        ),

        gx.expectations.ExpectColumnValuesToNotBeNull(
            column="city"
        ),

        gx.expectations.ExpectColumnValuesToNotBeNull(
            column="latitude"
        ),

        gx.expectations.ExpectColumnValuesToNotBeNull(
            column="longitude"
        ),

        # 3. Latitude valide
        gx.expectations.ExpectColumnValuesToBeBetween(
            column="latitude",
            min_value=-90,
            max_value=90,
        ),

        # 4. Longitude valide
        gx.expectations.ExpectColumnValuesToBeBetween(
            column="longitude",
            min_value=-180,
            max_value=180,
        ),

        # 5. Température moyenne raisonnable
        gx.expectations.ExpectColumnValuesToBeBetween(
            column="temperature_mean",
            min_value=-50,
            max_value=60,
        ),

        # 6. Température maximale raisonnable
        gx.expectations.ExpectColumnValuesToBeBetween(
            column="temperature_max",
            min_value=-50,
            max_value=60,
        ),

        # 7. Température minimale raisonnable
        gx.expectations.ExpectColumnValuesToBeBetween(
            column="temperature_min",
            min_value=-50,
            max_value=60,
        ),

        # 8. Villes autorisées
        gx.expectations.ExpectColumnValuesToBeInSet(
            column="city",
            value_set=[
                "Yaounde",
                "Douala",
                "Lagos",
                "Nairobi",
                "Dakar",
            ],
        ),
    ]

    # Exécuter les tests
    results = []

    for i, expectation in enumerate(expectations, start=1):

        result = batch.validate(expectation)

        success = result["success"]

        results.append(success)

        status = "PASS" if success else "FAIL"

        print(
            f"Test {i:02d} - "
            f"{expectation.expectation_type}: "
            f"{status}"
        )

    print()
    print("=" * 60)

    if all(results):
        print("QUALITÉ DES DONNÉES : PASS")
        print("Toutes les Expectations sont respectées.")
        return True
    else:
        print("QUALITÉ DES DONNÉES : FAIL")
        print("Au moins une Expectation n'est pas respectée.")
        return False


if __name__ == "__main__":
    validate_weather_data()
