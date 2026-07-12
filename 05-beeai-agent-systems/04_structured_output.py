"""Step 4 — Structured output with a Pydantic schema (BusinessPlan)."""
from core import BusinessPlan

def demo_plan() -> BusinessPlan:
    return BusinessPlan(
        company_name="AquaSense",
        mission="Make coastal water quality visible to everyone.",
        target_market="Municipal water authorities",
        revenue_streams=["sensor subscriptions", "analytics dashboard"],
        first_year_goal="Deploy 50 sensor buoys across two estuaries.",
    )

if __name__ == "__main__":
    print(demo_plan().model_dump_json(indent=2))
