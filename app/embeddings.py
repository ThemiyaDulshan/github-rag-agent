from functools import lru_cache

from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_embedding_model(model_name: str = MODEL_NAME):
    return SentenceTransformer(model_name)


class EmbeddingModel:
    def __init__(self, model_name: str = MODEL_NAME):
        self.model = get_embedding_model(model_name)

    def encode(self, texts: list[str]) -> list[list[float]]:
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=True
        )

        return embeddings.tolist()

    def encode_one(self, text: str) -> list[float]:
        embedding = self.model.encode(
            text,
            convert_to_numpy=True
        )

        return embedding.tolist()

    def dimension(self) -> int:
        return self.model.get_embedding_dimension()