import json
from app.services.llm_service import generate_response
from app.schemas.campaign import CampaignStrategy
from app.services.validation_service import validate_budget_allocation
from app.services.validation_service import validate_recommended_platforms
from app.services.validation_service import validate_duplicate_platforms
prompt = """
Create an advertising campaign for a smartphone launch.

Budget: 500000 INR.
Target audience: 18-30 years.
Objective: Brand Awareness.
"""

result = generate_response(prompt)


campaign_data = json.loads(result)
campaign = CampaignStrategy.model_validate(campaign_data)

print("\nCampaign Summary:")
print(campaign.summary)

print("\nRecommended Platforms:")
print(campaign.recommended_platforms)

print("\nBudget Allocation:")
for allocation in campaign.budget_allocation:
    print(allocation.platform, allocation.amount, allocation.reason)

print("\nAd Copy:")
for ad in campaign.ad_copy:
    print(ad)

validate_budget_allocation(campaign, 500000)
print("\nBudget validation passed!")

allowed_platforms = ["Instagram", "YouTube", "Facebook"]
validate_recommended_platforms(campaign, allowed_platforms)
print("Platform validation passed!")

validate_duplicate_platforms(campaign)
print("Duplicate platform validation passed!")