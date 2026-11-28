import os
import sys

# Ensure backend root is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.tools import (
    calculate_budget,
    recommend_platforms,
    allocate_weighted_budget,
    validate_ad_character_limits,
    check_advertising_compliance_rules,
    estimate_platform_kpis
)
from app.agents import (
    run_product_intelligence_agent,
    run_campaign_strategy_agent,
    run_campaign_planning_agent,
    run_ad_generation_agent,
    run_compliance_agent
)
from app.schemas.agent_schemas import (
    ProductIntelligence,
    CampaignStrategyDeliverable,
    CampaignPlan,
    AdCreativesDeliverable,
    ComplianceAudit
)


def test_enhanced_domain_tools():
    # 1. Test weighted budget allocation
    total_budget = 350000.0
    platforms = ["Google Ads", "Instagram", "YouTube"]
    alloc = allocate_weighted_budget.invoke({
        "total_budget": total_budget,
        "platforms": platforms,
        "objective": "SALES"
    })
    total_allocated = sum(item["amount"] for item in alloc)
    assert abs(total_allocated - total_budget) < 0.01, f"Budget mismatch: {total_allocated} != {total_budget}"
    # In SALES, Google Ads should get highest share
    google_item = next(i for i in alloc if i["platform"] == "Google Ads")
    youtube_item = next(i for i in alloc if i["platform"] == "YouTube")
    assert google_item["amount"] > youtube_item["amount"], "Google Ads should be weighted higher than YouTube for SALES"
    print("[PASS] Weighted budget allocation tool verified with 100% budget conservation")

    # 2. Test character limits validator
    valid_check = validate_ad_character_limits.invoke({
        "headlines": ["Buy Smart Watch", "Best Fitness Tracker"],
        "descriptions": ["Track your workouts with high precision GPS. Free express delivery in India."],
        "platform": "Google Ads"
    })
    assert valid_check["is_valid"] is True

    invalid_check = validate_ad_character_limits.invoke({
        "headlines": ["This headline is way too long and definitely exceeds 30 characters"],
        "descriptions": ["Short description"],
        "platform": "Google Ads"
    })
    assert invalid_check["is_valid"] is False
    assert len(invalid_check["violations"]) == 1
    print("[PASS] Google Ads character limit validator tool verified")

    # 3. Test compliance rules
    banned_test = check_advertising_compliance_rules.invoke({
        "text_corpus": [
            "Experience unmatched comfort.",
            "This is 100% guaranteed to double your money in 2 days!",
            "Our miracle cure fixes everything."
        ]
    })
    assert len(banned_test) == 2, f"Expected 2 violations, got {len(banned_test)}"
    print("[PASS] Advertising compliance policy scanner tool verified")

    # 4. Test KPI estimator
    kpis = estimate_platform_kpis.invoke({
        "platform": "Instagram",
        "budget": 100000.0,
        "objective": "BRAND_AWARENESS"
    })
    assert "estimated_impressions" in kpis
    assert "estimated_clicks" in kpis
    print("[PASS] Platform KPI estimator tool verified")


def test_five_agents_pipeline():
    campaign_input = {
        "product_name": "ZenPulse Noise-Cancelling Headphones",
        "target_audience": "Urban professionals and remote workers aged 24-45 in India",
        "budget": 250000.0,
        "objective": "SALES",
        "platforms": ["Instagram", "Google Ads", "YouTube"],
        "product_description": "Wireless over-ear headphones with 45dB hybrid ANC, 40-hour battery life, and spatial audio.",
        "brand_tone": "Sophisticated, calming, and premium",
        "price_point": "12,999 INR"
    }

    print("\n--- Running 1. Product Intelligence Agent ---")
    product_intel = run_product_intelligence_agent(campaign_input)
    assert isinstance(product_intel, ProductIntelligence)
    assert len(product_intel.core_benefits) > 0
    assert len(product_intel.target_personas) > 0
    print(f"Product Summary: {product_intel.product_summary[:90]}...")
    print(f"Personas generated: {[p.name for p in product_intel.target_personas]}")

    print("\n--- Running 2. Campaign Strategy Agent ---")
    strategy = run_campaign_strategy_agent(campaign_input, product_intel)
    assert isinstance(strategy, CampaignStrategyDeliverable)
    assert len(strategy.messaging_pillars) > 0
    assert len(strategy.funnel_stages) > 0
    print(f"Campaign Theme: {strategy.campaign_theme}")
    print(f"Messaging Pillars: {strategy.messaging_pillars}")

    print("\n--- Running 3. Campaign Planning Agent ---")
    plan = run_campaign_planning_agent(campaign_input, strategy)
    assert isinstance(plan, CampaignPlan)
    assert abs(sum(i.amount for i in plan.budget_allocation) - campaign_input["budget"]) < 0.5
    print(f"Total Budget Planned: {plan.total_budget} {plan.currency}")
    for item in plan.budget_allocation:
        print(f" - {item.platform}: ₹{item.amount:,.2f} ({item.percentage}%)")

    print("\n--- Running 4. Ad Generation Agent ---")
    creatives = run_ad_generation_agent(campaign_input, product_intel, strategy, plan)
    assert isinstance(creatives, AdCreativesDeliverable)
    print(f"Search Ads Count: {len(creatives.search_ads)}")
    print(f"Social Ads Count: {len(creatives.social_ads)}")
    for sa in creatives.search_ads:
        for h in sa.headlines:
            assert len(h) <= 30, f"Headline '{h}' exceeds 30 chars"
    print("Google Search Headlines verified <= 30 chars")

    print("\n--- Running 5. Quality & Compliance Agent ---")
    audit = run_compliance_agent(campaign_input, product_intel, strategy, plan, creatives)
    assert isinstance(audit, ComplianceAudit)
    print(f"Audit Status: Approved={audit.is_approved}, Score={audit.compliance_score}/100")
    print(f"Violations Detected: {len(audit.violations)}")
    print(f"Strengths: {audit.strengths}")


if __name__ == "__main__":
    test_enhanced_domain_tools()
    test_five_agents_pipeline()
    print("\nALL PHASE 2 VERIFICATION CHECKS PASSED SUCCESSFULLY!")
