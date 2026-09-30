import sys
import pandas as pd
import great_expectations as gx


DATA_FILE = "data/processed/weather_processed.csv"

VALIDATION_NAME = "weather_validation"
CHECKPOINT_NAME = "weather_quality_checkpoint"


def run_checkpoint():

    context = gx.get_context(mode="file")

    # --------------------------------------------------
    # 1. CHARGER LES DONNÉES
    # --------------------------------------------------

    df = pd.read_csv(DATA_FILE)

    print("=" * 60)
    print("GREAT EXPECTATIONS — CHECKPOINT")
    print("=" * 60)
    print(f"Fichier : {DATA_FILE}")
    print(f"Lignes  : {len(df)}")
    print(f"Colonnes : {len(df.columns)}")
    print()

    # --------------------------------------------------
    # 2. RÉCUPÉRER LA VALIDATION DEFINITION
    # --------------------------------------------------

    validation_definition = (
        context.validation_definitions.get(
            VALIDATION_NAME
        )
    )

    # --------------------------------------------------
    # 3. CRÉER / RÉCUPÉRER LE CHECKPOINT
    # --------------------------------------------------

    try:

        checkpoint = context.checkpoints.get(
            CHECKPOINT_NAME
        )

        print("Checkpoint existant récupéré.")

    except Exception:

        checkpoint = gx.Checkpoint(
            name=CHECKPOINT_NAME,
            validation_definitions=[
                validation_definition
            ],
        )

        context.checkpoints.add(
            checkpoint
        )

        print("Checkpoint créé.")

    print()
    print("Exécution du Checkpoint...")
    print()

    # --------------------------------------------------
    # 4. EXÉCUTER LA VALIDATION
    # --------------------------------------------------

    result = checkpoint.run(
        batch_parameters={
            "dataframe": df
        }
    )

    # --------------------------------------------------
    # 5. AFFICHER LE RÉSULTAT
    # --------------------------------------------------

    print()
    print("=" * 60)

    if result.success:

        print("QUALITÉ DES DONNÉES : PASS")
        print("=" * 60)
        print("Toutes les Expectations sont respectées.")

        return True

    else:

        print("QUALITÉ DES DONNÉES : FAIL")
        print("=" * 60)
        print(
            "Au moins une Expectation "
            "n'est pas respectée."
        )

        return False


if __name__ == "__main__":

    success = run_checkpoint()

    # Très important pour le CI/CD
    if not success:
        sys.exit(1)
