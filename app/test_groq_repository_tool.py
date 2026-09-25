import json

from groq import Groq

from app.config import GROQ_API_KEY, GROQ_MODEL
from app.github_loader import load_repository
from app.repository_agent_tools import RepositoryTools


def main():
    repository_url = "https://github.com/pallets/flask"
    repository_path = "data/repositories/langgraph-agent-test"

    load_repository(
        repository_url,
        repository_path
    )

    repository_tools = RepositoryTools(
        repository_path
    )

    client = Groq(
        api_key=GROQ_API_KEY
    )

    tools = [
        {
            "type": "function",
            "function": {
                "name": "definition_lookup",
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
                            "description": "Optional definition type: function or class."
                        }
                    },
                    "required": ["name"]
                }
            }
        }
    ]

    messages = [
        {
            "role": "user",
            "content": "Where is the Flask class implemented? Use the definition_lookup tool."
        }
    ]

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    message = response.choices[0].message

    print("\nRepository Tool Test")
    print("=" * 60)
    print("Initial response:")
    print(message)

    if not message.tool_calls:
        print("\nThe model did not request a tool.")
        return

    messages.append(message)

    for tool_call in message.tool_calls:
        arguments = json.loads(
            tool_call.function.arguments
        )

        result = repository_tools.definition_lookup(
            **arguments
        )

        print("\nTool called:")
        print(tool_call.function.name)

        print("\nArguments:")
        print(arguments)

        print("\nTool result:")
        print(result)

        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": tool_call.function.name,
            "content": json.dumps(result)
        })

    final_response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages
    )

    print("\nFinal answer:")
    print("-" * 60)
    print(final_response.choices[0].message.content)


if __name__ == "__main__":
    main()