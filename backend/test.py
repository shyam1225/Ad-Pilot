
from app.services.llm_service import generate_response

prompt = """
Create an advertising campaign for a new smartphone.

Budget: 500000 INR
Target audience: People aged 18-30 in India
Objective: Brand Awareness

Recommend platforms, allocate the budget,
and generate advertising copy.
"""

result = generate_response(prompt)

print(result)

print("\nCampaign Summary:")
print(result.summary)

print("\nRecommended Platforms:")
print(result.recommended_platforms)

print("\nBudget Allocation:")

for allocation in result.budget_allocation:
    print(allocation.platform, allocation.amount)

print("\nAd Copy:")

for copy in result.ad_copy:
    print(copy)
