"""Step 6 — A ReAct agent wired with memory and the calculator tool."""
from beeai_framework.agents.react import ReActAgent
from beeai_framework.memory import UnconstrainedMemory
from core import SimpleCalculatorTool
from importlib import import_module

def build_agent() -> ReActAgent:
    make_chat_model = import_module("05_chat_model").make_chat_model
    return ReActAgent(
        llm=make_chat_model(),
        tools=[SimpleCalculatorTool()],
        memory=UnconstrainedMemory(),
    )

if __name__ == "__main__":
    print(type(build_agent()).__name__)
