import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database import get_db
from app.models import Campaign
from app.schemas.campaign import CampaignRequest, CampaignResponse
from app.agents.adpilot_graph import run_adpilot_workflow
from app.services.campaign_graph import campaign_graph

logger = logging.getLogger("adpilot.api")
router = APIRouter()


@router.post("/campaigns", response_model=CampaignResponse)
def create_campaign_route(
    campaign: CampaignRequest,
    mode: Optional[str] = "multi_agent",
    db: Session = Depends(get_db)
):
    """
    Creates an AI-driven advertising campaign.
    By default runs the five-agent system (Product Intelligence, Strategy, Planning, Ad Generation, Compliance).
    Supports fallback mode='fast' for single-graph generation.
    """
    logger.info(f"Received campaign request for: {campaign.product_name} (mode: {mode})")

    if mode == "fast":
        # Legacy fast-path fallback
        initial_state = {
            "campaign": campaign.model_dump(),
            "strategy": None,
            "retry_count": 0,
            "is_valid": False,
            "error": None
        }
        result = campaign_graph.invoke(initial_state)
        if not result.get("is_valid", False):
            raise HTTPException(
                status_code=422,
                detail=result.get("error") or "Campaign validation failed."
            )
        legacy_strategy = result["strategy"]
        prod_intel_dict = None
        plan_dict = None
        creatives_dict = None
        compliance_dict = None
    else:
        # Five-Agent Orchestration Pipeline
        result = run_adpilot_workflow(campaign.model_dump())
        legacy_strategy = result.get("legacy_strategy")

        prod_intel_dict = (
            result["product_intelligence"].model_dump()
            if result.get("product_intelligence") else None
        )
        plan_dict = (
            result["plan"].model_dump()
            if result.get("plan") else None
        )
        creatives_dict = (
            result["creatives"].model_dump()
            if result.get("creatives") else None
        )
        compliance_dict = (
            result["compliance"].model_dump()
            if result.get("compliance") else None
        )

    # Persist to database if available
    try:
        db_campaign = Campaign(
            product_name=campaign.product_name,
            target_audience=campaign.target_audience,
            budget=campaign.budget,
            objective=campaign.objective,
            platforms=campaign.platforms,
            strategy=legacy_strategy.model_dump() if legacy_strategy else None,
            product_intelligence=prod_intel_dict,
            plan=plan_dict,
            creatives=creatives_dict,
            compliance=compliance_dict
        )
        db.add(db_campaign)
        db.commit()
        db.refresh(db_campaign)
        logger.info(f"Campaign saved to database with id: {db_campaign.id}")
    except SQLAlchemyError as db_err:
        logger.warning(f"Database persistence skipped (DB offline or unreachable): {db_err}")
        db.rollback()

    return {
        "message": "Campaign created successfully",
        "campaign_details": campaign,
        "strategy": legacy_strategy,
        "product_intelligence": prod_intel_dict,
        "plan": plan_dict,
        "creatives": creatives_dict,
        "compliance": compliance_dict
    }


@router.get("/campaigns")
def get_campaigns(db: Session = Depends(get_db)):
    """
    Returns recent campaigns ordered by creation date descending.
    """
    try:
        campaigns = db.query(Campaign).order_by(Campaign.created_at.desc()).all()
        return campaigns
    except SQLAlchemyError as db_err:
        logger.warning(f"Failed to query database: {db_err}")
        return []


@router.get("/campaigns/{campaign_id}")
def get_campaign_by_id(campaign_id: int, db: Session = Depends(get_db)):
    """
    Returns details of a single campaign by ID.
    """
    try:
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    except SQLAlchemyError as db_err:
        logger.warning(f"Failed to query database: {db_err}")
        raise HTTPException(
            status_code=503,
            detail="Database service temporarily unavailable."
        )

    if campaign is None:
        raise HTTPException(
            status_code=404,
            detail="Campaign not found"
        )

    return campaign


from pydantic import BaseModel


class ImageGenerationRequest(BaseModel):
    prompt: str
    headline: Optional[str] = None
    product_name: Optional[str] = None
    cta: Optional[str] = "Shop Now"
    platform: Optional[str] = "Instagram"


from app.services.image_service import generate_visual_ad


@router.post("/campaigns/generate-image")
def generate_image_route(req: ImageGenerationRequest):
    """
    On-demand visual ad image generation using free AI diffusion model with vector banner fallback.
    """
    logger.info(f"Generating ad creative visual for {req.product_name or 'ad'} on {req.platform}...")
    result = generate_visual_ad(
        prompt=req.prompt,
        headline=req.headline or "",
        product_name=req.product_name or "",
        cta=req.cta or "Shop Now",
        platform=req.platform or "Instagram"
    )
    return result

