from typing import Optional, Literal, Union, Any
from pydantic import BaseModel, Field, field_validator


# -------------------------------------------------------------
# 1. Product Intelligence Agent Schemas
# -------------------------------------------------------------

class CustomerPersona(BaseModel):
    name: str = Field(description="Archetype name, e.g. 'Tech-Savvy Early Adopter'")
    demographics: str = Field(description="Age, profession, lifestyle, income bracket")
    pain_points: list[str] = Field(description="Key frustrations or unsolved needs")
    desires_and_motivations: list[str] = Field(description="Aspirations and emotional drivers")


class ProductIntelligence(BaseModel):
    product_summary: str = Field(description="Executive breakdown of the product and value proposition")
    core_benefits: list[str] = Field(description="Primary user-centric benefits")
    target_personas: list[CustomerPersona] = Field(description="Identified target audience archetypes")
    value_propositions: list[str] = Field(description="Key differentiators and Unique Selling Points (USPs)")
    positioning_angle: str = Field(description="Strategic positioning statement in the market")
    recommended_tone: str = Field(description="Optimal brand tone of voice for the campaign")


# -------------------------------------------------------------
# 2. Campaign Strategy Agent Schemas
# -------------------------------------------------------------

class FunnelStageStrategy(BaseModel):
    stage: str = Field(
        default="TOFU",
        description="Funnel stage indicator, e.g. 'TOFU', 'MOFU', 'BOFU', 'Awareness', or 'Conversion'"
    )
    objective: str = Field(description="Goal for this specific funnel stage")
    key_messaging: str = Field(description="Core hook or narrative angle")
    recommended_channels: list[str] = Field(description="Platforms most suited for this stage")


class CampaignStrategyDeliverable(BaseModel):
    campaign_theme: str = Field(description="Creative thematic concept or overarching 'Big Idea'")
    positioning_statement: str = Field(description="How the campaign positions the product against alternatives")
    messaging_pillars: list[str] = Field(description="3-4 core pillars that guide all creative assets")
    target_audience_summary: str = Field(description="Targeting guidelines aligned with product intelligence")
    recommended_platforms: list[str] = Field(description="Final strategic platforms prioritized from user selection")
    funnel_stages: list[FunnelStageStrategy] = Field(description="Stage-by-stage funnel progression")
    summary: str = Field(description="Strategic summary integrating all elements")


# -------------------------------------------------------------
# 3. Campaign Planning Agent Schemas
# -------------------------------------------------------------

class PlatformPlanItem(BaseModel):
    platform: str = Field(description="Advertising platform name")
    amount: float = Field(description="Allocated spend amount in campaign currency")
    percentage: float = Field(description="Percentage share of total campaign budget (0-100)")
    rationale: str = Field(description="Data-driven reason for this budget allocation")
    recommended_ad_formats: list[str] = Field(
        description="Ad formats to utilize (e.g. Stories, Carousel, Search Ads, In-Feed)"
    )


class KPIEstimate(BaseModel):
    platform: str = Field(description="Platform name")
    estimated_impressions: Optional[str] = Field(default=None, description="Projected impression range")
    estimated_clicks: Optional[str] = Field(default=None, description="Projected click volume")
    target_metric: Optional[str] = Field(default=None, description="Primary success benchmark (e.g. CTR, CPC, ROAS)")


class CampaignPlan(BaseModel):
    total_budget: float = Field(description="Total campaign budget confirmed")
    currency: str = Field(default="INR", description="Campaign currency")
    budget_allocation: list[PlatformPlanItem] = Field(description="Platform breakdown of spend")
    flight_schedule: list[str] = Field(
        default_factory=list,
        description="Phased execution timeline (e.g. Phase 1 Warmup, Phase 2 Scaling)"
    )
    kpi_estimates: list[KPIEstimate] = Field(
        default_factory=list,
        description="Projected performance KPIs"
    )

    @field_validator("flight_schedule", mode="before")
    @classmethod
    def normalize_flight_schedule(cls, v: Any) -> list[str]:
        if not isinstance(v, list):
            return [str(v)] if v else []
        normalized = []
        for item in v:
            if isinstance(item, dict):
                phase_title = item.get("phase") or item.get("name") or item.get("title") or "Phase"
                details = [f"{k}: {val}" for k, val in item.items() if k not in ["phase", "name", "title"]]
                if details:
                    normalized.append(f"{phase_title} ({', '.join(details)})")
                else:
                    normalized.append(str(phase_title))
            else:
                normalized.append(str(item))
        return normalized


# -------------------------------------------------------------
# 4. Ad Generation Agent Schemas
# -------------------------------------------------------------

class GoogleSearchAd(BaseModel):
    headlines: list[str] = Field(
        description="3 to 5 headlines, each strictly 30 characters or fewer"
    )
    descriptions: list[str] = Field(
        description="2 to 4 descriptions, each strictly 90 characters or fewer"
    )
    path_1: Optional[str] = Field(default=None, description="Display URL path 1 (max 15 chars)")
    path_2: Optional[str] = Field(default=None, description="Display URL path 2 (max 15 chars)")


class SocialMediaAd(BaseModel):
    platform: str = Field(description="Target platform, e.g. Instagram, Facebook, LinkedIn, YouTube")
    format: str = Field(description="Ad unit format (e.g. Feed Post, Reel, Story, Sponsored Update)")
    primary_text: str = Field(description="Compelling post body copy")
    headline: Optional[str] = Field(default=None, description="Catchy card headline")
    call_to_action: str = Field(description="CTA label, e.g. 'Learn More', 'Shop Now', 'Get Started'")
    visual_brief: str = Field(description="Description of image/video creative concept, scene, and text overlays")
    image_url: Optional[str] = Field(default=None, description="URL of generated sample visual ad")
    image_prompt: Optional[str] = Field(default=None, description="Detailed prompt used for AI image generation")
    image_provider: Optional[str] = Field(default=None, description="Model or generator provider name")


class AdCreativesDeliverable(BaseModel):
    search_ads: list[GoogleSearchAd] = Field(default_factory=list, description="Search ad variations")
    social_ads: list[SocialMediaAd] = Field(default_factory=list, description="Social media creative variations")
    ad_copy_summaries: list[str] = Field(
        default_factory=list,
        description="Flat list of top punchy slogans/hooks for quick preview or legacy compatibility"
    )


# -------------------------------------------------------------
# 5. Quality and Compliance Agent Schemas
# -------------------------------------------------------------

class ComplianceViolation(BaseModel):
    category: str = Field(
        default="policy",
        description="Category of the detected issue (e.g. 'budget', 'policy', 'character_limit', 'brand_voice', 'hallucination')"
    )
    severity: str = Field(
        default="medium",
        description="Severity impact of the violation: 'low', 'medium', or 'critical'"
    )
    message: str = Field(description="Clear explanation of the rule failure")
    remediation_instruction: str = Field(description="Specific actionable directive on how to fix this violation")


class ComplianceAudit(BaseModel):
    is_approved: bool = Field(description="Whether the entire campaign bundle passes quality checks")
    compliance_score: float = Field(ge=0.0, le=100.0, description="Overall compliance and quality score from 0 to 100")
    violations: list[ComplianceViolation] = Field(default_factory=list, description="List of detected violations")
    strengths: list[str] = Field(default_factory=list, description="Positive aspects observed in the campaign bundle")
    target_agent_for_fix: Optional[str] = Field(
        default=None,
        description="If rejected, specifies which agent must revise its output ('ad_generation', 'planning', 'strategy')"
    )
