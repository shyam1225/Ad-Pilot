
from fastapi import APIRouter
from app.schemas.campaign import CampaignRequest, CampaignResponse
from app.services.campaign_graph import campaign_graph
from fastapi import APIRouter, HTTPException
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Campaign
router = APIRouter()

@router.post("/campaigns", response_model=CampaignResponse)
def create_campaign_route(
    campaign: CampaignRequest,
    db: Session = Depends(get_db)):

    initial_state = {
        "campaign": campaign.model_dump(),
        "strategy": None,
        "retry_count": 0,
        "is_valid": False,
        "error": None
    }

    result = campaign_graph.invoke(initial_state)

    if not result["is_valid"]:
        raise HTTPException(
            status_code=422,
            detail=result["error"] or "Campaign validation failed."
        )
    
    db_campaign = Campaign(
        product_name=campaign.product_name,
        target_audience=campaign.target_audience,
        budget=campaign.budget,
        objective=campaign.objective,
        platforms=campaign.platforms,
        strategy=result["strategy"].model_dump()
    )

    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    return {
        "message": "Campaign created successfully",
        "campaign_details": campaign,
        "strategy": result["strategy"]
    }
@router.get("/campaigns")
def get_campaigns(db: Session = Depends(get_db)):
    campaigns = db.query(Campaign).order_by(
        Campaign.created_at.desc()
    ).all()

    return campaigns
@router.get("/campaigns/{campaign_id}")
def get_campaign_by_id(
    campaign_id: int,
    db: Session = Depends(get_db)
):
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id
    ).first()

    if campaign is None:
        raise HTTPException(
            status_code=404,
            detail="Campaign not found"
        )

    return campaign

