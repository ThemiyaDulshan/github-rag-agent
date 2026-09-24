from pathlib import Path

from app.language_detector import detect_language


SUPPORTED_ENCODINGS = [
    "utf-8",
    "utf-8-sig",
    "latin-1",
]


def read_text_file(path: Path) -> str | None:
    for encoding in SUPPORTED_ENCODINGS:
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
        except OSError:
            return None

    return None


def load_documents(repository_path: str, files: list[dict]) -> list[dict]:
    root = Path(repository_path)
    documents = []

    for file_info in files:
        if file_info["category"] is None:
            continue

        if file_info["binary"]:
            continue

        if file_info["size"] > 1_000_000:
            continue

        relative_path = Path(file_info["path"])
        absolute_path = root / relative_path

        content = read_text_file(absolute_path)

        if content is None:
            continue

        language = detect_language(
            file_info["extension"]
        )

        documents.append({
            "content": content,
            "path": str(relative_path),
            "extension": file_info["extension"],
            "category": file_info["category"],
            "language": language,
            "size": file_info["size"],
            "line_count": len(content.splitlines()),
        })

    return documents