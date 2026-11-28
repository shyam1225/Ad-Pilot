from typing import Optional
from app.core.llm import generate_structured_output
from app.schemas.agent_schemas import CampaignStrategyDeliverable, CampaignPlan, PlatformPlanItem, KPIEstimate
from app.services.tools import allocate_weighted_budget, estimate_platform_kpis


SYSTEM_PROMPT = """You are the Campaign Planning Agent of AdPilot, an advanced AI advertising platform.
Your responsibility is to turn high-level strategic directives into an actionable media plan,
rigorously allocating the media budget and organizing flight schedules and KPI milestones.

Guidelines:
1. Ground budget allocations in performance marketing reality.
2. Adhere strictly to the computed mathematical budget allocation provided to avoid math errors.
3. Recommend specific ad formats appropriate to each platform (e.g. In-Feed, Reels, Search, Discovery).
4. Organize flighting into logical phases (e.g. Phase 1: Awareness & Warmup, Phase 2: Engagement & Retargeting, Phase 3: Conversion Push).
5. If revision feedback is provided, adjust timelines, formats, or allocations accordingly.
"""


def run_campaign_planning_agent(
    campaign_input: dict,
    strategy: CampaignStrategyDeliverable,
    feedback: Optional[str] = None
) -> CampaignPlan:
    """
    Executes the Campaign Planning Agent, using deterministic budget allocation tools
    and KPI modeling combined with strategic reasoning.
    """
    total_budget = float(campaign_input.get("budget", 0))
    objective = campaign_input.get("objective", "BRAND_AWARENESS")
    
    # Use selected strategy platforms, or fall back to input platforms
    platforms = strategy.recommended_platforms or campaign_input.get("platforms", [])
    if not platforms:
        platforms = ["Instagram", "Google Ads"]

    # Tool invocation for deterministic, benchmark-weighted budget split
    calculated_allocations = allocate_weighted_budget.invoke({
        "total_budget": total_budget,
        "platforms": platforms,
        "objective": objective
    })

    # Tool invocation for benchmark KPI estimations
    kpi_benchmarks = []
    for alloc in calculated_allocations:
        kpi_info = estimate_platform_kpis.invoke({
            "platform": alloc["platform"],
            "budget": alloc["amount"],
            "objective": objective
        })
        kpi_benchmarks.append(kpi_info)

    prompt = f"""
Construct a structured CampaignPlan based on the following specifications and mathematical allocations:

CAMPAIGN DETAILS:
- Total Budget: {total_budget} INR
- Objective: {objective}
- Campaign Theme: {strategy.campaign_theme}
- Messaging Pillars: {', '.join(strategy.messaging_pillars)}

DETERMINISTIC BUDGET SPLIT (MAINTAIN EXACT AMOUNTS AND PERCENTAGES):
{calculated_allocations}

BENCHMARK PERFORMANCE ESTIMATES:
{kpi_benchmarks}
"""

    if feedback:
        prompt += f"""
PREVIOUS AUDIT FEEDBACK (MUST REMEDIATE):
{feedback}
"""

    prompt += """
Generate a complete CampaignPlan output:
1. total_budget: Confirm exact total budget
2. currency: 'INR'
3. budget_allocation: List of PlatformPlanItem with platform, amount, percentage, rationale, and recommended_ad_formats
4. flight_schedule: Phased rollout schedule (e.g. Week 1, Weeks 2-3, Week 4)
5. kpi_estimates: List of KPIEstimate with platform, estimated_impressions, estimated_clicks, and target_metric
"""

    plan = generate_structured_output(
        prompt=prompt,
        schema=CampaignPlan,
        system_prompt=SYSTEM_PROMPT,
        temperature=0.1
    )

    # Deterministic safeguard: ensure the mathematical tool outputs are preserved
    # to guarantee 100% budget conservation
    clean_items = []
    for i, alloc in enumerate(calculated_allocations):
        # find matching item from LLM for rationale and formats, or generate sensible defaults
        matched = next((item for item in plan.budget_allocation if item.platform.lower() == alloc["platform"].lower()), None)
        rationale = matched.rationale if matched else f"Weighted allocation for {objective} on {alloc['platform']}"
        formats = matched.recommended_ad_formats if (matched and matched.recommended_ad_formats) else ["In-Feed Ads", "Story Ads"]
        
        clean_items.append(PlatformPlanItem(
            platform=alloc["platform"],
            amount=alloc["amount"],
            percentage=alloc["percentage"],
            rationale=rationale,
            recommended_ad_formats=formats
        ))

    plan.budget_allocation = clean_items
    plan.total_budget = total_budget

    return plan
