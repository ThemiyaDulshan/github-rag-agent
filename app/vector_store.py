import hashlib
import json
from pathlib import Path

import chromadb

from app.chunker import create_chunks
from app.document_loader import load_documents
from app.embeddings import EmbeddingModel


CHROMA_PATH = "chroma_db"
COLLECTION_PREFIX = "github_code_"
METADATA_PATH = Path(CHROMA_PATH) / "repositories"


def get_repository_key(owner: str, repository: str) -> str:
    value = f"{owner}/{repository}".lower()
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:16]


def get_collection_name(
    owner: str,
    repository: str
) -> str:
    return (
        COLLECTION_PREFIX
        + get_repository_key(
            owner,
            repository
        )
    )


def get_metadata_path(
    owner: str,
    repository: str
) -> Path:
    return (
        METADATA_PATH
        / f"{get_repository_key(owner, repository)}.json"
    )


class VectorStore:
    def __init__(
        self,
        path: str = CHROMA_PATH,
        collection_name: str | None = None
    ):
        self.client = chromadb.PersistentClient(
            path=path
        )

        self.collection_name = (
            collection_name
            or f"{COLLECTION_PREFIX}default"
        )

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


def get_indexed_repository(
    owner: str,
    repository: str
) -> dict | None:
    metadata_path = get_metadata_path(
        owner,
        repository
    )

    if not metadata_path.exists():
        return None

    try:
        with metadata_path.open(
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError):
        return None


def is_indexed_repository(
    owner: str,
    repository: str
) -> bool:
    metadata = get_indexed_repository(
        owner,
        repository
    )

    if not metadata:
        return False

    collection = VectorStore(
        collection_name=get_collection_name(
            owner,
            repository
        )
    )

    return collection.count() > 0


def save_indexed_repository(
    owner: str,
    repository: str,
    index: dict
):
    METADATA_PATH.mkdir(
        parents=True,
        exist_ok=True
    )

    metadata_path = get_metadata_path(
        owner,
        repository
    )

    metadata = {
        "owner": owner,
        "repository": repository,
        "index": index
    }

    with metadata_path.open(
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            metadata,
            file,
            indent=2
        )


def build_index(
    repository_path: str,
    files: list[dict],
    owner: str | None = None,
    repository: str | None = None
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

    if not owner or not repository:
        repository_name = Path(
            repository_path
        ).name

        if "__" in repository_name:
            owner, repository = repository_name.split(
                "__",
                1
            )
        else:
            owner = "default"
            repository = repository_name

    collection_name = get_collection_name(
        owner,
        repository
    )

    vector_store = VectorStore(
        collection_name=collection_name
    )

    vector_store.reset()

    vector_store.add_chunks(
        chunks,
        embeddings
    )

    index = {
        "documents": len(documents),
        "chunks": len(chunks),
        "embeddings": len(embeddings),
        "dimensions": len(embeddings[0]),
    }

    save_indexed_repository(
        owner,
        repository,
        index
    )

    return index


def search(
    query: str,
    n_results: int = 5,
    owner: str | None = None,
    repository: str | None = None
) -> list[dict]:
    if not owner or not repository:
        raise ValueError(
            "Owner and repository are required for semantic search"
        )

    embedding_model = EmbeddingModel()

    query_embedding = embedding_model.encode_one(
        query
    )

    vector_store = VectorStore(
        collection_name=get_collection_name(
            owner,
            repository
        )
    )

    return vector_store.search(
        query_embedding,
        n_results=n_results
    )