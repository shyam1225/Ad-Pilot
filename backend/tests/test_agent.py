from app.services.agent_service import llm
from app.services.tools import calculate_budget, recommend_platforms
from langchain.agents import create_agent

agent = create_agent(
    model=llm,
    tools=[calculate_budget, recommend_platforms],
    system_prompt="""
You are an advertising campaign assistant.

Follow these instructions:

1. If the user asks for platform recommendations,
   use the recommend_platforms tool.

2. If the user asks for budget allocation,
   use the calculate_budget tool.

3. If the user asks for both:
   - First recommend the platforms.
   - Then use the recommended platforms
     to calculate the budget allocation.

4. Explain the final result clearly.
""")

response = agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": (
                "Create a Brand Awareness campaign with a budget "
"of 500000 INR. Recommend platforms and allocate "
"the budget equally across them."
            )
        }
    ]
})

for message in response["messages"]:

    print("\nMessage type:", type(message).__name__)

    if hasattr(message, "tool_calls") and message.tool_calls:
        print("Tool calls:", message.tool_calls)

    if message.content:
        print("Content:", message.content)