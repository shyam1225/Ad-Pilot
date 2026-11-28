from typing import Optional
from app.core.llm import generate_structured_output
from app.schemas.agent_schemas import ProductIntelligence, CampaignStrategyDeliverable
from app.services.tools import recommend_platforms


SYSTEM_PROMPT = """You are the Campaign Strategy Agent of AdPilot, an advanced AI advertising platform.
Your responsibility is to design a high-converting, omnichannel marketing campaign strategy.

Guidelines:
1. Formulate a creative campaign theme / "Big Idea" that captures customer attention.
2. Formulate 3-4 distinct messaging pillars grounded in the product's value propositions.
3. Recommend platforms strictly chosen from the allowed platforms list provided by the user.
4. Establish clear funnel stages (TOFU: Awareness, MOFU: Consideration, BOFU: Conversion).
5. If revision feedback is provided, incorporate the necessary strategic corrections explicitly.
"""


def build_campaign_strategy_prompt(
    campaign_input: dict,
    product_intel: ProductIntelligence,
    feedback: Optional[str] = None
) -> str:
    objective = campaign_input.get("objective", "BRAND_AWARENESS")
    budget = campaign_input.get("budget", 0)
    allowed_platforms = campaign_input.get("platforms", ["Instagram", "Google Ads"])

    # Consult tool for benchmark recommendations
    suggested_platforms = recommend_platforms.invoke({"objective": objective})
    
    # Filter to intersect with allowed platforms
    valid_platform_candidates = [p for p in allowed_platforms if p in suggested_platforms]
    if not valid_platform_candidates:
        valid_platform_candidates = allowed_platforms

    prompt = f"""
Design the Campaign Strategy for this initiative:

CAMPAIGN OBJECTIVE: {objective}
TOTAL BUDGET: {budget} INR
ALLOWED PLATFORMS (STRICT): {allowed_platforms}
ALIGNED PLATFORM CANDIDATES: {valid_platform_candidates}

PRODUCT INTELLIGENCE DOSSIER:
- Summary: {product_intel.product_summary}
- Positioning Angle: {product_intel.positioning_angle}
- Core Benefits: {', '.join(product_intel.core_benefits)}
- Value Propositions: {', '.join(product_intel.value_propositions)}
- Target Personas: {', '.join([p.name for p in product_intel.target_personas])}
- Recommended Tone: {product_intel.recommended_tone}
"""

    if feedback:
        prompt += f"""
PREVIOUS AUDIT FEEDBACK (MUST REMEDIATE):
{feedback}
"""

    prompt += """
Provide a structured CampaignStrategyDeliverable containing:
1. campaign_theme: A creative big idea / unifying concept
2. positioning_statement: Clear market differentiation
3. messaging_pillars: 3-4 thematic narrative angles
4. target_audience_summary: Synthesis of audience targeting
5. recommended_platforms: Platforms selected from allowed platforms
6. funnel_stages: List of TOFU, MOFU, and BOFU strategies with objectives and channels
7. summary: Comprehensive strategic executive summary
"""
    return prompt


def run_campaign_strategy_agent(
    campaign_input: dict,
    product_intel: ProductIntelligence,
    feedback: Optional[str] = None
) -> CampaignStrategyDeliverable:
    """
    Executes the Campaign Strategy Agent.
    """
    prompt = build_campaign_strategy_prompt(campaign_input, product_intel, feedback)
    return generate_structured_output(
        prompt=prompt,
        schema=CampaignStrategyDeliverable,
        system_prompt=SYSTEM_PROMPT,
        temperature=0.3
    )
