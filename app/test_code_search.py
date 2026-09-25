from app.github_loader import load_repository
from app.code_search import search_code


def main():
    url = input(
        "Enter GitHub repository URL: "
    ).strip()

    destination = "data/repositories/search-test"

    result = load_repository(
        url,
        destination
    )

    query = input(
        "\nEnter code search query: "
    ).strip()

    results = search_code(
        destination,
        query,
        max_results=20
    )

    print("\nCode Search Results")
    print("=" * 60)

    print(f"Query: {query}")
    print(f"Matches: {len(results)}")

    print("\nMatches")
    print("-" * 60)

    for index, match in enumerate(
        results,
        start=1
    ):
        print(
            f"{index}. "
            f"{match['path']}:"
            f"{match['line']}"
        )

        print(
            f"   {match['content']}"
        )


if __name__ == "__main__":
    main()