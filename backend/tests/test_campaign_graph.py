
from app.services.campaign_graph import campaign_graph


initial_state = {
    "campaign": {
        "product_name": "Smartphone",
        "target_audience": "18-30 year olds in India",
        "budget": 500000,
        "objective": "Brand Awareness",
        "platforms": ["Instagram", "YouTube", "Facebook"]
    },
    "strategy": None,
    "retry_count": 0,
    "is_valid": False,
    "error": None
}


result = campaign_graph.invoke(initial_state)

print("\nFinal Campaign Strategy:")
print(result["strategy"])

print("\nValidation Status:", result["is_valid"])
print("Retry Count:", result["retry_count"])
print("Error:", result["error"])
