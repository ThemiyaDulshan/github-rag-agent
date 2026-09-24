from google import genai

from app.config import GEMINI_API_KEY, GEMINI_MODEL


def main():
    client = genai.Client(api_key=GEMINI_API_KEY)

    interaction = client.interactions.create(
        model=GEMINI_MODEL,
        input="Explain what a RAG system is in one short sentence.",
    )

    print("\nGemini response:")
    print("-" * 50)
    print(interaction.output_text)
    print("-" * 50)


if __name__ == "__main__":
    main()