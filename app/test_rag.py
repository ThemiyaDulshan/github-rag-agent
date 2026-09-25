from app.rag import RAGPipeline


def main():
    question = input(
        "\nAsk a question about the repository: "
    ).strip()

    rag = RAGPipeline()

    print("\nRetrieving repository context...")
    print("=" * 60)

    result = rag.ask(
        question,
        n_results=5
    )

    print("\nAnswer")
    print("=" * 60)
    print(result["answer"])

    print("\nRetrieved Sources")
    print("=" * 60)

    for index, source in enumerate(
        result["sources"],
        start=1
    ):
        metadata = source["metadata"]

        print(
            f"{index}. "
            f"{metadata['path']} "
            f"("
            f"lines "
            f"{metadata['start_line']}-"
            f"{metadata['end_line']}"
            f")"
        )


if __name__ == "__main__":
    main()