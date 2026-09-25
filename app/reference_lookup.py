from pathlib import Path


IGNORED_DIRECTORIES = {
    ".git",
    ".github",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    "env",
    "dist",
    "build",
}


MAX_FILE_SIZE = 1_000_000


def find_references(
    repository_path: str,
    name: str,
    max_results: int = 50
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
        if any(
            part in IGNORED_DIRECTORIES
            for part in path.parts
        ):
            continue

        if not path.is_file():
            continue

        try:
            if path.stat().st_size > MAX_FILE_SIZE:
                continue

            content = path.read_text(
                encoding="utf-8"
            )
        except (OSError, UnicodeDecodeError):
            continue

        lines = content.splitlines()

        for line_number, line in enumerate(
            lines,
            start=1
        ):
            if name not in line:
                continue

            relative_path = path.relative_to(root)

            results.append({
                "path": str(relative_path),
                "line": line_number,
                "content": line.strip(),
            })

            if len(results) >= max_results:
                return results

    return results