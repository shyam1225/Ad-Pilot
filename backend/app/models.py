from sqlalchemy import Column, Integer, String, Numeric, DateTime, JSON, func
from app.database import Base


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String(100), nullable=False)
    target_audience = Column(String(255), nullable=False)
    budget = Column(Numeric(12, 2), nullable=False)
    objective = Column(String(50), nullable=False)
    platforms = Column(JSON, nullable=False)
    strategy = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())