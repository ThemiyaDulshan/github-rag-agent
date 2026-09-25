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


def get_repository_structure(
    repository_path: str,
    max_depth: int = 4
) -> str:
    root = Path(repository_path)

    if not root.exists():
        raise FileNotFoundError(
            f"Repository not found: {repository_path}"
        )

    lines = [root.name]

    def walk(directory: Path, prefix: str, depth: int):
        if depth >= max_depth:
            return

        try:
            entries = sorted(
                directory.iterdir(),
                key=lambda path: (
                    path.is_file(),
                    path.name.lower()
                )
            )
        except OSError:
            return

        entries = [
            entry
            for entry in entries
            if entry.name not in IGNORED_DIRECTORIES
        ]

        for index, entry in enumerate(entries):
            is_last = index == len(entries) - 1

            connector = "└── " if is_last else "├── "

            lines.append(
                f"{prefix}{connector}{entry.name}"
            )

            if entry.is_dir():
                extension = "    " if is_last else "│   "

                walk(
                    entry,
                    prefix + extension,
                    depth + 1
                )

    walk(root, "", 0)

    return "\n".join(lines)


def get_file(
    repository_path: str,
    file_path: str,
    line_start: int | None = None,
    line_end: int | None = None
) -> dict:
    root = Path(repository_path).resolve()
    target = (root / file_path).resolve()

    try:
        target.relative_to(root)
    except ValueError:
        raise ValueError(
            "File path is outside the repository"
        )

    if not target.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    if not target.is_file():
        raise ValueError(
            f"Path is not a file: {file_path}"
        )

    try:
        content = target.read_text(
            encoding="utf-8"
        )
    except UnicodeDecodeError:
        content = target.read_text(
            encoding="latin-1"
        )

    lines = content.splitlines()

    total_lines = len(lines)

    if line_start is None:
        line_start = 1

    line_start = max(
        1,
        line_start
    )

    if line_end is None:
        line_end = min(
            line_start + 199,
            total_lines
        )

    line_end = min(
        line_end,
        total_lines
    )

    selected_lines = lines[
        line_start - 1:line_end
    ]

    numbered_content = "\n".join(
        f"{number}: {line}"
        for number, line in enumerate(
            selected_lines,
            start=line_start
        )
    )

    return {
        "path": file_path,
        "content": numbered_content,
        "line_start": line_start,
        "line_end": line_end,
        "line_count": total_lines,
    }