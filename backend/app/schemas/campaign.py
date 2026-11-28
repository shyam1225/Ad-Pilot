from typing import Optional
from pydantic import BaseModel, Field


class CampaignRequest(BaseModel):
    product_name: str = Field(
        min_length=2,
        max_length=100,
        description="Name of the product or service"
    )

    target_audience: str = Field(
        min_length=3,
        max_length=200,
        description="Primary target demographic or audience description"
    )

    budget: float = Field(
        gt=0,
        description="Campaign budget must be greater than zero"
    )

    objective: str = Field(
        min_length=3,
        description="Core campaign objective (e.g. BRAND_AWARENESS, LEAD_GENERATION, SALES, WEBSITE_TRAFFIC)"
    )

    platforms: list[str] = Field(
        min_length=1,
        description="List of selected advertising platforms"
    )

    # Optional enhanced fields for the five-agent system (backward compatible)
    product_description: Optional[str] = Field(
        default=None,
        description="Detailed description, key features or landing page info"
    )

    brand_tone: Optional[str] = Field(
        default=None,
        description="Desired tone of voice (e.g. Professional, Energetic, Casual, Sophisticated)"
    )

    target_locations: Optional[list[str]] = Field(
        default=None,
        description="Geographic targeting locations"
    )

    price_point: Optional[str] = Field(
        default=None,
        description="Pricing tier, price range, or special offering context"
    )


class PlatformBudget(BaseModel):
    platform: str
    amount: float
    reason: str


class CampaignStrategy(BaseModel):
    summary: str
    recommended_platforms: list[str]
    budget_allocation: list[PlatformBudget]
    ad_copy: list[str]


class CampaignResponse(BaseModel):
    message: str
    campaign_details: CampaignRequest
    strategy: CampaignStrategy
    # Optional multi-agent deliverable extensions
    product_intelligence: Optional[dict] = None
    plan: Optional[dict] = None
    creatives: Optional[dict] = None
    compliance: Optional[dict] = None
