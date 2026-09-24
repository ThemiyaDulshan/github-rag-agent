from app.github_loader import load_repository
from app.document_loader import load_documents
from app.chunker import create_chunks
from app.embeddings import EmbeddingModel


def main():
    url = input("Enter GitHub repository URL: ").strip()

    destination = "data/repositories/embedding-test"

    result = load_repository(
        url,
        destination
    )

    documents = load_documents(
        destination,
        result["files"]
    )

    chunks = create_chunks(documents)

    print("\nEmbedding Model")
    print("=" * 50)

    model = EmbeddingModel()

    print(f"Model dimension: {model.dimension()}")
    print(f"Chunks: {len(chunks)}")

    sample_texts = [
        chunk["content"]
        for chunk in chunks[:5]
    ]

    embeddings = model.encode(sample_texts)

    print("\nEmbedding Results")
    print("-" * 50)

    print(f"Embeddings generated: {len(embeddings)}")

    for index, embedding in enumerate(embeddings):
        print(
            f"Chunk {index + 1}: "
            f"{len(embedding)} dimensions"
        )

    print("\nFirst Embedding")
    print("-" * 50)

    print(embeddings[0][:10])


if __name__ == "__main__":
    main()