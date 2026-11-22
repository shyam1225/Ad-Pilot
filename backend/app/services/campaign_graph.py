from typing import TypedDict, Optional
from app.schemas.campaign import CampaignStrategy
from app.services.campaign_service import generate_campaign_strategy
from app.services.validation_service import (
    validate_budget_allocation,
    validate_recommended_platforms,
    validate_duplicate_platforms
)
from langgraph.graph import StateGraph, START, END

class CampaignState(TypedDict):
    campaign: dict
    strategy: Optional[CampaignStrategy]
    retry_count: int
    is_valid: bool
    error: Optional[str]

def generate_strategy_node(state: CampaignState):
    print("Generating campaign strategy...")

    strategy = generate_campaign_strategy(state["campaign"])

    return {
    "strategy": strategy,
    "error": None,
    "retry_count": state["retry_count"] + 1
}

def validate_strategy_node(state: CampaignState):
    print("Validating campaign strategy...")

    try:
        strategy = state["strategy"]
        campaign = state["campaign"]

        validate_budget_allocation(
            strategy,
            campaign["budget"]
        )

        validate_recommended_platforms(
            strategy,
            campaign["platforms"]
        )

        validate_duplicate_platforms(strategy)

        return {
            "is_valid": True,
            "error": None
        }

    except ValueError as e:
        return {
            "is_valid": False,
            "error": str(e)
        }
    
def decide_next_step(state: CampaignState):
    if state["is_valid"]:
        return "success"

    if state["retry_count"] < 3:
        print("Validation failed. Retrying...")
        return "retry"

    print("Maximum retries reached.")
    return "failed"
# Build graph
builder = StateGraph(CampaignState)

# Register nodes
builder.add_node("generate", generate_strategy_node)
builder.add_node("validate", validate_strategy_node)

# Define execution flow
builder.add_edge(START, "generate")
builder.add_edge("generate", "validate")

# Add conditional routing
builder.add_conditional_edges(
    "validate",
    decide_next_step,
    {
        "success": END,
        "retry": "generate",
        "failed": END
    }
)

campaign_graph = builder.compile()