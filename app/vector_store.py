import chromadb

from app.chunker import create_chunks
from app.document_loader import load_documents
from app.embeddings import EmbeddingModel


CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "github_code"


class VectorStore:
    def __init__(
        self,
        path: str = CHROMA_PATH,
        collection_name: str = COLLECTION_NAME
    ):
        self.client = chromadb.PersistentClient(
            path=path
        )
        self.collection_name = collection_name
        self.collection = self._get_collection()

    def _get_collection(self):
        return self.client.get_or_create_collection(
            name=self.collection_name
        )

    def reset(self):
        try:
            self.client.delete_collection(
                name=self.collection_name
            )
        except Exception:
            pass

        self.collection = self.client.get_or_create_collection(
            name=self.collection_name
        )

    def add_chunks(
        self,
        chunks: list[dict],
        embeddings: list[list[float]]
    ):
        documents = []
        metadatas = []
        ids = []

        for index, (chunk, embedding) in enumerate(
            zip(chunks, embeddings)
        ):
            metadata = {
                "path": chunk["path"],
                "language": chunk["language"],
                "category": chunk["category"],
                "type": chunk["type"],
                "name": chunk["name"] or "",
                "parent_class": chunk["parent_class"] or "",
                "start_line": chunk["start_line"],
                "end_line": chunk["end_line"],
            }

            documents.append(chunk["content"])
            metadatas.append(metadata)
            ids.append(f"chunk-{index}")

        if not documents:
            return

        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings
        )

    def search(
        self,
        query_embedding: list[float],
        n_results: int = 5
    ) -> list[dict]:
        count = self.collection.count()

        if count == 0:
            return []

        n_results = min(
            n_results,
            count
        )

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )

        documents = results.get(
            "documents",
            [[]]
        )[0]

        metadatas = results.get(
            "metadatas",
            [[]]
        )[0]

        distances = results.get(
            "distances",
            [[]]
        )[0]

        matches = []

        for document, metadata, distance in zip(
            documents,
            metadatas,
            distances
        ):
            matches.append({
                "content": document,
                "metadata": metadata,
                "distance": distance
            })

        return matches

    def count(self) -> int:
        return self.collection.count()


def build_index(
    repository_path: str,
    files: list[dict]
) -> dict:
    documents = load_documents(
        repository_path,
        files
    )

    chunks = create_chunks(
        documents
    )

    if not chunks:
        raise ValueError(
            "No indexable chunks were found in the repository"
        )

    embedding_model = EmbeddingModel()

    texts = [
        chunk["content"]
        for chunk in chunks
    ]

    embeddings = embedding_model.encode(
        texts
    )

    vector_store = VectorStore()

    vector_store.reset()

    vector_store.add_chunks(
        chunks,
        embeddings
    )

    return {
        "documents": len(documents),
        "chunks": len(chunks),
        "embeddings": len(embeddings),
        "dimensions": len(embeddings[0]),
    }


def search(
    query: str,
    n_results: int = 5
) -> list[dict]:
    embedding_model = EmbeddingModel()

    query_embedding = embedding_model.encode_one(
        query
    )

    vector_store = VectorStore()

    return vector_store.search(
        query_embedding,
        n_results=n_results
    )