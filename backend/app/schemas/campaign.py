
from pydantic import BaseModel


class CampaignRequest(BaseModel):
    product_name: str
    target_audience: str
    budget: float
    objective: str
    platforms: list[str]
