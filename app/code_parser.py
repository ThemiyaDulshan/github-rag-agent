import ast


def get_node_name(node: ast.AST) -> str | None:
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return node.name

    return None


def get_node_type(node: ast.AST) -> str | None:
    if isinstance(node, ast.ClassDef):
        return "class"

    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return "function"

    return None


def get_imports(tree: ast.AST) -> list[str]:
    imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)

        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""

            for alias in node.names:
                if module:
                    imports.append(f"{module}.{alias.name}")
                else:
                    imports.append(alias.name)

    return sorted(set(imports))


def parse_python_code(content: str) -> dict:
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return {
            "nodes": [],
            "imports": [],
        }

    nodes = []

    def visit(node: ast.AST, parent_class: str | None = None):
        node_type = get_node_type(node)

        current_class = parent_class

        if node_type == "class":
            current_class = node.name

        if node_type in {"class", "function"}:
            if hasattr(node, "lineno"):
                end_line = getattr(
                    node,
                    "end_lineno",
                    node.lineno
                )

                nodes.append({
                    "type": node_type,
                    "name": node.name,
                    "start_line": node.lineno,
                    "end_line": end_line,
                    "parent_class": (
                        parent_class
                        if node_type == "function"
                        else None
                    ),
                })

        for child in ast.iter_child_nodes(node):
            visit(child, current_class)

    visit(tree)

    return {
        "nodes": sorted(
            nodes,
            key=lambda node: (
                node["start_line"],
                node["end_line"]
            )
        ),
        "imports": get_imports(tree),
    }