"""Tests for the LangGraph intent router.

The compiled StateGraph is executed for REAL — entry point, router node,
conditional edges, handler nodes, and state merging are all genuine
LangGraph execution. Only the chat model is a deterministic
FakeListChatModel scripting the classification (and handler) outputs,
so each routing path can be verified exactly.
"""

import os
import sys

import pytest
from langchain_core.language_models.fake_chat_models import FakeListChatModel

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import router as r  # noqa: E402


def run_with_llm_script(responses, user_input):
    """Configure a scripted LLM, build the real graph, invoke it."""
    r.configure_llm(FakeListChatModel(responses=responses))
    app = r.build_app()
    return app.invoke({"user_input": user_input, "task_type": "", "output": ""})


class TestRoutingPaths:
    def test_ride_request_routes_to_ride_hailing(self):
        result = run_with_llm_script(
            ["ride_hailing_call", "Dispatch: downtown → airport, 3pm."],
            "I need a ride from downtown to the airport at 3pm",
        )
        assert result["task_type"] == "ride_hailing_call"
        assert "Dispatch" in result["output"]

    def test_pizza_request_routes_to_restaurant(self):
        result = run_with_llm_script(
            ["restaurant_order", "Order: 2 large pepperoni pizzas, delivery."],
            "I want to order 2 large pepperoni pizzas for delivery",
        )
        assert result["task_type"] == "restaurant_order"
        assert "pepperoni" in result["output"]

    def test_grocery_request_routes_to_groceries(self):
        result = run_with_llm_script(
            ["groceries", "Shopping list: milk, bread, eggs, vegetables."],
            "I need milk, bread, eggs, and vegetables for the week",
        )
        assert result["task_type"] == "groceries"
        assert "milk" in result["output"]

    def test_unrelated_request_falls_to_default_handler(self):
        result = run_with_llm_script(
            ["default_handler", "I could not classify this request."],
            "What's the weather like today?",
        )
        assert result["task_type"] == "default_handler"


class TestRouterRobustness:
    def test_garbage_classification_falls_back_to_default(self):
        # LLM returns something outside the valid task set
        result = run_with_llm_script(
            ["bananas!!", "Fallback response."],
            "gibberish request",
        )
        assert result["task_type"] == "default_handler"

    def test_classification_whitespace_and_case_normalized(self):
        result = run_with_llm_script(
            ["  GROCERIES \n", "List handled."],
            "buy apples",
        )
        assert result["task_type"] == "groceries"

    def test_original_input_preserved_in_final_state(self):
        result = run_with_llm_script(
            ["groceries", "ok"], "buy rice and beans"
        )
        assert result["user_input"] == "buy rice and beans"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
