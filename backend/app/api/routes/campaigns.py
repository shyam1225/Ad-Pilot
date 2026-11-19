
from fastapi import APIRouter
from app.schemas.campaign import CampaignRequest, CampaignResponse
from app.services.campaign_service import create_campaign

router = APIRouter()


@router.post("/campaigns", response_model=CampaignResponse)
def create_campaign_route(campaign: CampaignRequest):
    return create_campaign(campaign.model_dump())
