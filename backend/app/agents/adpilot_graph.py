from typing import TypedDict, Optional, List
from langgraph.graph import StateGraph, START, END

from app.schemas.campaign import CampaignStrategy, PlatformBudget
from app.schemas.agent_schemas import (
    ProductIntelligence,
    CampaignStrategyDeliverable,
    CampaignPlan,
    AdCreativesDeliverable,
    ComplianceAudit
)
from app.agents.product_intelligence_agent import run_product_intelligence_agent
from app.agents.campaign_strategy_agent import run_campaign_strategy_agent
from app.agents.campaign_planning_agent import run_campaign_planning_agent
from app.agents.ad_generation_agent import run_ad_generation_agent
from app.agents.compliance_agent import run_compliance_agent


class AdPilotState(TypedDict):
    # Initial input specification
    campaign_input: dict
    
    # Five-Agent deliverables
    product_intelligence: Optional[ProductIntelligence]
    strategy: Optional[CampaignStrategyDeliverable]
    plan: Optional[CampaignPlan]
    creatives: Optional[AdCreativesDeliverable]
    compliance: Optional[ComplianceAudit]
    
    # Consolidated legacy format for backward compatibility
    legacy_strategy: Optional[CampaignStrategy]
    
    # Orchestration control and critique history
    retry_count: int
    feedback_history: List[str]
    is_valid: bool
    error: Optional[str]


# -------------------------------------------------------------
# Node Implementations
# -------------------------------------------------------------

def node_product_intelligence(state: AdPilotState) -> dict:
    print("[AdPilot Graph] 1/5 Running Product Intelligence Agent...")
    product_intel = run_product_intelligence_agent(state["campaign_input"])
    return {
        "product_intelligence": product_intel,
        "error": None
    }


def node_campaign_strategy(state: AdPilotState) -> dict:
    print("[AdPilot Graph] 2/5 Running Campaign Strategy Agent...")
    feedback = state["feedback_history"][-1] if state.get("feedback_history") else None
    strategy = run_campaign_strategy_agent(
        campaign_input=state["campaign_input"],
        product_intel=state["product_intelligence"],
        feedback=feedback
    )
    return {
        "strategy": strategy,
        "error": None
    }


def node_campaign_planning(state: AdPilotState) -> dict:
    print("[AdPilot Graph] 3/5 Running Campaign Planning Agent...")
    feedback = state["feedback_history"][-1] if state.get("feedback_history") else None
    plan = run_campaign_planning_agent(
        campaign_input=state["campaign_input"],
        strategy=state["strategy"],
        feedback=feedback
    )
    return {
        "plan": plan,
        "error": None
    }


def node_ad_generation(state: AdPilotState) -> dict:
    print("[AdPilot Graph] 4/5 Running Ad Generation Agent...")
    feedback = state["feedback_history"][-1] if state.get("feedback_history") else None
    creatives = run_ad_generation_agent(
        campaign_input=state["campaign_input"],
        product_intel=state["product_intelligence"],
        strategy=state["strategy"],
        plan=state["plan"],
        feedback=feedback
    )
    return {
        "creatives": creatives,
        "error": None
    }


def node_compliance_audit(state: AdPilotState) -> dict:
    print("[AdPilot Graph] 5/5 Running Quality and Compliance Agent...")
    audit = run_compliance_agent(
        campaign_input=state["campaign_input"],
        product_intel=state["product_intelligence"],
        strategy=state["strategy"],
        plan=state["plan"],
        creatives=state["creatives"]
    )

    history = list(state.get("feedback_history") or [])
    if not audit.is_approved:
        remediation_notes = "; ".join([f"[{v.category.upper()}] {v.remediation_instruction}" for v in audit.violations])
        history.append(remediation_notes)

    current_retries = state.get("retry_count", 0)
    if not audit.is_approved:
        current_retries += 1

    return {
        "compliance": audit,
        "feedback_history": history,
        "retry_count": current_retries
    }


def node_format_deliverables(state: AdPilotState) -> dict:
    """
    Adapter node that reconciles multi-agent deliverables into a backwards-compatible
    CampaignStrategy object for existing frontend/API consumers.
    """
    print("[AdPilot Graph] Finalizing deliverables & legacy adapter mapping...")
    plan = state.get("plan")
    strategy = state.get("strategy")
    creatives = state.get("creatives")
    compliance = state.get("compliance")

    # Map budget allocations
    budget_items = []
    if plan and plan.budget_allocation:
        for item in plan.budget_allocation:
            budget_items.append(
                PlatformBudget(
                    platform=item.platform,
                    amount=item.amount,
                    reason=item.rationale
                )
            )

    # Compile representative ad copy snippets
    ad_copy_list = []
    if creatives:
        ad_copy_list.extend(creatives.ad_copy_summaries)
        for s in creatives.search_ads:
            for h in s.headlines:
                if h not in ad_copy_list:
                    ad_copy_list.append(h)
        for soc in creatives.social_ads:
            formatted = f"[{soc.platform} {soc.format}] {soc.headline or ''}: {soc.primary_text}"
            ad_copy_list.append(formatted)

    summary_text = strategy.summary if strategy else "AI-generated campaign strategy."
    platforms = [item.platform for item in plan.budget_allocation] if plan else (strategy.recommended_platforms if strategy else [])

    legacy_strategy = CampaignStrategy(
        summary=summary_text,
        recommended_platforms=platforms,
        budget_allocation=budget_items,
        ad_copy=ad_copy_list[:6]
    )

    is_valid = True
    error_msg = None

    if compliance:
        if not compliance.is_approved and state.get("retry_count", 0) >= 2:
            is_valid = False
            error_msg = f"Compliance score {compliance.compliance_score}/100: " + "; ".join(
                [v.message for v in compliance.violations[:2]]
            )
        else:
            is_valid = compliance.is_approved

    return {
        "legacy_strategy": legacy_strategy,
        "is_valid": is_valid,
        "error": error_msg
    }


# -------------------------------------------------------------
# Conditional Routing
# -------------------------------------------------------------

def decide_compliance_action(state: AdPilotState) -> str:
    compliance = state.get("compliance")
    retry_count = state.get("retry_count", 0)

    if compliance and compliance.is_approved:
        print("[AdPilot Graph] >> Compliance Approved!")
        return "approved"

    if retry_count >= 2:
        print(f"[AdPilot Graph] >> Maximum retries ({retry_count}) reached. Proceeding to finalize.")
        return "max_retries"

    target = compliance.target_agent_for_fix if compliance else "ad_generation"
    print(f"[AdPilot Graph] >> Revision required (attempt {retry_count}). Routing feedback to {target}...")

    if target == "planning":
        return "retry_planning"
    elif target == "strategy":
        return "retry_strategy"
    else:
        return "retry_ad_generation"


# -------------------------------------------------------------
# Build & Compile Graph
# -------------------------------------------------------------

builder = StateGraph(AdPilotState)

# Add Nodes
builder.add_node("product_intelligence", node_product_intelligence)
builder.add_node("campaign_strategy", node_campaign_strategy)
builder.add_node("campaign_planning", node_campaign_planning)
builder.add_node("ad_generation", node_ad_generation)
builder.add_node("compliance_audit", node_compliance_audit)
builder.add_node("format_deliverables", node_format_deliverables)

# Define Main Sequential Pipeline
builder.add_edge(START, "product_intelligence")
builder.add_edge("product_intelligence", "campaign_strategy")
builder.add_edge("campaign_strategy", "campaign_planning")
builder.add_edge("campaign_planning", "ad_generation")
builder.add_edge("ad_generation", "compliance_audit")

# Conditional Router after Compliance Audit
builder.add_conditional_edges(
    "compliance_audit",
    decide_compliance_action,
    {
        "approved": "format_deliverables",
        "max_retries": "format_deliverables",
        "retry_ad_generation": "ad_generation",
        "retry_planning": "campaign_planning",
        "retry_strategy": "campaign_strategy"
    }
)

builder.add_edge("format_deliverables", END)

adpilot_graph = builder.compile()


def run_adpilot_workflow(campaign_input: dict) -> dict:
    """
    High-level entrypoint function executing the AdPilot multi-agent graph.
    """
    initial_state: AdPilotState = {
        "campaign_input": campaign_input,
        "product_intelligence": None,
        "strategy": None,
        "plan": None,
        "creatives": None,
        "compliance": None,
        "legacy_strategy": None,
        "retry_count": 0,
        "feedback_history": [],
        "is_valid": False,
        "error": None
    }

    return adpilot_graph.invoke(initial_state)
