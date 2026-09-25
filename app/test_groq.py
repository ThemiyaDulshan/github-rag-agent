from groq import Groq

from app.config import GROQ_API_KEY, GROQ_MODEL


def main():
    client = Groq(
        api_key=GROQ_API_KEY
    )

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "user",
                "content": "Explain what RAG is in one short sentence."
            }
        ]
    )

    print("\nGroq response:")
    print("-" * 50)
    print(response.choices[0].message.content)
    print("-" * 50)


if __name__ == "__main__":
    main()