from typing import TypedDict


class AgentState(TypedDict):
    question: str
    repository_path: str
    messages: list
    answer: str
    tool_calls: list