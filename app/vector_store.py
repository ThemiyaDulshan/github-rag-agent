import chromadb


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

        self.collection = self.client.get_or_create_collection(
            name=collection_name
        )

    def add_chunks(
        self,
        chunks: list[dict],
        embeddings: list[list[float]]
    ):
        ids = []
        documents = []
        metadatas = []

        for index, (chunk, embedding) in enumerate(
            zip(chunks, embeddings)
        ):
            chunk_id = (
                f"{chunk['path']}:"
                f"{chunk['start_line']}:"
                f"{chunk['end_line']}:"
                f"{index}"
            )

            ids.append(chunk_id)
            documents.append(chunk["content"])

            metadatas.append({
                "path": chunk["path"],
                "language": chunk["language"],
                "category": chunk["category"],
                "type": chunk["type"],
                "name": chunk["name"] or "",
                "parent_class": (
                    chunk["parent_class"] or ""
                ),
                "start_line": chunk["start_line"],
                "end_line": chunk["end_line"],
            })

        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )

    def count(self) -> int:
        return self.collection.count()

    def search(
        self,
        query_embedding: list[float],
        n_results: int = 5
    ) -> list[dict]:
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        matches = []

        for document, metadata, distance in zip(
            documents,
            metadatas,
            distances
        ):
            matches.append({
                "content": document,
                "metadata": metadata,
                "distance": distance,
            })

        return matches