import json

from app.services.llm_service import generate_response
from app.schemas.campaign import CampaignStrategy
from app.services.validation_service import (
    validate_budget_allocation,
    validate_recommended_platforms,
    validate_duplicate_platforms
)


def build_campaign_prompt(campaign):
    return f"""
    You are an expert digital marketing strategist.

    Create an advertising campaign using only the information provided below.

    Product: {campaign['product_name']}
    Target Audience: {campaign['target_audience']}
    Budget: {campaign['budget']} INR
    Objective: {campaign['objective']}
    Allowed Platforms: {campaign['platforms']}

    Important instructions:

    1. Recommend only platforms from the allowed platforms list.
    2. Allocate the entire campaign budget.
    3. Do not include duplicate platforms.
    4. Provide a practical and realistic advertising strategy.
    5. Do not invent product specifications, features, or capabilities.
    6. Do not invent discounts, promotional offers, prices, or guarantees.
    7. Do not invent brand names or product details.
    8. Base all product-related claims strictly on the supplied information.
    9. If product specifications are not provided, use general marketing
       language without making specific product claims.
    10. Make the ad copy relevant to the target audience and campaign objective.

    Return a structured response containing:
    - summary
    - recommended_platforms
    - budget_allocation (platform, amount, reason)
    - ad_copy
    """

def create_campaign(campaign):
    strategy = generate_campaign_strategy(campaign)

    validated_strategy = validate_campaign(
        strategy,
        campaign
    )

    return {
        "message": "Campaign created successfully",
        "campaign_details": campaign,
        "strategy": validated_strategy
    }

def generate_campaign_strategy(campaign):
    prompt = build_campaign_prompt(campaign)

    result = generate_response(prompt)

    campaign_data = json.loads(result)

    strategy = CampaignStrategy.model_validate(campaign_data)

    return strategy

def validate_campaign(strategy, campaign):
    validate_budget_allocation(
        strategy,
        campaign["budget"]
    )

    validate_recommended_platforms(
        strategy,
        campaign["platforms"]
    )

    validate_duplicate_platforms(strategy)

    return strategy