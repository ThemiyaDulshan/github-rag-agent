from app.github_loader import load_repository
from app.definition_lookup import find_definitions


def main():
    url = input(
        "Enter GitHub repository URL: "
    ).strip()

    destination = "data/repositories/definition-test"

    load_repository(
        url,
        destination
    )

    name = input(
        "\nEnter function or class name: "
    ).strip()

    definition_type = input(
        "Enter type (function/class/all): "
    ).strip().lower()

    if definition_type == "all":
        definition_type = None

    results = find_definitions(
        destination,
        name,
        definition_type
    )

    print("\nDefinition Lookup Results")
    print("=" * 60)

    print(f"Name: {name}")
    print(
        f"Type: "
        f"{definition_type or 'all'}"
    )
    print(f"Matches: {len(results)}")

    print("\nDefinitions")
    print("-" * 60)

    for index, result in enumerate(
        results,
        start=1
    ):
        print(
            f"{index}. "
            f"{result['path']}"
        )

        print(
            f"   Type: {result['type']}"
        )

        print(
            f"   Name: {result['name']}"
        )

        print(
            f"   Lines: "
            f"{result['start_line']}-"
            f"{result['end_line']}"
        )


if __name__ == "__main__":
    main()