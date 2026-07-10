"""LangGraph Intent-Based Workflow Router.

A StateGraph that classifies a user request (ride hailing, restaurant
order, groceries, or unclassifiable) and routes it to a specialized
handler node, each of which produces a service-specific structured
response via an LLM.

PROVENANCE: Based on the IBM Skills Network lab "Implement Workflow
Patterns with LangGraph" (Intent-Based Routing pattern). The graph
assembly, groceries/default handler bodies, and test cases are faithful
to the lab; RouterState's fields, the router node/decision function,
the LLM injection, and the ride-hailing/restaurant handler bodies were
not captured in the source material and are RECONSTRUCTED to the lab's
documented pattern.

The LLM is injected via configure_llm() so the graph runs against IBM
watsonx, OpenAI, or a deterministic fake model for offline testing.
"""

from typing import TypedDict

from langgraph.graph import StateGraph

_llm = None


def configure_llm(llm) -> None:
    """Inject the chat model used by all nodes (any LangChain chat model)."""
    global _llm
    _llm = llm


class RouterState(TypedDict):
    user_input: str
    task_type: str
    output: str


VALID_TASKS = {"ride_hailing_call", "restaurant_order", "groceries"}


def router_node(state: RouterState) -> RouterState:
    """Classify the request into a task type using the LLM."""
    prompt = f"""Classify the following user request into exactly one category.
    Respond with ONLY the category name, nothing else.

    Categories:
    - ride_hailing_call: transportation, rides, trips to a destination
    - restaurant_order: ordering prepared food from restaurants
    - groceries: shopping for grocery items and household supplies
    - default_handler: anything that fits none of the above

    User Request: "{state['user_input']}"
    """
    response = _llm.invoke(prompt)
    task = response.content.strip().lower()
    if task not in VALID_TASKS:
        task = "default_handler"
    return {**state, "task_type": task}


def router(state: RouterState) -> str:
    """Conditional-edge decision function: route on classified task type."""
    return state["task_type"]


def ride_hailing_node(state: RouterState) -> RouterState:
    prompt = f"""You are a ride-hailing dispatch assistant.

    Extract and organize from the request:
    - Pickup location and destination
    - Requested pickup time
    - Vehicle preferences or special requirements

    User Request: "{state['user_input']}"

    Provide a clear dispatch summary a driver can act on, including any
    missing details the rider should confirm.
    """
    response = _llm.invoke(prompt)
    return {
        **state,
        "task_type": "ride_hailing_call",
        "output": response.content.strip(),
    }


def restaurant_order_node(state: RouterState) -> RouterState:
    prompt = f"""You are a restaurant order assistant.

    Extract and organize from the request:
    - Items, quantities, and sizes
    - Delivery or pickup preference and address if given
    - Dietary notes or substitutions

    User Request: "{state['user_input']}"

    Provide a clear order summary the restaurant can prepare from,
    flagging anything that needs confirmation.
    """
    response = _llm.invoke(prompt)
    return {
        **state,
        "task_type": "restaurant_order",
        "output": response.content.strip(),
    }


def groceries_node(state: RouterState) -> RouterState:
    prompt = f"""You are a grocery delivery assistant.

    Shopping List:
    - All items with quantities
    - Preferred store or location
    - Budget considerations
    - Special instructions for finding items

    Delivery Details:
    - Delivery address (if provided)
    - Preferred delivery time window
    - Any special delivery instructions
    - Contact information for driver coordination

    Driver Instructions:
    - Substitution preferences (if item unavailable)
    - How to handle out-of-stock items
    - Any items requiring special handling (fragile, cold items)
    - Payment method (if mentioned)

    User Request: "{state['user_input']}"

    Provide a comprehensive delivery order summary that our driver can use to efficiently shop and deliver groceries.
    Include estimated pickup time and any special notes for the shopping trip.

    Format the response as a clear, organized delivery order that includes all necessary details for our driver service.
    """
    response = _llm.invoke(prompt)
    return {
        **state,
        "task_type": "groceries",
        "output": response.content.strip(),
    }


def default_handler_node(state: RouterState) -> RouterState:
    prompt = f"""
    I couldn't classify your request into a specific category.
    Let me provide general assistance for: "{state['user_input']}"

    I can help you with:
    - Ride hailing services
    -  Restaurant orders
    -  Grocery shopping

    Please rephrase your request to match one of these services, or if you need assistance with something else, I will connect you with our customer support team who can provide personalized help.

    Would you like me to:
    1. Help you rephrase your request for one of our services
    2. Connect you with customer support for additional assistance
    """
    response = _llm.invoke(prompt)
    return {
        **state,
        "task_type": "default_handler",
        "output": response.content.strip(),
    }


def build_app():
    """Assemble and compile the routing StateGraph."""
    workflow = StateGraph(RouterState)
    workflow.add_node("ride_hailing_call", ride_hailing_node)
    workflow.add_node("restaurant_order", restaurant_order_node)
    workflow.add_node("groceries", groceries_node)
    workflow.add_node("default_handler", default_handler_node)
    workflow.add_node("router", router_node)
    workflow.set_entry_point("router")
    workflow.add_conditional_edges(
        "router",
        router,
        {
            "groceries": "groceries",
            "restaurant_order": "restaurant_order",
            "ride_hailing_call": "ride_hailing_call",
            "default_handler": "default_handler",
        },
    )
    workflow.set_finish_point("ride_hailing_call")
    workflow.set_finish_point("restaurant_order")
    workflow.set_finish_point("groceries")
    workflow.set_finish_point("default_handler")
    return workflow.compile()


if __name__ == "__main__":
    import os

    if os.environ.get("USE_WATSONX", "").lower() == "true":
        from langchain_ibm import ChatWatsonx

        configure_llm(
            ChatWatsonx(
                model_id="ibm/granite-4-h-small",
                url=os.environ.get(
                    "WATSONX_URL", "https://us-south.ml.cloud.ibm.com"
                ),
                apikey=os.environ["WATSONX_APIKEY"],
                project_id=os.environ["WATSONX_PROJECT_ID"],
            )
        )
    else:
        raise SystemExit(
            "Set USE_WATSONX=true with credentials, or import this module "
            "and call configure_llm() with any LangChain chat model."
        )

    app = build_app()
    test_cases = [
        {"user_input": "I need a ride from downtown to the airport at 3pm"},
        {"user_input": "I want to order 2 large pepperoni pizzas for delivery"},
        {"user_input": "I need milk, bread, eggs, and vegetables for the week"},
        {"user_input": "What's the weather like today?"},
    ]
    for test_input in test_cases:
        result = app.invoke(test_input)
        print(f"question {test_input['user_input']}\n")
        print(f"task_type {result['task_type']}\n")
        print(f"output: {result['output']}\n")
        print("-" * 35)
