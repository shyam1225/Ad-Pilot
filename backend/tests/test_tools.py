from app.services.tools import calculate_budget

print("Tool name:", calculate_budget.name)
print("Tool description:", calculate_budget.description)
print("Tool arguments:", calculate_budget.args)

from app.services.tools import recommend_platforms

result = recommend_platforms.invoke({
    "objective": "Brand Awareness"
})

print(result)