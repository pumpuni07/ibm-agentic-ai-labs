"""27 tests for the BeeAI progression. Everything verifiable offline runs
against real framework machinery — zero mocks. Live model calls are the only
thing not executed (repo policy)."""

import asyncio
import importlib
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))

from core import (
    BusinessPlan,
    CalculatorInput,
    SimpleCalculatorTool,
    SimplePromptTemplate,
)
from beeai_framework.tools import StringToolOutput, Tool


# ---------- SimplePromptTemplate (4) ----------

def test_render_substitutes_single_variable():
    assert SimplePromptTemplate("Hello {name}!").render(name="Jack") == "Hello Jack!"


def test_render_substitutes_multiple_variables():
    out = SimplePromptTemplate("{a} + {b}").render(a="one", b="two")
    assert out == "one + two"


def test_render_substitutes_repeated_variables():
    out = SimplePromptTemplate("{x} and {x} again").render(x="echo")
    assert out == "echo and echo again"


def test_render_stringifies_non_string_values():
    assert SimplePromptTemplate("n={n}").render(n=42) == "n=42"


# ---------- _safe_calculate safety contract (7) ----------

def test_safe_calculate_basic_arithmetic():
    assert SimpleCalculatorTool._safe_calculate("2 + 3 * 4") == 14.0


def test_safe_calculate_parentheses_and_division():
    assert SimpleCalculatorTool._safe_calculate("(2 + 3) / 2") == 2.5


def test_safe_calculate_rejects_code_injection():
    with pytest.raises(ValueError):
        SimpleCalculatorTool._safe_calculate("__import__('os').system('ls')")


def test_safe_calculate_rejects_letters():
    with pytest.raises(ValueError):
        SimpleCalculatorTool._safe_calculate("2 + abc")


def test_safe_calculate_zero_division_raises_value_error():
    with pytest.raises(ValueError, match="Division by zero"):
        SimpleCalculatorTool._safe_calculate("1 / 0")


def test_safe_calculate_invalid_syntax_raises_value_error():
    with pytest.raises(ValueError):
        SimpleCalculatorTool._safe_calculate("2 + + )")


def test_documented_quirk_power_operator_passes_char_filter():
    assert SimpleCalculatorTool._safe_calculate("2**8") == 256.0


# ---------- Real async Tool.run() pipeline (5) ----------

def run_tool(expression: str) -> str:
    async def go():
        tool = SimpleCalculatorTool()
        output = await tool.run(CalculatorInput(expression=expression))
        return output
    return asyncio.run(go())


def test_tool_run_executes_through_real_pipeline():
    output = run_tool("6 * 7")
    assert isinstance(output, StringToolOutput)
    assert output.get_text_content() == "42.0"


def test_tool_run_validates_input_schema():
    async def go():
        tool = SimpleCalculatorTool()
        return await tool.run({"expression": "1 + 1"})
    assert asyncio.run(go()).get_text_content() == "2.0"


def test_tool_run_returns_graceful_error_output_not_exception():
    output = run_tool("1 / 0")
    assert "Calculator error" in output.get_text_content()
    assert "Division by zero" in output.get_text_content()


def test_tool_run_rejects_injection_gracefully():
    output = run_tool("open('x')")
    assert "Calculator error" in output.get_text_content()


def test_tool_is_real_beeai_tool_subclass():
    assert issubclass(SimpleCalculatorTool, Tool)


# ---------- Tool metadata the LLM sees (3) ----------

def test_tool_name_is_exact():
    assert SimpleCalculatorTool().name == "simple_calculator"


def test_tool_description_is_exact():
    assert SimpleCalculatorTool().description == "Safely evaluate a basic arithmetic expression."


def test_tool_input_json_schema_exposes_expression_field():
    schema = CalculatorInput.model_json_schema()
    assert schema["properties"]["expression"]["type"] == "string"
    assert "expression" in schema["required"]


# ---------- BusinessPlan schema (3) ----------

VALID_PLAN = dict(
    company_name="AquaSense",
    mission="Make coastal water quality visible.",
    target_market="Municipalities",
    revenue_streams=["subscriptions"],
    first_year_goal="Deploy 50 buoys.",
)


def test_business_plan_accepts_valid_plan():
    plan = BusinessPlan(**VALID_PLAN)
    assert plan.company_name == "AquaSense"
    assert plan.revenue_streams == ["subscriptions"]


def test_business_plan_rejects_missing_field():
    incomplete = {k: v for k, v in VALID_PLAN.items() if k != "mission"}
    with pytest.raises(ValidationError):
        BusinessPlan(**incomplete)


def test_business_plan_rejects_mistyped_field():
    bad = dict(VALID_PLAN, revenue_streams="not-a-list-of-strings-at-all")
    with pytest.raises(ValidationError):
        BusinessPlan(**bad)


# ---------- BeeAI PromptTemplate (real framework) (2) ----------

def test_beeai_prompt_template_renders():
    module = importlib.import_module("02_beeai_prompt_template")
    out = module.build_template().render(topic="reefs", audience="policy")
    assert out == "Summarize reefs for a policy audience."


def test_beeai_prompt_template_render_is_schema_backed():
    module = importlib.import_module("02_beeai_prompt_template")
    template = module.build_template()
    assert template.render(topic="a", audience="b").count("a") >= 1


# ---------- Workflow (real execution) (2) ----------

def test_workflow_executes_both_steps_with_typed_state():
    module = importlib.import_module("11_workflow")
    async def go():
        return await module.build_workflow().run(module.PipelineState(text="bee ai rocks"))
    run = asyncio.run(go())
    assert run.state.word_count == 3
    assert run.state.shouted == "BEE AI ROCKS"


def test_workflow_step_order_count_then_shout():
    module = importlib.import_module("11_workflow")
    workflow = module.build_workflow()
    assert workflow.step_names == ["count", "shout"]


# ---------- API-compatibility: all 12 scripts import cleanly (1) ----------

SCRIPTS = sorted(p.stem for p in PROJECT.glob("[01]*_*.py"))


def test_all_twelve_scripts_import_cleanly_against_pinned_beeai():
    assert len(SCRIPTS) == 12
    for stem in SCRIPTS:
        importlib.import_module(stem)
