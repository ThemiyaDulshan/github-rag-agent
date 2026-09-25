from pathlib import Path

from app.code_parser import parse_python_code


SUPPORTED_EXTENSIONS = {".py"}


def find_definitions(
    repository_path: str,
    name: str,
    definition_type: str | None = None
) -> list[dict]:
    root = Path(repository_path)

    if not root.exists():
        raise FileNotFoundError(
            f"Repository not found: {repository_path}"
        )

    if not name:
        return []

    results = []

    for path in root.rglob("*"):
        if not path.is_file():
            continue

        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        try:
            content = path.read_text(
                encoding="utf-8"
            )
        except (OSError, UnicodeDecodeError):
            continue

        parsed = parse_python_code(content)

        for node in parsed["nodes"]:
            if node["name"] != name:
                continue

            if (
                definition_type is not None
                and node["type"] != definition_type
            ):
                continue

            results.append({
                "path": str(path.relative_to(root)),
                "type": node["type"],
                "name": node["name"],
                "start_line": node["start_line"],
                "end_line": node["end_line"],
                "parent_class": node["parent_class"],
            })

    return results