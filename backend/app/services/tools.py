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

    recommendations = {
        "brand awareness": ["Instagram", "YouTube", "Facebook"],
        "lead generation": ["LinkedIn", "Google Ads", "Facebook"],
        "sales": ["Google Ads", "Instagram", "Facebook"],
        "website traffic": ["Google Ads", "Instagram", "YouTube"]
    }

    result = recommendations.get(objective.lower())

    if result is None:
        raise ValueError("Unsupported campaign objective.")

    return result