import os
import sys
from pathlib import Path

# Ensure backend root is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.image_service import (
    build_ad_image_prompt,
    generate_svg_banner,
    generate_visual_ad,
    STATIC_DIR
)
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_build_ad_image_prompt():
    prompt = build_ad_image_prompt(
        product_name="ZenPulse Headphones",
        brand_tone="Sophisticated",
        visual_brief="Cinematic shot on a dark mahogany desk",
        platform="Instagram"
    )
    assert "ZenPulse Headphones" in prompt
    assert "Sophisticated" in prompt
    assert "photorealistic" in prompt
    print("[PASS] Visual prompt builder verified")


def test_svg_banner_generation():
    test_file = STATIC_DIR / "test_banner.svg"
    generate_svg_banner(
        product_name="ZenPulse Headphones",
        headline="Silence the Noise. Amplify Focus.",
        cta="Shop Now",
        platform="Instagram",
        output_path=test_file
    )
    assert test_file.exists()
    content = test_file.read_text(encoding="utf-8")
    assert "<svg" in content
    assert "ZenPulse Headphones" in content
    assert "Silence the Noise" in content
    print("[PASS] SVG vector ad banner generator verified")


def test_generate_visual_ad():
    res = generate_visual_ad(
        prompt="Studio product photography of ZenPulse Headphones",
        headline="Focus Anytime",
        product_name="ZenPulse",
        cta="Get Started",
        platform="Instagram"
    )
    assert "image_url" in res
    assert "http://127.0.0.1:8000/static/generated_ads/" in res["image_url"]
    assert "provider" in res
    print(f"[PASS] Visual ad generated: {res['image_url']} (Provider: {res['provider']})")


def test_api_generate_image_endpoint():
    payload = {
        "prompt": "Commercial ad for ZenPulse Headphones",
        "headline": "Pure Acoustic Silence",
        "product_name": "ZenPulse",
        "cta": "Buy Now",
        "platform": "Instagram"
    }
    resp = client.post("/campaigns/generate-image", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "image_url" in data
    assert "http://127.0.0.1:8000/static/generated_ads/" in data["image_url"]
    print(f"[PASS] API endpoint POST /campaigns/generate-image verified: {data['image_url']}")


if __name__ == "__main__":
    test_build_ad_image_prompt()
    test_svg_banner_generation()
    test_generate_visual_ad()
    test_api_generate_image_endpoint()
    print("\nALL GENAI IMAGE GENERATION CHECKS PASSED SUCCESSFULLY!")
