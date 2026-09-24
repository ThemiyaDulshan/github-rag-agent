from app.embeddings import EmbeddingModel
from app.vector_store import VectorStore


def main():
    query = input("\nEnter your repository question: ").strip()

    embedding_model = EmbeddingModel()
    vector_store = VectorStore()

    query_embedding = embedding_model.encode_one(query)

    results = vector_store.search(
        query_embedding,
        n_results=5
    )

    print("\nSemantic Search Results")
    print("=" * 60)

    for index, result in enumerate(results, start=1):
        metadata = result["metadata"]

        print(f"\nResult {index}")
        print("-" * 60)

        print(
            f"File: {metadata['path']}"
        )

        print(
            f"Type: {metadata['type']}"
        )

        print(
            f"Name: {metadata['name']}"
        )

        print(
            f"Parent class: "
            f"{metadata['parent_class']}"
        )

        print(
            f"Lines: "
            f"{metadata['start_line']}-"
            f"{metadata['end_line']}"
        )

        print(
            f"Distance: "
            f"{result['distance']:.4f}"
        )

        print("\nContent:")
        print(result["content"][:1500])


if __name__ == "__main__":
    main()