from typing import TypedDict
from langgraph.graph import StateGraph, START, END


class CampaignState(TypedDict):
    budget: int
    allocated_budget: int
    retry_count: int
    is_valid: bool


# Node 1: Generate campaign
def generate_campaign(state: CampaignState):

    print("Generating campaign...")

    # Simulate an incorrect allocation on the first attempt
    if state["retry_count"] == 0:
        allocation = 400000
    else:
        allocation = 500000

    return {
        "allocated_budget": allocation
    }


# Node 2: Validate campaign
def validate_campaign(state: CampaignState):

    print("Validating campaign...")

    is_valid = state["budget"] == state["allocated_budget"]

    return {
        "is_valid": is_valid,
        "retry_count": state["retry_count"] + 1
    }


# Node 3: Decide whether to retry
def decide_next_step(state: CampaignState):

    if state["is_valid"]:
        return "success"

    if state["retry_count"] < 3:
        return "retry"

    return "failed"


# Build graph
builder = StateGraph(CampaignState)

builder.add_node("generate", generate_campaign)
builder.add_node("validate", validate_campaign)

builder.add_edge(START, "generate")
builder.add_edge("generate", "validate")

builder.add_conditional_edges(
    "validate",
    decide_next_step,
    {
        "success": END,
        "retry": "generate",
        "failed": END
    }
)

graph = builder.compile()


# Execute graph
result = graph.invoke({
    "budget": 500000,
    "allocated_budget": 0,
    "retry_count": 0,
    "is_valid": False
})

print("\nFinal State:", result)