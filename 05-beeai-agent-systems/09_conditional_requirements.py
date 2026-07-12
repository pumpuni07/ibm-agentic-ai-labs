"""Step 9 — ConditionalRequirement: force thinking before calculating."""
from beeai_framework.agents.experimental import RequirementAgent
from beeai_framework.agents.experimental.requirements.conditional import ConditionalRequirement
from beeai_framework.tools.think import ThinkTool
from core import SimpleCalculatorTool
from importlib import import_module

def build_agent() -> RequirementAgent:
    make_chat_model = import_module("05_chat_model").make_chat_model
    return RequirementAgent(
        llm=make_chat_model(),
        tools=[ThinkTool(), SimpleCalculatorTool()],
        requirements=[ConditionalRequirement(ThinkTool, force_at_step=1)],
    )

if __name__ == "__main__":
    print(type(build_agent()).__name__)
