from typing import Optional
from app.core.llm import generate_structured_output
from app.schemas.agent_schemas import (
    ProductIntelligence,
    CampaignStrategyDeliverable,
    CampaignPlan,
    AdCreativesDeliverable,
    GoogleSearchAd,
    SocialMediaAd
)
from app.services.tools import validate_ad_character_limits
from app.services.image_service import generate_visual_ad, build_ad_image_prompt


SYSTEM_PROMPT = """You are the Ad Generation Agent of AdPilot, an advanced AI advertising platform.
Your mission is to produce high-performing, platform-native ad creatives, headlines, body copy, and creative briefs.

Critical Guidelines:
1. Google Search Ads character limits are NON-NEGOTIABLE:
   - Every headline must be strictly 30 characters or fewer.
   - Every description must be strictly 90 characters or fewer.
2. For Social Media (Instagram, Facebook, LinkedIn, YouTube, etc.):
   - Write engaging, scroll-stopping primary copy aligned with the recommended tone.
   - Include a concise visual brief describing the image, video, or storyboard scene.
   - Specify a direct and relevant Call to Action (e.g., 'Learn More', 'Shop Now', 'Request Demo').
3. Strictly forbid unsupported promises: no '100% guaranteed', no fake awards, no miracle claims.
4. If revision feedback is provided, strictly adjust headlines, descriptions, or angles as requested.
"""


def run_ad_generation_agent(
    campaign_input: dict,
    product_intel: ProductIntelligence,
    strategy: CampaignStrategyDeliverable,
    plan: CampaignPlan,
    feedback: Optional[str] = None
) -> AdCreativesDeliverable:
    """
    Executes the Ad Generation Agent.
    """
    product_name = campaign_input.get("product_name", "Product")
    platforms = [item.platform for item in plan.budget_allocation]

    prompt = f"""
Generate high-impact ad creatives for {product_name}:

STRATEGY & POSITIONING:
- Campaign Theme: {strategy.campaign_theme}
- Positioning Statement: {strategy.positioning_statement}
- Messaging Pillars: {', '.join(strategy.messaging_pillars)}
- Recommended Tone: {product_intel.recommended_tone}
- Value Propositions: {', '.join(product_intel.value_propositions)}
- Core Benefits: {', '.join(product_intel.core_benefits)}

ACTIVE PLATFORMS: {', '.join(platforms)}
"""

    if feedback:
        prompt += f"""
REVISION DIRECTIVES FROM COMPLIANCE AUDIT (MUST FIX):
{feedback}
"""

    prompt += """
Generate a structured AdCreativesDeliverable:
1. search_ads: If 'Google Ads' is among the platforms, create 1-2 GoogleSearchAd objects:
   - headlines: 3 to 5 headlines (EACH <= 30 CHARACTERS STRICTLY)
   - descriptions: 2 to 3 descriptions (EACH <= 90 CHARACTERS STRICTLY)
   - path_1 & path_2: Short subpath (<= 15 chars)
2. social_ads: For each social platform (Instagram, Facebook, LinkedIn, YouTube, Snapchat), create 1-2 SocialMediaAd objects:
   - platform: platform name
   - format: e.g. 'Reel', 'Carousel', 'Sponsored Post'
   - primary_text: Engaging body copy
   - headline: Punchy card headline
   - call_to_action: Specific CTA
   - visual_brief: Scene description / storyboard prompt
3. ad_copy_summaries: 3-5 concise slogans or tagline summaries for executive overview
"""

    creatives = generate_structured_output(
        prompt=prompt,
        schema=AdCreativesDeliverable,
        system_prompt=SYSTEM_PROMPT,
        temperature=0.4
    )

    # Post-generation enforcement for Google Ads character constraints
    for search_ad in creatives.search_ads:
        trimmed_headlines = []
        for h in search_ad.headlines:
            if len(h) > 30:
                trimmed_headlines.append(h[:27].rstrip() + "...")
            else:
                trimmed_headlines.append(h)
        search_ad.headlines = trimmed_headlines

        trimmed_descriptions = []
        for d in search_ad.descriptions:
            if len(d) > 90:
                trimmed_descriptions.append(d[:87].rstrip() + "...")
            else:
                trimmed_descriptions.append(d)
        search_ad.descriptions = trimmed_descriptions

    # Generate visual sample ads for social ad variations
    for i, social_ad in enumerate(creatives.social_ads):
        try:
            image_prompt = build_ad_image_prompt(
                product_name=product_name,
                brand_tone=product_intel.recommended_tone,
                visual_brief=social_ad.visual_brief,
                platform=social_ad.platform
            )
            image_result = generate_visual_ad(
                prompt=image_prompt,
                headline=social_ad.headline or product_name,
                product_name=product_name,
                cta=social_ad.call_to_action,
                platform=social_ad.platform
            )
            social_ad.image_url = image_result["image_url"]
            social_ad.image_prompt = image_result["image_prompt"]
            social_ad.image_provider = image_result["provider"]
        except Exception as img_err:
            print(f"[Ad Generation] Notice: image generation fallback used for ad {i+1}: {img_err}")

    return creatives
