from app.code_parser import parse_python_code


MAX_CHUNK_LINES = 150
TEXT_CHUNK_LINES = 100


def split_text_into_chunks(
    document: dict,
    content: str,
    start_line: int = 1
) -> list[dict]:
    lines = content.splitlines()
    chunks = []

    for index in range(0, len(lines), TEXT_CHUNK_LINES):
        chunk_lines = lines[index:index + TEXT_CHUNK_LINES]

        if not chunk_lines:
            continue

        chunk_start = start_line + index
        chunk_end = chunk_start + len(chunk_lines) - 1

        chunks.append({
            "content": "\n".join(chunk_lines),
            "path": document["path"],
            "language": document["language"],
            "category": document["category"],
            "type": "document",
            "name": None,
            "parent_class": None,
            "start_line": chunk_start,
            "end_line": chunk_end,
        })

    return chunks


def create_python_chunks(document: dict) -> list[dict]:
    content = document["content"]
    lines = content.splitlines()

    parsed = parse_python_code(content)

    nodes = parsed["nodes"]
    imports = parsed["imports"]

    chunks = []

    for node in nodes:
        start = node["start_line"]
        end = node["end_line"]

        if end - start + 1 > MAX_CHUNK_LINES:
            chunk_content = "\n".join(
                lines[start - 1:start - 1 + MAX_CHUNK_LINES]
            )
            end = start + len(
                chunk_content.splitlines()
            ) - 1
        else:
            chunk_content = "\n".join(
                lines[start - 1:end]
            )

        chunks.append({
            "content": chunk_content,
            "path": document["path"],
            "language": document["language"],
            "category": document["category"],
            "type": node["type"],
            "name": node["name"],
            "parent_class": node["parent_class"],
            "start_line": start,
            "end_line": end,
            "imports": imports,
        })

    return chunks


def create_chunks(documents: list[dict]) -> list[dict]:
    chunks = []

    for document in documents:
        if document["language"] == "Python":
            python_chunks = create_python_chunks(document)

            if python_chunks:
                chunks.extend(python_chunks)
            else:
                chunks.extend(
                    split_text_into_chunks(
                        document,
                        document["content"]
                    )
                )
        else:
            chunks.extend(
                split_text_into_chunks(
                    document,
                    document["content"]
                )
            )

    return chunks