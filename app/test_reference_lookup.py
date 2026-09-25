from app.github_loader import load_repository
from app.reference_lookup import find_references


def main():
    url = input(
        "Enter GitHub repository URL: "
    ).strip()

    destination = "data/repositories/reference-test"

    load_repository(
        url,
        destination
    )

    name = input(
        "\nEnter symbol to find references for: "
    ).strip()

    results = find_references(
        destination,
        name,
        max_results=20
    )

    print("\nReference Lookup Results")
    print("=" * 60)

    print(f"Symbol: {name}")
    print(f"Matches: {len(results)}")

    print("\nReferences")
    print("-" * 60)

    for index, result in enumerate(
        results,
        start=1
    ):
        print(
            f"{index}. "
            f"{result['path']}:"
            f"{result['line']}"
        )

        print(
            f"   {result['content']}"
        )


if __name__ == "__main__":
    main()