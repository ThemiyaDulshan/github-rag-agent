from langgraph.graph import StateGraph, START, END
from groq import Groq

from app.agent_state import AgentState
from app.config import GROQ_API_KEY, GROQ_MODEL
from app.groq_tools import build_tool_definitions, execute_tool_call


SYSTEM_PROMPT = """You are a read-only GitHub repository code analysis agent.

You can inspect the repository using the available tools.

Never modify files, create files, delete files, commit changes, or perform any write operation.

Use repository tools when the question requires information about the codebase.

When answering, provide specific file paths and line numbers when available.

Keep answers concise and grounded in repository evidence.
"""


def call_model(state: AgentState) -> AgentState:
    client = Groq(
        api_key=GROQ_API_KEY
    )

    messages = state["messages"]

    if not messages:
        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": state["question"]
            }
        ]

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        tools=build_tool_definitions(),
        tool_choice="auto",
        max_tokens=1000
    )

    message = response.choices[0].message

    assistant_message = {
        "role": "assistant",
        "content": message.content or ""
    }

    if message.tool_calls:
        assistant_message["tool_calls"] = [
            {
                "id": tool_call.id,
                "type": "function",
                "function": {
                    "name": tool_call.function.name,
                    "arguments": tool_call.function.arguments
                }
            }
            for tool_call in message.tool_calls
        ]

    updated_messages = messages + [
        assistant_message
    ]

    return {
        "question": state["question"],
        "repository_path": state["repository_path"],
        "messages": updated_messages,
        "answer": message.content or "",
        "tool_calls": assistant_message.get("tool_calls", [])
    }


def execute_tools(state: AgentState) -> AgentState:
    last_message = state["messages"][-1]

    tool_messages = []

    for tool_call in last_message.get(
        "tool_calls",
        []
    ):
        class Function:
            pass

        class ToolCall:
            pass

        function = Function()
        function.name = tool_call["function"]["name"]
        function.arguments = tool_call["function"]["arguments"]

        tool_call_object = ToolCall()
        tool_call_object.id = tool_call["id"]
        tool_call_object.function = function

        tool_message = execute_tool_call(
            state["repository_path"],
            tool_call_object
        )

        content = tool_message["content"]

        if len(content) > 12000:
            content = content[:12000]

        tool_message["content"] = content

        tool_messages.append(
            tool_message
        )

    return {
        "question": state["question"],
        "repository_path": state["repository_path"],
        "messages": state["messages"] + tool_messages,
        "answer": state["answer"],
        "tool_calls": []
    }


def route_after_model(state: AgentState):
    if state["tool_calls"]:
        return "tools"

    return END


def build_graph(repository_path: str):
    graph = StateGraph(
        AgentState
    )

    graph.add_node(
        "model",
        call_model
    )

    graph.add_node(
        "tools",
        execute_tools
    )

    graph.add_edge(
        START,
        "model"
    )

    graph.add_conditional_edges(
        "model",
        route_after_model
    )

    graph.add_edge(
        "tools",
        "model"
    )

    return graph.compile()