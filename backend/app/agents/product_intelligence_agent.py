from typing import Optional
from app.core.llm import generate_structured_output
from app.schemas.agent_schemas import ProductIntelligence


SYSTEM_PROMPT = """You are the Product Intelligence Agent of AdPilot, an advanced AI advertising platform.
Your objective is to conduct a thorough analysis of the advertised product or service based on the provided inputs.

Guidelines:
1. Extract true user-centric benefits rather than mere technical specs.
2. Formulate 2-3 detailed target customer personas, identifying realistic pain points, demographics, and emotional motivators.
3. Formulate clear Unique Selling Propositions (USPs) and a defensible positioning angle.
4. Align the recommended brand tone with the specified audience and product category.
5. Do not invent unverifiable claims (e.g. false certifications, non-existent awards, or imaginary discounts).
"""


def build_product_intelligence_prompt(campaign_input: dict) -> str:
    product_name = campaign_input.get("product_name", "Unknown Product")
    target_audience = campaign_input.get("target_audience", "General Public")
    product_description = campaign_input.get("product_description") or "Not provided. Infer core features from the product name and market standards."
    price_point = campaign_input.get("price_point") or "Market competitive"
    brand_tone = campaign_input.get("brand_tone") or "Professional and compelling"
    target_locations = campaign_input.get("target_locations") or ["National"]

    return f"""
Analyze this product and extract structured intelligence:

- Product Name: {product_name}
- Target Audience: {target_audience}
- Description & Features: {product_description}
- Price Point Context: {price_point}
- Desired Tone: {brand_tone}
- Target Geography: {', '.join(target_locations) if isinstance(target_locations, list) else target_locations}

Provide a structured ProductIntelligence output covering:
1. product_summary
2. core_benefits (list)
3. target_personas (list of customer personas with archetype name, demographics, pain points, desires)
4. value_propositions (list of USPs)
5. positioning_angle (strategic positioning statement)
6. recommended_tone
"""


def run_product_intelligence_agent(campaign_input: dict) -> ProductIntelligence:
    """
    Executes the Product Intelligence Agent to generate rich product and audience analysis.
    """
    prompt = build_product_intelligence_prompt(campaign_input)
    return generate_structured_output(
        prompt=prompt,
        schema=ProductIntelligence,
        system_prompt=SYSTEM_PROMPT,
        temperature=0.2
    )
