import os
import sys

# Ensure backend root is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base, get_db
from app import models
from app.main import app

# Shared in-memory SQLite engine using StaticPool so all connections share the same memory DB
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
Base.metadata.create_all(bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_health_and_root():
    # Root check
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "online"
    assert data["version"] == "2.0.0"

    # Health check
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "healthy"}
    print("[PASS] Root and /health endpoints verified")


def test_get_campaigns_endpoint():
    resp = client.get("/campaigns")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    print(f"[PASS] GET /campaigns returned 200 with {len(resp.json())} items")


def test_post_campaign_validation_error():
    bad_payload = {
        "product_name": "X",  # Too short (min 2)
        "target_audience": "All",
        "budget": -500,       # Must be > 0
        "objective": "SALES",
        "platforms": []       # min 1
    }
    resp = client.post("/campaigns", json=bad_payload)
    assert resp.status_code == 422
    print("[PASS] Request input validation errors caught with 422")


def test_get_nonexistent_campaign():
    resp = client.get("/campaigns/999999")
    assert resp.status_code == 404
    print("[PASS] Nonexistent campaign ID returns 404")


def test_campaign_db_persistence():
    # Insert a test campaign directly via session
    db = TestingSessionLocal()
    c = models.Campaign(
        product_name="GlowSerum",
        target_audience="Adults",
        budget=50000,
        objective="SALES",
        platforms=["Instagram"],
        strategy={"summary": "Test strategy", "recommended_platforms": ["Instagram"], "budget_allocation": [], "ad_copy": []},
        product_intelligence={"product_summary": "Test summary", "core_benefits": [], "target_personas": [], "value_propositions": [], "positioning_angle": "", "recommended_tone": ""},
        plan={"total_budget": 50000, "currency": "INR", "budget_allocation": [], "flight_schedule": [], "kpi_estimates": []},
        creatives={"search_ads": [], "social_ads": [], "ad_copy_summaries": []},
        compliance={"is_approved": True, "compliance_score": 100, "violations": [], "strengths": []}
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    campaign_id = c.id
    db.close()

    # Query via API
    resp = client.get(f"/campaigns/{campaign_id}")
    assert resp.status_code == 200
    fetched = resp.json()
    assert fetched["product_name"] == "GlowSerum"
    assert fetched["product_intelligence"]["product_summary"] == "Test summary"
    assert fetched["plan"]["total_budget"] == 50000
    print(f"[PASS] Multi-agent campaign successfully persisted and retrieved with id: {campaign_id}")


if __name__ == "__main__":
    test_health_and_root()
    test_get_campaigns_endpoint()
    test_post_campaign_validation_error()
    test_get_nonexistent_campaign()
    test_campaign_db_persistence()
    print("\nALL PHASE 4 VERIFICATION CHECKS PASSED SUCCESSFULLY!")
