from pathlib import Path
from urllib.parse import urlparse
from collections import Counter

from git import Repo

from app.vector_store import build_index


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

FILE_CATEGORIES = {
    "source": {
        ".py",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".java",
        ".c",
        ".h",
        ".cpp",
        ".hpp",
        ".cc",
        ".cxx",
        ".go",
        ".rs",
        ".rb",
        ".php",
        ".swift",
        ".kt",
        ".kts",
        ".scala",
    },
    "documentation": {
        ".md",
        ".rst",
        ".txt",
        ".adoc",
    },
    "configuration": {
        ".json",
        ".yaml",
        ".yml",
        ".toml",
        ".ini",
        ".cfg",
        ".conf",
    },
    "web": {
        ".html",
        ".htm",
        ".css",
        ".scss",
        ".sass",
    },
    "database": {
        ".sql",
    },
    "scripts": {
        ".sh",
        ".bat",
        ".ps1",
    },
}

MAX_FILE_SIZE = 1_000_000


def parse_github_url(url: str) -> dict:
    parsed = urlparse(url)

    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Invalid URL scheme")

    if parsed.netloc != "github.com":
        raise ValueError("URL must be a GitHub repository URL")

    parts = parsed.path.strip("/").split("/")

    if len(parts) < 2:
        raise ValueError("URL must contain an owner and repository name")

    owner = parts[0]
    repository = parts[1]

    if repository.endswith(".git"):
        repository = repository[:-4]

    return {
        "owner": owner,
        "repository": repository,
        "url": url,
    }


def clone_repository(url: str, destination: str) -> Path:
    parse_github_url(url)

    destination_path = Path(destination)

    if destination_path.exists() and any(destination_path.iterdir()):
        raise FileExistsError(
            f"Destination already exists and is not empty: {destination}"
        )

    destination_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    Repo.clone_from(
        url,
        destination_path,
        depth=1
    )

    return destination_path


def get_file_category(path: Path) -> str | None:
    extension = path.suffix.lower()

    for category, extensions in FILE_CATEGORIES.items():
        if extension in extensions:
            return category

    return None


def is_binary_file(path: Path) -> bool:
    try:
        with path.open("rb") as file:
            chunk = file.read(8192)

        return b"\x00" in chunk

    except OSError:
        return True


def scan_repository(repository_path: str) -> dict:
    root = Path(repository_path)

    if not root.exists():
        raise FileNotFoundError(
            f"Repository not found: {repository_path}"
        )

    files = []
    extensions = Counter()
    categories = Counter()

    total_size = 0
    skipped_large_files = 0
    binary_files = 0
    relevant_files = 0

    directories = set()

    for path in root.rglob("*"):
        if any(
            part in IGNORED_DIRECTORIES
            for part in path.parts
        ):
            continue

        if not path.is_file():
            continue

        relative_path = path.relative_to(root)

        try:
            file_size = path.stat().st_size
        except OSError:
            continue

        total_size += file_size

        category = get_file_category(path)
        binary = is_binary_file(path)

        if binary:
            binary_files += 1

        if file_size > MAX_FILE_SIZE:
            skipped_large_files += 1

        if (
            category
            and not binary
            and file_size <= MAX_FILE_SIZE
        ):
            relevant_files += 1

        files.append({
            "path": str(relative_path),
            "extension": path.suffix.lower(),
            "category": category,
            "size": file_size,
            "binary": binary,
        })

        extension = path.suffix.lower()

        if extension:
            extensions[extension] += 1

        if category:
            categories[category] += 1

        if len(relative_path.parts) > 1:
            directories.add(
                str(relative_path.parent)
            )

    return {
        "repository_name": root.name,
        "total_files": len(files),
        "relevant_files": relevant_files,
        "total_size_bytes": total_size,
        "binary_files": binary_files,
        "skipped_large_files": skipped_large_files,
        "files": files,
        "extensions": dict(
            extensions.most_common()
        ),
        "categories": dict(
            categories.most_common()
        ),
        "directories": sorted(directories),
    }


def load_repository(
    url: str,
    destination: str
) -> dict:
    metadata = parse_github_url(url)

    repository_path = clone_repository(
        url,
        destination
    )

    scan_result = scan_repository(
        repository_path
    )

    index_result = build_index(
        str(repository_path),
        scan_result["files"]
    )

    return {
        **metadata,
        **scan_result,
        "index": index_result,
    }