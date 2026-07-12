"""Step 7 — ReAct agent with built-in tools (weather + think)."""
from beeai_framework.agents.react import ReActAgent
from beeai_framework.memory import UnconstrainedMemory
from beeai_framework.tools.weather import OpenMeteoTool
from importlib import import_module

def build_agent() -> ReActAgent:
    make_chat_model = import_module("05_chat_model").make_chat_model
    return ReActAgent(
        llm=make_chat_model(),
        tools=[OpenMeteoTool()],
        memory=UnconstrainedMemory(),
    )

if __name__ == "__main__":
    print([t.name for t in build_agent()._input.tools])
