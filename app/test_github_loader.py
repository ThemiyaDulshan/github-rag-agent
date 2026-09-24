from app.github_loader import load_repository


def main():
    url = input("Enter GitHub repository URL: ").strip()

    destination = "data/repositories/test-repository-4"

    result = load_repository(
        url,
        destination
    )

    print("\nRepository Information")
    print("=" * 50)

    print(f"Owner: {result['owner']}")
    print(f"Repository: {result['repository']}")
    print(f"URL: {result['url']}")
    print(f"Total files: {result['total_files']}")
    print(f"Relevant files: {result['relevant_files']}")
    print(f"Binary files: {result['binary_files']}")
    print(f"Large files: {result['skipped_large_files']}")
    print(f"Total size: {result['total_size_bytes']:,} bytes")

    print("\nFile Categories")
    print("-" * 50)

    for category, count in result["categories"].items():
        print(f"{category}: {count}")

    print("\nFile Types")
    print("-" * 50)

    for extension, count in result["extensions"].items():
        print(f"{extension or '[no extension]'}: {count}")


if __name__ == "__main__":
    main()