from src.agent import graph


result = graph.invoke({

    "user_requirements": {

        "room_type": "Bedroom",

        "dimensions": "10 × 12 ft",

        "budget": 10000,

        "currency": "PKR",

        "style": "Minimalist",

        "existing_furniture":
            "Bed, wardrobe, study table",

        "requirements":
            "Need more storage and better lighting."
    },

    "room_analysis": {

        "room_type": "bedroom",

        "visible_furniture": [
            "bed",
            "wardrobe",
            "study table"
        ],

        "colors": [
            "white",
            "brown"
        ],

        "lighting":
            "Limited natural light",

        "storage": [
            "wardrobe"
        ],

        "layout_issues": [
            "Limited storage space"
        ],

        "opportunities": [
            "Use vertical storage",
            "Improve task lighting"
        ]
    },

    "retrieved_knowledge": [],

    "available_products": [],

    "design_strategy": {},

    "selected_products": [],

    "budget_result": {},
    "budget_adjustment_attempts": 0,
    "budget_adjustment_made": False,
    "user_feedback": "",

    "final_plan": {}
})


print("\nFINAL STATE:\n")

print(result)

print("\nRETRIEVED KNOWLEDGE:\n")

for item in result["retrieved_knowledge"]:

    print(
        f"\nSource: {item['source']}"
    )

    print(
        item["content"]
    )

print("\nDESIGN STRATEGY:\n")

print(
    result["design_strategy"]
)

print("\nSELECTED PRODUCTS:\n")

for product in result["selected_products"]:

    print(
        f"{product['name']} - "
        f"{product['price']} "
        f"{product['currency']}"
    )

print("\nBUDGET RESULT:\n")

print(
    result["budget_result"]
)

print("\nFINAL PRODUCTS:\n")

for product in result["selected_products"]:
    print(
        product["name"],
        "-",
        product["price"],
        product["currency"]
    )

print("\nFINAL BUDGET:\n")

print(result["budget_result"])
