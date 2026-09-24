import great_expectations as gx


DATA_SOURCE_NAME = "weather_pandas_source"
DATA_ASSET_NAME = "weather_data"
BATCH_NAME = "weather_batch"
SUITE_NAME = "weather_quality_suite"
VALIDATION_NAME = "weather_validation"


def create_validation():

    context = gx.get_context(mode="file")

    # --------------------------------------------------
    # 1. DATA SOURCE
    # --------------------------------------------------

    try:
        data_source = context.data_sources.get(
            DATA_SOURCE_NAME
        )
        print("Data Source existante.")

    except Exception:
        data_source = context.data_sources.add_pandas(
            name=DATA_SOURCE_NAME
        )
        print("Data Source créée.")

    # --------------------------------------------------
    # 2. DATA ASSET
    # --------------------------------------------------

    try:
        data_asset = data_source.get_asset(
            DATA_ASSET_NAME
        )
        print("Data Asset existante.")

    except Exception:
        data_asset = data_source.add_dataframe_asset(
            name=DATA_ASSET_NAME
        )
        print("Data Asset créée.")

    # --------------------------------------------------
    # 3. BATCH DEFINITION
    # --------------------------------------------------

    try:
        batch_definition = data_asset.get_batch_definition(
            BATCH_NAME
        )
        print("Batch Definition existante.")

    except Exception:
        batch_definition = (
            data_asset.add_batch_definition_whole_dataframe(
                BATCH_NAME
            )
        )
        print("Batch Definition créée.")

    # --------------------------------------------------
    # 4. EXPECTATION SUITE
    # --------------------------------------------------

    suite = context.suites.get(
        SUITE_NAME
    )

    print(
        f"Expectation Suite récupérée : "
        f"{suite.name}"
    )

    # --------------------------------------------------
    # 5. VALIDATION DEFINITION
    # --------------------------------------------------

    try:
        validation_definition = (
            context.validation_definitions.get(
                VALIDATION_NAME
            )
        )

        print("Validation Definition existante.")

    except Exception:

        validation_definition = gx.ValidationDefinition(
            data=batch_definition,
            suite=suite,
            name=VALIDATION_NAME,
        )

        context.validation_definitions.add(
            validation_definition
        )

        print("Validation Definition créée.")

    print()
    print("=" * 60)
    print("VALIDATION DEFINITION")
    print("=" * 60)
    print(f"Nom : {VALIDATION_NAME}")
    print(f"Suite : {SUITE_NAME}")
    print(f"Batch : {BATCH_NAME}")


if __name__ == "__main__":
    create_validation()
