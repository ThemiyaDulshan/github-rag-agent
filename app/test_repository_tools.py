from app.github_loader import load_repository
from app.repository_tools import (
    get_repository_structure,
    get_file,
)


def main():
    url = input("Enter GitHub repository URL: ").strip()

    destination = "data/repositories/tools-test"

    result = load_repository(
        url,
        destination
    )

    print("\nRepository Structure")
    print("=" * 60)

    structure = get_repository_structure(
        destination,
        max_depth=3
    )

    print(structure)

    print("\nFile Lookup")
    print("=" * 60)

    file_path = input(
        "\nEnter a repository file path: "
    ).strip()

    file_result = get_file(
        destination,
        file_path
    )

    print(f"\nFile: {file_result['path']}")
    print(f"Lines: {file_result['line_count']}")

    print("\nContent")
    print("-" * 60)

    print(
        file_result["content"][:5000]
    )


if __name__ == "__main__":
    main()