import os
import sys

# Ensure backend root is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.agents.adpilot_graph import (
    adpilot_graph,
    run_adpilot_workflow,
    AdPilotState,
    decide_compliance_action,
    node_format_deliverables
)
from app.schemas.campaign import CampaignStrategy, PlatformBudget
from app.schemas.agent_schemas import (
    ProductIntelligence,
    CampaignStrategyDeliverable,
    CampaignPlan,
    PlatformPlanItem,
    AdCreativesDeliverable,
    GoogleSearchAd,
    SocialMediaAd,
    ComplianceAudit,
    ComplianceViolation
)


def test_graph_structure():
    # Verify compiled graph nodes
    nodes = adpilot_graph.nodes
    expected_nodes = [
        "product_intelligence",
        "campaign_strategy",
        "campaign_planning",
        "ad_generation",
        "compliance_audit",
        "format_deliverables"
    ]
    for node in expected_nodes:
        assert node in nodes, f"Node {node} missing from compiled graph"
    print("[PASS] Graph topology verified with all 5 agent nodes + format_deliverables node")


def test_conditional_routing_logic():
    # Scenario A: Approved
    approved_audit = ComplianceAudit(
        is_approved=True,
        compliance_score=95.0,
        violations=[],
        strengths=["Flawless execution"]
    )
    state_approved: AdPilotState = {
        "campaign_input": {},
        "product_intelligence": None,
        "strategy": None,
        "plan": None,
        "creatives": None,
        "compliance": approved_audit,
        "legacy_strategy": None,
        "retry_count": 0,
        "feedback_history": [],
        "is_valid": False,
        "error": None
    }
    assert decide_compliance_action(state_approved) == "approved"

    # Scenario B: Rejected -> target planning
    rejected_audit_planning = ComplianceAudit(
        is_approved=False,
        compliance_score=60.0,
        violations=[
            ComplianceViolation(
                category="budget",
                severity="critical",
                message="Budget mismatch",
                remediation_instruction="Rebalance budget"
            )
        ],
        strengths=[],
        target_agent_for_fix="planning"
    )
    state_planning: AdPilotState = {
        "campaign_input": {},
        "product_intelligence": None,
        "strategy": None,
        "plan": None,
        "creatives": None,
        "compliance": rejected_audit_planning,
        "legacy_strategy": None,
        "retry_count": 0,
        "feedback_history": [],
        "is_valid": False,
        "error": None
    }
    assert decide_compliance_action(state_planning) == "retry_planning"

    # Scenario C: Max retries hit
    state_max_retries: AdPilotState = {
        "campaign_input": {},
        "product_intelligence": None,
        "strategy": None,
        "plan": None,
        "creatives": None,
        "compliance": rejected_audit_planning,
        "legacy_strategy": None,
        "retry_count": 2,
        "feedback_history": ["Previous error 1", "Previous error 2"],
        "is_valid": False,
        "error": None
    }
    assert decide_compliance_action(state_max_retries) == "max_retries"
    print("[PASS] Multi-Agent conditional feedback routing logic verified")


def test_format_deliverables_legacy_adapter():
    mock_plan = CampaignPlan(
        total_budget=150000.0,
        currency="INR",
        budget_allocation=[
            PlatformPlanItem(
                platform="Instagram",
                amount=90000.0,
                percentage=60.0,
                rationale="Visual focus",
                recommended_ad_formats=["Reels"]
            ),
            PlatformPlanItem(
                platform="Google Ads",
                amount=60000.0,
                percentage=40.0,
                rationale="High-intent search",
                recommended_ad_formats=["Search Ads"]
            )
        ],
        flight_schedule=["Launch"],
        kpi_estimates=[]
    )
    mock_creatives = AdCreativesDeliverable(
        search_ads=[
            GoogleSearchAd(
                headlines=["Buy Now", "Best Quality"],
                descriptions=["Ultra fast delivery nationwide."]
            )
        ],
        social_ads=[
            SocialMediaAd(
                platform="Instagram",
                format="Reels",
                primary_text="Transform your routine.",
                headline="Special Launch",
                call_to_action="Shop Now",
                visual_brief="Clean product reveal"
            )
        ],
        ad_copy_summaries=["Transform your routine.", "Special Launch."]
    )
    mock_compliance = ComplianceAudit(
        is_approved=True,
        compliance_score=92.0,
        violations=[],
        strengths=["Great copy"]
    )

    state: AdPilotState = {
        "campaign_input": {},
        "product_intelligence": None,
        "strategy": None,
        "plan": mock_plan,
        "creatives": mock_creatives,
        "compliance": mock_compliance,
        "legacy_strategy": None,
        "retry_count": 0,
        "feedback_history": [],
        "is_valid": False,
        "error": None
    }

    formatted = node_format_deliverables(state)
    assert isinstance(formatted["legacy_strategy"], CampaignStrategy)
    assert len(formatted["legacy_strategy"].budget_allocation) == 2
    assert formatted["legacy_strategy"].budget_allocation[0].platform == "Instagram"
    assert formatted["is_valid"] is True
    print("[PASS] Deliverables adapter maps multi-agent state to legacy CampaignStrategy seamlessly")


def test_live_adpilot_workflow():
    campaign_input = {
        "product_name": "HydroGlow Serum",
        "target_audience": "Women and skincare enthusiasts aged 20-38 in urban India",
        "budget": 150000.0,
        "objective": "SALES",
        "platforms": ["Instagram", "Google Ads"],
        "product_description": "Hyaluronic acid and niacinamide facial serum delivering 72-hour deep skin hydration.",
        "brand_tone": "Clean, radiant, dermatologically trusted",
        "price_point": "₹899"
    }

    print("\n--- Executing Full adpilot_graph Workflow ---")
    result = run_adpilot_workflow(campaign_input)

    assert result["product_intelligence"] is not None
    assert result["strategy"] is not None
    assert result["plan"] is not None
    assert result["creatives"] is not None
    assert result["compliance"] is not None
    assert isinstance(result["legacy_strategy"], CampaignStrategy)

    print("\nWorkflow Execution Output Summary:")
    print(f"Product Intelligence USPs: {result['product_intelligence'].value_propositions}")
    print(f"Strategy Theme: {result['strategy'].campaign_theme}")
    print(f"Media Plan Total: ₹{result['plan'].total_budget:,.2f}")
    print(f"Search Ads: {len(result['creatives'].search_ads)} | Social Ads: {len(result['creatives'].social_ads)}")
    print(f"Compliance Approval: {result['compliance'].is_approved} (Score: {result['compliance'].compliance_score}/100)")
    print(f"Legacy Strategy Summary: {result['legacy_strategy'].summary[:80]}...")
    print(f"Legacy Budget Items Count: {len(result['legacy_strategy'].budget_allocation)}")


if __name__ == "__main__":
    test_graph_structure()
    test_conditional_routing_logic()
    test_format_deliverables_legacy_adapter()
    test_live_adpilot_workflow()
    print("\nALL PHASE 3 VERIFICATION CHECKS PASSED SUCCESSFULLY!")
