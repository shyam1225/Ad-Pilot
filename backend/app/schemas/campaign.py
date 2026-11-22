from pydantic import BaseModel, Field


class CampaignRequest(BaseModel):

    product_name: str = Field(
        min_length=2,
        max_length=100
    )

    target_audience: str = Field(
        min_length=3,
        max_length=200
    )

    budget: float = Field(
        gt=0,
        description="Campaign budget must be greater than zero"
    )

    objective: str = Field(
        min_length=3
    )

    platforms: list[str] = Field(
        min_length=1
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

class PlatformBudget(BaseModel):
    platform: str
    amount: float
    reason: str

class CampaignResponse(BaseModel):
    message: str
    campaign_details: CampaignRequest
    strategy: CampaignStrategy


class CampaignStrategy(BaseModel):
    summary: str
    recommended_platforms: list[str]
    budget_allocation: list[PlatformBudget]
    ad_copy: list[str]