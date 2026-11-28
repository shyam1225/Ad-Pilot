from math import isclose
from typing import Optional
from app.core.llm import generate_structured_output
from app.schemas.agent_schemas import (
    ProductIntelligence,
    CampaignStrategyDeliverable,
    CampaignPlan,
    AdCreativesDeliverable,
    ComplianceAudit,
    ComplianceViolation
)
from app.services.tools import (
    validate_ad_character_limits,
    check_advertising_compliance_rules
)


SYSTEM_PROMPT = """You are the Quality and Compliance Agent of AdPilot, an advanced AI advertising platform.
Your job is to act as a rigorous, impartial critic and safety gatekeeper for advertising campaigns.

Audit Checklist:
1. Policy Compliance: Adhere strictly to FTC and global advertising standards (no fake guarantees, deceptive promises, unproven medical/financial claims).
2. Grounded Claims & Hallucination Prevention: Verify that ad copy makes no ungrounded claims beyond the product intelligence.
3. Brand Tone Consistency: Ensure the copy aligns with the recommended brand tone.
4. Channel Alignment: Confirm creatives match their target platform specifications.

If critical violations exist, provide clear remediation directives and designate which agent must fix them:
- 'ad_generation' (for copy issues, character counts, ungrounded claims)
- 'planning' (for budget, format or flighting discrepancies)
- 'strategy' (for platform or core messaging misalignment)
"""


def run_compliance_agent(
    campaign_input: dict,
    product_intel: ProductIntelligence,
    strategy: CampaignStrategyDeliverable,
    plan: CampaignPlan,
    creatives: AdCreativesDeliverable
) -> ComplianceAudit:
    """
    Executes the Quality and Compliance Agent by combining programmatic rule verification
    with deep semantic evaluation.
    """
    total_budget = float(campaign_input.get("budget", 0))
    allowed_platforms = campaign_input.get("platforms", [])

    programmatic_violations: list[ComplianceViolation] = []

    # 1. Budget reconciliation check
    allocated_sum = sum(item.amount for item in plan.budget_allocation)
    if not isclose(allocated_sum, total_budget, abs_tol=0.5):
        programmatic_violations.append(
            ComplianceViolation(
                category="budget",
                severity="critical",
                message=f"Allocated total ({allocated_sum}) does not match campaign budget ({total_budget}).",
                remediation_instruction="Rebalance platform budget amounts to equal the total budget exactly."
            )
        )

    # 2. Platform selection check
    for item in plan.budget_allocation:
        if item.platform not in allowed_platforms:
            programmatic_violations.append(
                ComplianceViolation(
                    category="policy",
                    severity="critical",
                    message=f"Platform '{item.platform}' was not selected in allowed platforms: {allowed_platforms}.",
                    remediation_instruction=f"Remove '{item.platform}' from allocation and reassign to allowed platforms."
                )
            )

    # 3. Google Ads character limit verification
    for search_ad in creatives.search_ads:
        char_check = validate_ad_character_limits.invoke({
            "headlines": search_ad.headlines,
            "descriptions": search_ad.descriptions,
            "platform": "Google Ads"
        })
        for v in char_check.get("violations", []):
            programmatic_violations.append(
                ComplianceViolation(
                    category="character_limit",
                    severity="medium",
                    message=v,
                    remediation_instruction="Shorten headline to <= 30 chars or description to <= 90 chars."
                )
            )

    # 4. Prohibited claims regex rule verification
    all_texts = []
    for s in creatives.search_ads:
        all_texts.extend(s.headlines)
        all_texts.extend(s.descriptions)
    for soc in creatives.social_ads:
        all_texts.append(soc.primary_text)
        if soc.headline:
            all_texts.append(soc.headline)
    all_texts.extend(creatives.ad_copy_summaries)

    prohibited_hits = check_advertising_compliance_rules.invoke({"text_corpus": all_texts})
    for hit in prohibited_hits:
        programmatic_violations.append(
            ComplianceViolation(
                category="policy",
                severity="critical",
                message=f"Prohibited pattern detected in '{hit['matched_text']}': {hit['explanation']}",
                remediation_instruction="Remove absolute guarantee, miracle claim, or deceptive language."
            )
        )

    # 5. Semantic audit via LLM
    prompt = f"""
Audit this complete campaign bundle for quality, truthfulness, and brand alignment:

CAMPAIGN OBJECTIVE: {campaign_input.get('objective')}
PRODUCT NAME: {campaign_input.get('product_name')}
PRODUCT SUMMARY: {product_intel.product_summary}
CORE BENEFITS: {product_intel.core_benefits}
RECOMMENDED TONE: {product_intel.recommended_tone}

CAMPAIGN THEME: {strategy.campaign_theme}
MESSAGING PILLARS: {strategy.messaging_pillars}

TOTAL BUDGET: {plan.total_budget} INR
ALLOCATION: {[{'platform': i.platform, 'amount': i.amount} for i in plan.budget_allocation]}

SAMPLE AD CREATIVES:
- Headlines: {creatives.ad_copy_summaries}
- Search Ad Count: {len(creatives.search_ads)}
- Social Ad Count: {len(creatives.social_ads)}

PROGRAMMATIC AUDIT FINDINGS:
{[v.model_dump() for v in programmatic_violations]}

Provide a structured ComplianceAudit:
- is_approved: True ONLY if there are no critical violations and quality is high
- compliance_score: 0 to 100
- violations: list of all detected violations
- strengths: list of observed strengths
- target_agent_for_fix: 'ad_generation', 'planning', 'strategy', or null
"""

    audit = generate_structured_output(
        prompt=prompt,
        schema=ComplianceAudit,
        system_prompt=SYSTEM_PROMPT,
        temperature=0.1
    )

    # Merge programmatic violations into audit if any were missed
    existing_messages = {v.message for v in audit.violations}
    for pv in programmatic_violations:
        if pv.message not in existing_messages:
            audit.violations.append(pv)

    # Override approval if critical programmatic errors exist
    has_critical = any(str(v.severity).lower() in ["critical", "major", "high"] for v in audit.violations)
    if has_critical:
        audit.is_approved = False
        if not audit.target_agent_for_fix:
            if any("budget" in str(v.category).lower() for v in audit.violations):
                audit.target_agent_for_fix = "planning"
            else:
                audit.target_agent_for_fix = "ad_generation"

    return audit
