from app.basic_graph import build_graph
from app.github_loader import load_repository


def main():
    url = input(
        "Enter GitHub repository URL: "
    ).strip()

    destination = "data/repositories/langgraph-agent-test"

    load_repository(
        url,
        destination
    )

    question = input(
        "\nEnter your question: "
    ).strip()

    graph = build_graph(
        destination
    )

    result = graph.invoke({
        "question": question,
        "repository_path": destination,
        "messages": [],
        "answer": ""
    })

    print("\nLangGraph Agent Test")
    print("=" * 60)
    print(result["answer"])


if __name__ == "__main__":
    main()