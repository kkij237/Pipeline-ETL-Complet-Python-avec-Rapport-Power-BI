import great_expectations as gx

SITE_NAME = "local_site"
BASE_DIRECTORY = "uncommitted/data_docs/local_site/"

def build_docs():
    context = gx.get_context(mode="file")

    site_config = {
        "class_name": "SiteBuilder",
        "site_index_builder": {
            "class_name": "DefaultSiteIndexBuilder"
        },
        "store_backend": {
            "class_name": "TupleFilesystemStoreBackend",
            "base_directory": BASE_DIRECTORY,
        },
    }

    try:
        context.add_data_docs_site(
            site_name=SITE_NAME,
            site_config=site_config,
        )
        print("Data Docs configurés.")
    except Exception as error:
        print("Configuration Data Docs déjà présente.")
        print(f"Détail : {error}")

    print()
    print("Construction des Data Docs...")

    result = context.build_data_docs(
        site_names=[SITE_NAME]
    )

    print()
    print("=" * 60)
    print("DATA DOCS GÉNÉRÉS")
    print("=" * 60)
    print(f"Site : {SITE_NAME}")
    print(f"Emplacement : gx/{BASE_DIRECTORY}")

    if result:
        print()
        print("Résultat :")
        for site, location in result.items():
            print(f"- {site} : {location}")


if __name__ == "__main__":
    build_docs()
