import re
from typing import Optional
from langchain.tools import tool


@tool
def calculate_budget(total_budget: float, platforms: list[str]) -> dict:
    """
    Calculate an equal budget allocation across the given advertising platforms.

    Args:
        total_budget: Total campaign budget in INR.
        platforms: List of allowed advertising platforms.
    """
    if total_budget <= 0:
        raise ValueError("Budget must be greater than zero.")

    if not platforms:
        raise ValueError("At least one platform is required.")

    allocation = total_budget / len(platforms)

    result = {}
    for platform in platforms:
        result[platform] = round(allocation, 2)

    return result


@tool
def recommend_platforms(objective: str) -> list[str]:
    """
    Recommend advertising platforms based on the campaign objective.

    Args:
        objective: The objective of the advertising campaign.
    """
    clean_obj = objective.lower().replace("_", " ")

    recommendations = {
        "brand awareness": ["Instagram", "YouTube", "Facebook"],
        "lead generation": ["LinkedIn", "Google Ads", "Facebook"],
        "sales": ["Google Ads", "Instagram", "Facebook"],
        "website traffic": ["Google Ads", "Instagram", "YouTube"]
    }

    result = recommendations.get(clean_obj)
    if result is None:
        # Default fallback
        result = ["Instagram", "Google Ads", "Facebook"]

    return result


@tool
def allocate_weighted_budget(total_budget: float, platforms: list[str], objective: str) -> list[dict]:
    """
    Calculate a strategically weighted budget allocation based on the campaign objective
    and industry performance benchmarks for each platform.

    Args:
        total_budget: Total campaign budget amount.
        platforms: List of allowed platforms.
        objective: Campaign objective (e.g. SALES, BRAND_AWARENESS, LEAD_GENERATION, WEBSITE_TRAFFIC).
    """
    if total_budget <= 0:
        raise ValueError("Total budget must be greater than zero.")
    if not platforms:
        raise ValueError("At least one platform is required.")

    clean_obj = objective.upper().replace(" ", "_")

    # Platform affinity weights by objective
    weights_map = {
        "SALES": {
            "Google Ads": 1.4,
            "Instagram": 1.1,
            "Facebook": 1.0,
            "YouTube": 0.8,
            "LinkedIn": 0.7,
            "Snapchat": 0.6
        },
        "LEAD_GENERATION": {
            "LinkedIn": 1.5,
            "Google Ads": 1.3,
            "Facebook": 1.0,
            "Instagram": 0.8,
            "YouTube": 0.7,
            "Snapchat": 0.5
        },
        "BRAND_AWARENESS": {
            "Instagram": 1.4,
            "YouTube": 1.4,
            "Facebook": 1.0,
            "Snapchat": 0.9,
            "LinkedIn": 0.7,
            "Google Ads": 0.6
        },
        "WEBSITE_TRAFFIC": {
            "Google Ads": 1.4,
            "Facebook": 1.1,
            "Instagram": 1.0,
            "LinkedIn": 0.9,
            "YouTube": 0.8,
            "Snapchat": 0.6
        }
    }

    current_weights = weights_map.get(clean_obj, {})
    raw_weights = [current_weights.get(p, 1.0) for p in platforms]
    total_weight = sum(raw_weights)

    allocations = []
    accumulated_amount = 0.0

    for i, platform in enumerate(platforms):
        if i == len(platforms) - 1:
            # Reconcile exact difference to avoid floating point cent drift
            platform_amount = round(total_budget - accumulated_amount, 2)
        else:
            share = raw_weights[i] / total_weight
            platform_amount = round(total_budget * share, 2)
            accumulated_amount += platform_amount

        percentage = round((platform_amount / total_budget) * 100, 1)

        allocations.append({
            "platform": platform,
            "amount": platform_amount,
            "percentage": percentage,
            "weight_score": raw_weights[i]
        })

    return allocations


@tool
def validate_ad_character_limits(
    headlines: list[str],
    descriptions: list[str],
    platform: str = "Google Ads"
) -> dict:
    """
    Validates ad copy against platform character specifications.

    Args:
        headlines: List of ad headlines.
        descriptions: List of ad descriptions or body text.
        platform: Platform name (defaults to 'Google Ads').
    """
    violations = []

    if platform.lower() == "google ads":
        for i, h in enumerate(headlines):
            if len(h) > 30:
                violations.append(
                    f"Headline {i+1} ('{h}') exceeds Google Ads 30-character limit ({len(h)} chars)."
                )
        for i, d in enumerate(descriptions):
            if len(d) > 90:
                violations.append(
                    f"Description {i+1} exceeds Google Ads 90-character limit ({len(d)} chars)."
                )

    return {
        "platform": platform,
        "is_valid": len(violations) == 0,
        "violations": violations
    }


@tool
def check_advertising_compliance_rules(text_corpus: list[str]) -> list[dict]:
    """
    Scans a collection of ad copy texts for prohibited claims, deceptive guarantees,
    and major advertising policy violations.

    Args:
        text_corpus: List of text strings (headlines, descriptions, primary text).
    """
    # Prohibited pattern definitions (regex + explanation)
    prohibited_patterns = [
        (r"\b100%\s+guaranteed\b", "Absolute guarantee claim ('100% guaranteed') violates FTC/advertising standards"),
        (r"\bmiracle\s+(cure|product|results)\b", "Exaggerated/unsubstantiated health or miracle claim"),
        (r"\bget\s+rich\s+quick\b", "Deceptive financial earnings promise"),
        (r"\brisk[\s-]free\s+money\b", "Misleading financial risk claim"),
        (r"\bclick\s+here\s+now\b", "Aggressive low-quality engagement bait"),
        (r"\blose\s+\d+\s*(kg|lbs|pounds)\s+in\s+\d+\s*(days|weeks)\b", "Unsubstantiated rapid weight loss claim")
    ]

    violations = []
    for text in text_corpus:
        for pattern, explanation in prohibited_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                violations.append({
                    "matched_text": text,
                    "explanation": explanation
                })

    return violations


@tool
def estimate_platform_kpis(platform: str, budget: float, objective: str) -> dict:
    """
    Estimates key performance metrics based on standard digital advertising benchmarks in India (INR).

    Args:
        platform: Platform name.
        budget: Allocated budget in INR.
        objective: Campaign objective.
    """
    # Benchmark CPM & CPC estimates in INR
    benchmarks = {
        "Instagram": {"cpm": 180, "cpc": 12, "ctr": 0.015},
        "Facebook": {"cpm": 160, "cpc": 10, "ctr": 0.016},
        "Google Ads": {"cpm": 350, "cpc": 25, "ctr": 0.035},
        "YouTube": {"cpm": 220, "cpc": 18, "ctr": 0.012},
        "LinkedIn": {"cpm": 800, "cpc": 110, "ctr": 0.008},
        "Snapchat": {"cpm": 140, "cpc": 8, "ctr": 0.018}
    }

    bm = benchmarks.get(platform, {"cpm": 200, "cpc": 15, "ctr": 0.015})

    estimated_impressions = int((budget / bm["cpm"]) * 1000)
    estimated_clicks = int(budget / bm["cpc"])

    return {
        "platform": platform,
        "estimated_impressions": f"{estimated_impressions:,}",
        "estimated_clicks": f"{estimated_clicks:,}",
        "benchmark_ctr": f"{bm['ctr'] * 100:.1f}%",
        "benchmark_cpc": f"₹{bm['cpc']}"
    }
