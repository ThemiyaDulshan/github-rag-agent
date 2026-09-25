from app.github_loader import load_repository
from app.repository_agent_tools import RepositoryTools


def main():
    url = input(
        "Enter GitHub repository URL: "
    ).strip()

    destination = "data/repositories/tools-integration-test"

    load_repository(
        url,
        destination
    )

    tools = RepositoryTools(
        destination
    )

    print("\nRepository Structure")
    print("=" * 60)

    structure = tools.repository_structure(
        max_depth=2
    )

    print(structure)

    print("\nFile Lookup")
    print("=" * 60)

    file_result = tools.file_lookup(
        "src/flask/app.py"
    )

    print(
        f"File: {file_result['path']}"
    )

    print(
        f"Lines: {file_result['line_count']}"
    )

    print("\nCode Search")
    print("=" * 60)

    search_results = tools.code_search(
        "register_blueprint",
        max_results=5
    )

    for result in search_results:
        print(
            f"{result['path']}:"
            f"{result['line']}"
        )

    print("\nDefinition Lookup")
    print("=" * 60)

    definitions = tools.definition_lookup(
        "full_dispatch_request",
        "function"
    )

    for result in definitions:
        print(
            f"{result['path']} "
            f"{result['start_line']}-"
            f"{result['end_line']}"
        )

    print("\nReference Lookup")
    print("=" * 60)

    references = tools.reference_lookup(
        "full_dispatch_request",
        max_results=5
    )

    for result in references:
        print(
            f"{result['path']}:"
            f"{result['line']}"
        )

        print(
            f"  {result['content']}"
        )


if __name__ == "__main__":
    main()