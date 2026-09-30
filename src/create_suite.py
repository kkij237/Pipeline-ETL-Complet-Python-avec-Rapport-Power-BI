import great_expectations as gx
import great_expectations.expectations as gxe


SUITE_NAME = "weather_quality_suite"


def create_suite():

    context = gx.get_context(mode="file")

    # Vérifier si la suite existe déjà
    try:
        suite = context.suites.get(SUITE_NAME)
        print(f"La suite '{SUITE_NAME}' existe déjà.")
        print(f"Nombre d'Expectations : {len(suite.expectations)}")
        return
    except Exception:
        pass

    # Création de la suite
    suite = gx.ExpectationSuite(
        name=SUITE_NAME
    )

    # --------------------------------------------------
    # 1. STRUCTURE DU DATASET
    # --------------------------------------------------

    suite.add_expectation(
        gxe.ExpectTableColumnsToMatchSet(
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
        )
    )

    # --------------------------------------------------
    # 2. COMPLETUDE
    # --------------------------------------------------

    required_columns = [
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
    ]

    for column in required_columns:

        suite.add_expectation(
            gxe.ExpectColumnValuesToNotBeNull(
                column=column
            )
        )

    # --------------------------------------------------
    # 3. COORDONNEES
    # --------------------------------------------------

    suite.add_expectation(
        gxe.ExpectColumnValuesToBeBetween(
            column="latitude",
            min_value=-90,
            max_value=90,
        )
    )

    suite.add_expectation(
        gxe.ExpectColumnValuesToBeBetween(
            column="longitude",
            min_value=-180,
            max_value=180,
        )
    )

    # --------------------------------------------------
    # 4. TEMPERATURES
    # --------------------------------------------------

    for column in [
        "temperature_mean",
        "temperature_max",
        "temperature_min",
    ]:

        suite.add_expectation(
            gxe.ExpectColumnValuesToBeBetween(
                column=column,
                min_value=-50,
                max_value=60,
            )
        )

    # --------------------------------------------------
    # 5. VILLES AUTORISEES
    # --------------------------------------------------

    suite.add_expectation(
        gxe.ExpectColumnValuesToBeInSet(
            column="city",
            value_set=[
                "Yaounde",
                "Douala",
                "Lagos",
                "Nairobi",
                "Dakar",
            ],
        )
    )

    # --------------------------------------------------
    # 6. UNICITE CITY + DATE
    # --------------------------------------------------

    suite.add_expectation(
        gxe.ExpectCompoundColumnsToBeUnique(
            column_list=[
                "city",
                "date",
            ]
        )
    )

    # --------------------------------------------------
    # 7. NOMBRE DE LIGNES
    # --------------------------------------------------

    suite.add_expectation(
        gxe.ExpectTableRowCountToBeBetween(
            min_value=1,
            max_value=100000,
        )
    )

    # Sauvegarde
    context.suites.add(suite)

    print()
    print("=" * 60)
    print("EXPECTATION SUITE CRÉÉE")
    print("=" * 60)
    print(f"Nom : {SUITE_NAME}")
    print(f"Nombre d'Expectations : {len(suite.expectations)}")


if __name__ == "__main__":
    create_suite()
