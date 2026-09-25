from app.github_loader import load_repository
from app.code_parser import parse_python_code


def main():
    url = "https://github.com/pallets/flask"
    destination = "data/repositories/parser-test"

    load_repository(
        url,
        destination
    )

    file_path = (
        "data/repositories/parser-test/"
        "src/flask/app.py"
    )

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:
        content = file.read()

    result = parse_python_code(content)

    print("Result type:")
    print(type(result))

    print("\nResult keys:")
    print(result.keys())

    print("\nResult:")
    print(result)


if __name__ == "__main__":
    main()