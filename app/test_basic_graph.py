from app.basic_graph import build_graph
from app.github_loader import load_repository


def main():
    url = input("Enter GitHub repository URL: ").strip()
    destination = "data/repositories/current"

    print("\nLoading and indexing repository...")

    repository = load_repository(
        url,
        destination
    )

    print("\nRepository ready.")
    print(
        f"Indexed {repository['index']['chunks']} chunks."
    )

    graph = build_graph(destination)

    while True:
        question = input(
            "\nEnter your question (or type 'exit'): "
        ).strip()

        if question.lower() == "exit":
            break

        if not question:
            continue

        result = graph.invoke({
            "question": question,
            "repository_path": destination,
            "messages": [],
            "answer": "",
            "tool_calls": []
        })

        print("\nLangGraph Agent")
        print("=" * 60)
        print(result["answer"])


if __name__ == "__main__":
    main()