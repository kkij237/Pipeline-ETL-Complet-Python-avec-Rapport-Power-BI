import sys
import pandas as pd
import great_expectations as gx
from great_expectations.checkpoint import UpdateDataDocsAction

DATA_FILE = "data/processed/weather_processed.csv"
VALIDATION_NAME = "weather_validation"
CHECKPOINT_NAME = "weather_quality_checkpoint"
SITE_NAME = "local_site"


def run_checkpoint():
    context = gx.get_context(mode="file")

    df = pd.read_csv(DATA_FILE)

    print("=" * 60)
    print("GREAT EXPECTATIONS — CHECKPOINT")
    print("=" * 60)
    print(f"Fichier  : {DATA_FILE}")
    print(f"Lignes   : {len(df)}")
    print(f"Colonnes : {len(df.columns)}")
    print()

    # Récupération de la Validation Definition existante
    validation_definition = context.validation_definitions.get(
        VALIDATION_NAME
    )

    # Action permettant de mettre à jour les Data Docs
    actions = [
        UpdateDataDocsAction(
            name="update_data_docs",
            site_names=[SITE_NAME],
        )
    ]

    # Création ou mise à jour du Checkpoint
    checkpoint = gx.Checkpoint(
        name=CHECKPOINT_NAME,
        validation_definitions=[validation_definition],
        actions=actions,
    )

    context.checkpoints.add_or_update(checkpoint)

    print("Checkpoint créé ou mis à jour.")
    print("Action Data Docs ajoutée au Checkpoint.")

    print()
    print("Exécution du Checkpoint...")
    print()

    # Exécution du Checkpoint
    result = checkpoint.run(
        batch_parameters={"dataframe": df}
    )

    print()
    print("=" * 60)

    if result.success:
        print("QUALITÉ DES DONNÉES : PASS")
        print("=" * 60)
        print("Toutes les Expectations sont respectées.")
        print("Data Docs mis à jour automatiquement.")
        return True

    print("QUALITÉ DES DONNÉES : FAIL")
    print("=" * 60)
    print("Au moins une Expectation n'est pas respectée.")
    print("Les résultats ont été envoyés aux Data Docs.")
    return False


if __name__ == "__main__":
    success = run_checkpoint()

    if not success:
        sys.exit(1)

