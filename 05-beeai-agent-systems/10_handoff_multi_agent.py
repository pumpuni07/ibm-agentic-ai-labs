"""Step 10 — Multi-agent handoff: a coordinator delegates to a specialist."""
from beeai_framework.agents.experimental import RequirementAgent
from beeai_framework.tools.handoff import HandoffTool
from core import SimpleCalculatorTool
from importlib import import_module

def build_system() -> RequirementAgent:
    make_chat_model = import_module("05_chat_model").make_chat_model
    math_specialist = RequirementAgent(
        llm=make_chat_model(),
        tools=[SimpleCalculatorTool()],
        name="MathSpecialist",
        description="Handles arithmetic questions precisely.",
    )
    coordinator = RequirementAgent(
        llm=make_chat_model(),
        tools=[HandoffTool(math_specialist)],
        name="Coordinator",
        description="Routes questions to the right specialist.",
    )
    return coordinator

if __name__ == "__main__":
    print(type(build_system()).__name__)
