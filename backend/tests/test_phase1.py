import os
import sys

# Ensure backend root is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.schemas.campaign import (
    CampaignRequest,
    CampaignResponse,
    CampaignStrategy,
    PlatformBudget
)
from app.schemas.agent_schemas import (
    ProductIntelligence,
    CustomerPersona,
    CampaignStrategyDeliverable,
    FunnelStageStrategy,
    CampaignPlan,
    PlatformPlanItem,
    KPIEstimate,
    AdCreativesDeliverable,
    GoogleSearchAd,
    SocialMediaAd,
    ComplianceAudit,
    ComplianceViolation
)
from app.models import Campaign
from app.core.llm import get_api_key, get_openai_client, get_chat_llm, DEFAULT_MODEL
from app.services.tools import calculate_budget, recommend_platforms
from app.services.validation_service import (
    validate_budget_allocation,
    validate_recommended_platforms,
    validate_duplicate_platforms
)
from app.services.campaign_graph import campaign_graph


def test_legacy_campaign_schemas():
    req = CampaignRequest(
        product_name="AirFlow Sneakers",
        target_audience="Marathon runners aged 20-40",
        budget=100000.0,
        objective="SALES",
        platforms=["Instagram", "Google Ads"]
    )
    assert req.product_name == "AirFlow Sneakers"
    assert req.product_description is None

    # Test enhanced fields
    req_enhanced = CampaignRequest(
        product_name="AirFlow Sneakers",
        target_audience="Marathon runners aged 20-40",
        budget=100000.0,
        objective="SALES",
        platforms=["Instagram", "Google Ads"],
        product_description="Ultra-light running shoes with carbon-fiber plate",
        brand_tone="Athletic, inspiring, authoritative",
        target_locations=["Mumbai", "Bengaluru", "Delhi"]
    )
    assert req_enhanced.brand_tone == "Athletic, inspiring, authoritative"
    assert len(req_enhanced.target_locations) == 3

    strategy = CampaignStrategy(
        summary="High-performance launch campaign",
        recommended_platforms=["Instagram", "Google Ads"],
        budget_allocation=[
            PlatformBudget(platform="Instagram", amount=60000.0, reason="Visual storytelling"),
            PlatformBudget(platform="Google Ads", amount=40000.0, reason="High-intent search")
        ],
        ad_copy=["Engineered for endurance.", "Feel the carbon snap with every stride."]
    )

    resp = CampaignResponse(
        message="Campaign created successfully",
        campaign_details=req,
        strategy=strategy
    )
    assert resp.strategy.budget_allocation[0].amount == 60000.0
    print("[PASS] Legacy & Extended Campaign Schemas Validated")


def test_agent_schemas():
    # 1. Product Intelligence
    persona = CustomerPersona(
        name="Competitive Marathoner",
        demographics="25-38, tech professional, high disposable income",
        pain_points=["Foot fatigue over 30km", "Heavy shoes causing shin splints"],
        desires_and_motivations=["Break personal marathon record", "Premium durability"]
    )
    prod_intel = ProductIntelligence(
        product_summary="Carbon-plate ultra running shoe for marathoners",
        core_benefits=["Energy return", "Featherweight cushion", "Breathable mesh"],
        target_personas=[persona],
        value_propositions=["Lightest carbon shoe in category"],
        positioning_angle="Elite athletic performance for everyday marathoners",
        recommended_tone="Bold, motivating, precision-focused"
    )
    assert len(prod_intel.target_personas) == 1

    # 2. Campaign Strategy
    funnel = FunnelStageStrategy(
        stage="TOFU",
        objective="Drive massive video views of elite marathoners testing shoes",
        key_messaging="Break your limits, not your stride",
        recommended_channels=["Instagram", "YouTube"]
    )
    strat = CampaignStrategyDeliverable(
        campaign_theme="Defy Gravity",
        positioning_statement="The marathon shoe built to shave minutes off your PB",
        messaging_pillars=["Carbon Snap Propulsion", "Zero Fatigue Cushioning", "Breathable Aerodynamics"],
        target_audience_summary="Dedicated runners training for 10k to marathon distance",
        recommended_platforms=["Instagram", "Google Ads"],
        funnel_stages=[funnel],
        summary="Omni-channel blitz targeting runners during marathon training season"
    )
    assert strat.funnel_stages[0].stage == "TOFU"

    # 3. Campaign Planning
    plan_item = PlatformPlanItem(
        platform="Instagram",
        amount=60000.0,
        percentage=60.0,
        rationale="Top visual platform for sportswear",
        recommended_ad_formats=["Reels", "Story Ads"]
    )
    kpi = KPIEstimate(
        platform="Instagram",
        estimated_impressions="250k - 400k",
        estimated_clicks="8k - 12k",
        target_metric="CTR > 2.5%"
    )
    plan = CampaignPlan(
        total_budget=100000.0,
        currency="INR",
        budget_allocation=[plan_item],
        flight_schedule=["Week 1 Teaser", "Weeks 2-3 Launch Blitz", "Week 4 Retargeting"],
        kpi_estimates=[kpi]
    )
    assert plan.total_budget == 100000.0

    # 4. Ad Generation
    search_ad = GoogleSearchAd(
        headlines=["AirFlow Carbon Shoe", "Break Your Marathon PB", "Ultra-Light Carbon Plate"],
        descriptions=["Engineered with carbon snap technology for maximum propulsion. Order online today.",
                      "Experience zero foot fatigue over 42km. Free express delivery across India."]
    )
    social_ad = SocialMediaAd(
        platform="Instagram",
        format="Reels",
        primary_text="Every second counts. Shave minutes off your personal best with AirFlow.",
        headline="Run Faster. Recover Sooner.",
        call_to_action="Shop Now",
        visual_brief="Cinematic slow-motion shot of a runner's foot striking the pavement in the morning mist."
    )
    creatives = AdCreativesDeliverable(
        search_ads=[search_ad],
        social_ads=[social_ad],
        ad_copy_summaries=["Run Faster. Recover Sooner.", "Break your marathon PB with AirFlow."]
    )
    assert len(creatives.search_ads) == 1
    assert len(creatives.social_ads) == 1

    # 5. Quality & Compliance
    violation = ComplianceViolation(
        category="character_limit",
        severity="low",
        message="Headline 1 is 31 characters, limit is 30",
        remediation_instruction="Trim 1 character from Headline 1"
    )
    audit = ComplianceAudit(
        is_approved=True,
        compliance_score=94.5,
        violations=[violation],
        strengths=["Clear value propositions", "Valid budget math", "No prohibited claims"],
        target_agent_for_fix=None
    )
    assert audit.is_approved is True
    print("[PASS] Five-Agent Pydantic Schemas Validated")


def test_orm_model_columns():
    column_names = {c.name for c in Campaign.__table__.columns}
    required_cols = {
        "id", "product_name", "target_audience", "budget", "objective",
        "platforms", "strategy", "product_intelligence", "plan",
        "creatives", "compliance", "created_at"
    }
    missing = required_cols - column_names
    assert not missing, f"Missing columns in Campaign model: {missing}"
    print("[PASS] SQLAlchemy Campaign Model Schema Validated")


def test_core_llm_setup():
    key = get_api_key()
    assert len(key) > 10, "OpenRouter API Key present and configured"
    client = get_openai_client()
    assert client is not None
    chat_llm = get_chat_llm(temperature=0.0)
    assert chat_llm is not None
    print(f"[PASS] Core LLM Setup Configured (Default Model: {DEFAULT_MODEL})")


def test_existing_tools_and_validation():
    # Tools
    budget_res = calculate_budget.invoke({"total_budget": 50000.0, "platforms": ["Instagram", "Facebook"]})
    assert budget_res == {"Instagram": 25000.0, "Facebook": 25000.0}

    platforms = recommend_platforms.invoke({"objective": "brand awareness"})
    assert "Instagram" in platforms

    # Validation
    strategy = CampaignStrategy(
        summary="Test",
        recommended_platforms=["Instagram", "Facebook"],
        budget_allocation=[
            PlatformBudget(platform="Instagram", amount=25000.0, reason="reach"),
            PlatformBudget(platform="Facebook", amount=25000.0, reason="scale")
        ],
        ad_copy=["Ad 1"]
    )
    validate_budget_allocation(strategy, 50000.0)
    validate_recommended_platforms(strategy, ["Instagram", "Facebook", "YouTube"])
    validate_duplicate_platforms(strategy)

    # Existing Graph compilation
    assert campaign_graph is not None
    print("[PASS] Existing Tools, Validation & Graph Workflow Confirmed Operational")


if __name__ == "__main__":
    test_legacy_campaign_schemas()
    test_agent_schemas()
    test_orm_model_columns()
    test_core_llm_setup()
    test_existing_tools_and_validation()
    print("\nALL PHASE 1 VERIFICATION CHECKS PASSED SUCCESSFULLY!")
