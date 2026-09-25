from app.embeddings import EmbeddingModel
from app.vector_store import VectorStore
from app.config import GEMINI_API_KEY, GEMINI_MODEL

from google import genai


class RAGPipeline:
    def __init__(self):
        self.embedding_model = EmbeddingModel()
        self.vector_store = VectorStore()
        self.client = genai.Client(
            api_key=GEMINI_API_KEY
        )

    def retrieve(
        self,
        question: str,
        n_results: int = 5
    ) -> list[dict]:
        query_embedding = self.embedding_model.encode_one(
            question
        )

        return self.vector_store.search(
            query_embedding,
            n_results=n_results
        )

    def build_context(
        self,
        results: list[dict]
    ) -> str:
        context_parts = []

        for index, result in enumerate(
            results,
            start=1
        ):
            metadata = result["metadata"]

            source = (
                f"{metadata['path']}:"
                f"{metadata['start_line']}-"
                f"{metadata['end_line']}"
            )

            context_parts.append(
                f"[Source {index}: {source}]\n"
                f"{result['content']}"
            )

        return "\n\n".join(context_parts)

    def generate_answer(
        self,
        question: str,
        context: str
    ) -> str:
        prompt = f"""
You are a codebase analysis assistant.

Answer the user's question using only the provided repository context.

If the context does not contain enough information to answer the question, say that the repository context does not provide enough information.

Do not invent files, functions, classes, line numbers, or implementation details.

Include relevant source references using the format:
[file path, lines X-Y]

Repository context:
{context}

User question:
{question}
"""

        interaction = self.client.interactions.create(
            model=GEMINI_MODEL,
            input=prompt
        )

        return interaction.output_text

    def ask(
        self,
        question: str,
        n_results: int = 5
    ) -> dict:
        results = self.retrieve(
            question,
            n_results
        )

        context = self.build_context(
            results
        )

        answer = self.generate_answer(
            question,
            context
        )

        return {
            "question": question,
            "answer": answer,
            "sources": results,
        }