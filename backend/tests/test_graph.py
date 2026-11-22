from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class CampaignState(TypedDict):
    product_name: str
    objective: str
    message: str

def understand_campaign(state: CampaignState):
    print("Understanding campaign...")

    return {
        "message": f"Creating a campaign for {state['product_name']}"
    }


def generate_summary(state: CampaignState):
    print("Generating campaign summary...")

    return {
        "message": (
            f"{state['message']} "
            f"Objective: {state['objective']}"
        )
    }
def route_campaign(state: CampaignState):
    if state["objective"] == "Brand Awareness":
        return "summary"

    return "end"

graph_builder = StateGraph(CampaignState)


graph_builder.add_node("understand", understand_campaign)
graph_builder.add_node("summary", generate_summary)


graph_builder.add_edge(START, "understand")
graph_builder.add_conditional_edges(
    "understand",
    route_campaign,
    {
        "summary": "summary",
        "end": END
    }
)
graph_builder.add_edge("summary", END)


graph = graph_builder.compile()


result = graph.invoke({
    "product_name": "Smartphone",
    "objective": "Sales",
    "message": ""
})

print("\nFinal State:", result)