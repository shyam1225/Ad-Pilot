from math import isclose


def validate_budget_allocation(strategy, total_budget):
    allocated_budget = sum(
        item.amount for item in strategy.budget_allocation
    )

    if not isclose(allocated_budget, total_budget, abs_tol=0.01):
        raise ValueError(
            f"Allocated budget ({allocated_budget}) "
            f"does not match campaign budget ({total_budget})."
        )

def validate_recommended_platforms(strategy, allowed_platforms):
    for platform in strategy.recommended_platforms:
        if platform not in allowed_platforms:
            raise ValueError(
                f"Platform '{platform}' is not allowed."
            )
def validate_duplicate_platforms(strategy):
    platforms = [
        item.platform.lower()
        for item in strategy.budget_allocation
    ]

    if len(platforms) != len(set(platforms)):
        raise ValueError(
            "Duplicate platforms found in budget allocation."
        )