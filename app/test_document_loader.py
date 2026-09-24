from collections import Counter

from app.github_loader import load_repository
from app.document_loader import load_documents


def main():
    url = input("Enter GitHub repository URL: ").strip()

    destination = "data/repositories/language-test"

    result = load_repository(
        url,
        destination
    )

    documents = load_documents(
        destination,
        result["files"]
    )

    languages = Counter(
        document["language"]
        for document in documents
    )

    print("\nDocument Loading Results")
    print("=" * 50)

    print(f"Repository: {result['repository']}")
    print(f"Files discovered: {result['total_files']}")
    print(f"Documents loaded: {len(documents)}")

    total_lines = sum(
        document["line_count"]
        for document in documents
    )

    print(f"Total lines: {total_lines:,}")

    print("\nLanguages")
    print("-" * 50)

    for language, count in languages.most_common():
        print(f"{language}: {count}")

    print("\nFirst 15 Documents")
    print("-" * 50)

    for document in documents[:15]:
        print(
            f"{document['path']} | "
            f"{document['language']} | "
            f"{document['line_count']} lines"
        )


if __name__ == "__main__":
    main()