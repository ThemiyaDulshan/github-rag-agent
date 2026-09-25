import json

from groq import Groq

from app.config import GROQ_API_KEY, GROQ_MODEL


def get_repository_info(repository_name: str) -> str:
    return f"Repository received: {repository_name}"


def main():
    client = Groq(
        api_key=GROQ_API_KEY
    )

    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_repository_info",
                "description": "Get information about a repository.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository_name": {
                            "type": "string",
                            "description": "Name of the repository."
                        }
                    },
                    "required": ["repository_name"]
                }
            }
        }
    ]

    messages = [
        {
            "role": "user",
            "content": "Use the get_repository_info tool for the Flask repository."
        }
    ]

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    message = response.choices[0].message

    print("\nGroq Tool Calling Test")
    print("=" * 60)
    print("Content:")
    print(message.content)
    print("\nTool calls:")
    print(message.tool_calls)

    if message.tool_calls:
        messages.append(message)

        for tool_call in message.tool_calls:
            arguments = json.loads(
                tool_call.function.arguments
            )

            result = get_repository_info(
                **arguments
            )

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_call.function.name,
                "content": result
            })

        final_response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages
        )

        print("\nFinal response:")
        print("-" * 60)
        print(final_response.choices[0].message.content)


if __name__ == "__main__":
    main()