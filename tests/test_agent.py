import mimetypes
from pathlib import Path

from src.agent import graph


# Locate the test image relative to this file.
IMAGE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "bedroom.jpg"
)

if not IMAGE_PATH.is_file():
    raise FileNotFoundError(
        f"Test image not found: {IMAGE_PATH}\n"
        "Place a bedroom image at tests/fixtures/bedroom.jpg"
    )

# Read the image as bytes.
image_bytes = IMAGE_PATH.read_bytes()

# Determine the image MIME type.
mime_type, _ = mimetypes.guess_type(
    str(IMAGE_PATH)
)

if mime_type is None:
    raise ValueError(
        "Could not determine the image MIME type."
    )


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

    # Actual image supplied to Gemini Vision.
    "image_bytes": image_bytes,

    "mime_type": mime_type,

    # The agent will populate this from the image.
    "room_analysis": {},

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


print("\nROOM ANALYSIS:\n")
print(result["room_analysis"])

print("\nRETRIEVED KNOWLEDGE:\n")

for item in result["retrieved_knowledge"]:
    print(f"\nSource: {item['source']}")
    print(item["content"])

print("\nDESIGN STRATEGY:\n")
print(result["design_strategy"])

print("\nFINAL PRODUCTS:\n")

for product in result["selected_products"]:
    print(
        f"{product['name']} - "
        f"{product['price']} "
        f"{product['currency']}"
    )

print("\nFINAL BUDGET:\n")
print(result["budget_result"])
