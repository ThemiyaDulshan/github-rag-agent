from collections import Counter

from app.github_loader import load_repository
from app.document_loader import load_documents
from app.chunker import create_chunks


def main():
    url = input("Enter GitHub repository URL: ").strip()

    destination = "data/repositories/chunk-test"

    result = load_repository(
        url,
        destination
    )

    documents = load_documents(
        destination,
        result["files"]
    )

    chunks = create_chunks(documents)

    chunk_types = Counter(
        chunk["type"]
        for chunk in chunks
    )

    print("\nImproved Chunking Results")
    print("=" * 50)

    print(f"Repository: {result['repository']}")
    print(f"Documents: {len(documents)}")
    print(f"Total chunks: {len(chunks)}")

    print("\nChunk Types")
    print("-" * 50)

    for chunk_type, count in chunk_types.most_common():
        print(f"{chunk_type}: {count}")

    print("\nFirst 20 Chunks")
    print("-" * 50)

    for chunk in chunks[:20]:
        parent = chunk.get("parent_class")

        print(
            f"{chunk['path']} | "
            f"{chunk['type']} | "
            f"{chunk['name']} | "
            f"parent={parent} | "
            f"lines {chunk['start_line']}-{chunk['end_line']}"
        )

    python_chunks = [
        chunk
        for chunk in chunks
        if chunk["language"] == "Python"
    ]

    print("\nPython Chunk Example")
    print("-" * 50)

    if python_chunks:
        example = python_chunks[0]

        print(f"File: {example['path']}")
        print(f"Type: {example['type']}")
        print(f"Name: {example['name']}")
        print(f"Parent class: {example['parent_class']}")
        print(
            f"Lines: "
            f"{example['start_line']}-"
            f"{example['end_line']}"
        )
        print(f"Imports: {len(example['imports'])}")


if __name__ == "__main__":
    main()