"""Core building blocks for the BeeAI progression: a minimal prompt template,
a safety-hardened calculator tool built on the real BeeAI Tool pipeline, and
a structured-output schema. Shared by the numbered lab scripts."""

import re

from pydantic import BaseModel, Field
from beeai_framework.context import RunContext
from beeai_framework.emitter import Emitter
from beeai_framework.tools import StringToolOutput, Tool, ToolRunOptions


class SimplePromptTemplate:
    """A tiny {variable}-substitution template (lab warm-up before BeeAI's
    own PromptTemplate). Repeated variables are all substituted."""

    def __init__(self, template: str):
        self.template = template

    def render(self, **variables) -> str:
        rendered = self.template
        for key, value in variables.items():
            rendered = rendered.replace("{" + key + "}", str(value))
        return rendered


class CalculatorInput(BaseModel):
    expression: str = Field(description="Arithmetic expression, e.g. '2 + 3 * 4'")


class SimpleCalculatorTool(Tool[CalculatorInput, ToolRunOptions, StringToolOutput]):
    """Arithmetic tool on the real BeeAI Tool pipeline (emitter, schema
    validation, StringToolOutput). Safety contract: a strict character
    allow-list rejects anything but digits, whitespace, dot, and + - * / ( ).

    Documented quirk (kept faithful to the lab): '2**8' passes the character
    filter because '**' is two allowed '*' characters, so Python's power
    operator sneaks through the allow-list.
    """

    name = "simple_calculator"
    description = "Safely evaluate a basic arithmetic expression."
    input_schema = CalculatorInput

    def _create_emitter(self) -> Emitter:
        return Emitter.root().child(
            namespace=["tool", "calculator"], creator=self
        )

    @staticmethod
    def _safe_calculate(expression: str) -> float:
        allowed = re.fullmatch(r"[0-9+\-*/().\s]+", expression)
        if not allowed:
            raise ValueError(f"Expression contains disallowed characters: {expression!r}")
        try:
            result = eval(expression, {"__builtins__": {}}, {})
        except ZeroDivisionError:
            raise ValueError("Division by zero is not allowed.")
        except SyntaxError:
            raise ValueError(f"Invalid arithmetic expression: {expression!r}")
        return float(result)

    async def _run(
        self,
        input: CalculatorInput,
        options: ToolRunOptions | None,
        context: RunContext,
    ) -> StringToolOutput:
        try:
            return StringToolOutput(result=str(self._safe_calculate(input.expression)))
        except ValueError as error:
            return StringToolOutput(result=f"Calculator error: {error}")


class BusinessPlan(BaseModel):
    """Structured-output schema for the structured-generation lab step."""

    company_name: str = Field(description="Name of the company")
    mission: str = Field(description="One-sentence mission statement")
    target_market: str = Field(description="Primary customer segment")
    revenue_streams: list[str] = Field(description="Main ways the company earns money")
    first_year_goal: str = Field(description="Concrete goal for year one")
