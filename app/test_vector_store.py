from app.github_loader import load_repository
from app.document_loader import load_documents
from app.chunker import create_chunks
from app.embeddings import EmbeddingModel
from app.vector_store import VectorStore


def main():
    url = input("Enter GitHub repository URL: ").strip()

    destination = "data/repositories/vector-test"

    result = load_repository(
        url,
        destination
    )

    documents = load_documents(
        destination,
        result["files"]
    )

    chunks = create_chunks(documents)

    print("\nPreparing Embeddings")
    print("=" * 50)

    embedding_model = EmbeddingModel()

    texts = [
        chunk["content"]
        for chunk in chunks
    ]

    embeddings = embedding_model.encode(texts)

    print(f"Chunks: {len(chunks)}")
    print(f"Embeddings: {len(embeddings)}")
    print(f"Dimensions: {len(embeddings[0])}")

    print("\nStoring in ChromaDB")
    print("=" * 50)

    vector_store = VectorStore()

    vector_store.add_chunks(
        chunks,
        embeddings
    )

    print(
        f"Stored vectors: "
        f"{vector_store.count()}"
    )


if __name__ == "__main__":
    main()