import json

from app.repository_agent_tools import RepositoryTools


def build_tool_definitions():
    return [
        {
            "type": "function",
            "function": {
                "name": "repo_browser.repository_structure",
                "description": "Get the directory and file structure of the repository.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "max_depth": {
                            "type": "integer",
                            "description": "Maximum directory depth to display."
                        }
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "repo_browser.code_search",
                "description": "Search repository files for a text or code pattern.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Text or code pattern to search for."
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results."
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "repo_browser.open_file",
                "description": "Read a specific section of a repository file. Use path and optionally line_start and line_end.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Relative path of the file to read."
                        },
                        "line_start": {
                            "type": "integer",
                            "description": "Starting line number."
                        },
                        "line_end": {
                            "type": "integer",
                            "description": "Ending line number."
                        }
                    },
                    "required": ["path"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "repo_browser.definition_lookup",
                "description": "Find function or class definitions by name in the repository.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Function or class name to find."
                        },
                        "definition_type": {
                            "type": "string",
                            "description": "Optional definition type such as function or class."
                        }
                    },
                    "required": ["name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "repo_browser.reference_lookup",
                "description": "Find references to a function, class, or symbol in the repository.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Function, class, or symbol name."
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results."
                        }
                    },
                    "required": ["name"]
                }
            }
        }
    ]


def execute_tool(
    repository_path: str,
    tool_name: str,
    arguments: dict
):
    tools = RepositoryTools(
        repository_path
    )

    normalized_name = tool_name.split(".")[-1]

    if normalized_name == "repository_structure":
        return tools.repository_structure(
            max_depth=arguments.get(
                "max_depth",
                4
            )
        )

    if normalized_name in {
        "code_search",
        "search_code"
    }:
        return tools.code_search(
            query=arguments["query"],
            max_results=arguments.get(
                "max_results",
                50
            )
        )

    if normalized_name in {
        "open_file",
        "file_lookup"
    }:
        file_path = arguments.get(
            "path",
            arguments.get("file_path")
        )

        if not file_path:
            raise ValueError(
                "File path was not provided"
            )

        return tools.file_lookup(
            file_path=file_path,
            line_start=arguments.get(
                "line_start"
            ),
            line_end=arguments.get(
                "line_end"
            )
        )

    if normalized_name == "definition_lookup":
        definition_type = arguments.get(
            "definition_type"
        )

        if definition_type == "":
            definition_type = None

        return tools.definition_lookup(
            name=arguments["name"],
            definition_type=definition_type
        )

    if normalized_name == "reference_lookup":
        return tools.reference_lookup(
            name=arguments["name"],
            max_results=arguments.get(
                "max_results",
                50
            )
        )

    raise ValueError(
        f"Unknown tool: {tool_name}"
    )


def execute_tool_call(
    repository_path: str,
    tool_call
):
    arguments = json.loads(
        tool_call.function.arguments
    )

    result = execute_tool(
        repository_path,
        tool_call.function.name,
        arguments
    )

    return {
        "role": "tool",
        "tool_call_id": tool_call.id,
        "name": tool_call.function.name,
        "content": json.dumps(
            result,
            default=str
        )
    }