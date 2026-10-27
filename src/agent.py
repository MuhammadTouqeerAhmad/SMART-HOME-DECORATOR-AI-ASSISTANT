from typing import TypedDict
from google import genai
from groq import Groq
from langgraph.graph import (
    StateGraph,
    START,
    END
)

from src.rag import retrieve_knowledge
from src.config import GEMINI_API_KEY
from src.models import DesignStrategy
from src.prompts import DESIGN_STRATEGY_PROMPT
from src.tools import select_products
from src.tools import calculate_budget
from src.tools import find_cheaper_alternative
from src.vision import analyze_room

from src.config import GROQ_API_KEY, GROQ_MODEL

# client = genai.Client(
#     api_key=GEMINI_API_KEY
# )

# MODEL_NAME = "gemini-3.6-flash"

groq_client = (
    Groq(api_key=GROQ_API_KEY)
    if GROQ_API_KEY
    else None
)

class DecoratorState(TypedDict):

    user_requirements: dict

    image_bytes: bytes
    mime_type: str

    room_analysis: dict

    retrieved_knowledge: list

    available_products: list

    design_strategy: dict

    selected_products: list

    budget_result: dict
    budget_adjustment_attempts: int
    budget_adjustment_made: bool
    user_feedback: str

    final_plan: dict

def analyze_room_node(state):

    print("Analyzing room...")

    image_bytes = state.get("image_bytes")
    mime_type = state.get("mime_type")

    # If an image is provided, analyze it using Gemini Vision.
    if image_bytes is not None:

        if not mime_type:
            raise ValueError(
                "mime_type is required when an image is provided."
            )

        room_analysis = analyze_room(
            image_bytes=image_bytes,
            mime_type=mime_type
        )

        # Convert the Pydantic model into a dictionary
        # for the existing downstream nodes.
        room_analysis = room_analysis.model_dump()

        print("\nRoom analysis completed:")
        print(room_analysis)

        return {
            **state,
            "room_analysis": room_analysis
        }

    # Backward compatibility for tests that supply
    # a room analysis manually.
    if state.get("room_analysis"):
        print("Using the supplied room analysis.")

        return state

    raise ValueError(
        "Provide image_bytes and mime_type, "
        "or supply an existing room_analysis."
    )

def retrieve_knowledge_node(state):

    print("Retrieving design knowledge...")

    user_requirements = state["user_requirements"]
    room_analysis = state["room_analysis"]

    query = f"""
    Room type: {user_requirements["room_type"]}

    Room dimensions: {user_requirements["dimensions"]}

    Preferred style: {user_requirements["style"]}

    Existing furniture:
    {user_requirements["existing_furniture"]}

    Requirements:
    {user_requirements["requirements"]}

    Room analysis:
    {room_analysis}
    """

    knowledge = retrieve_knowledge(
        query=query,
        top_k=4
    )

    return {
        **state,
        "retrieved_knowledge": knowledge
    }



def create_design_strategy_node(state):
    print("Creating design strategy with Groq...")

    if groq_client is None:
        raise ValueError(
            "GROQ_API_KEY is missing. "
            "Please add it to your .env file."
        )

    user_requirements = state["user_requirements"]
    room_analysis = state["room_analysis"]
    knowledge = state["retrieved_knowledge"]

    knowledge_text = "\n\n".join(
        [
            f"Source: {item['source']}\n{item['content']}"
            for item in knowledge
        ]
    )

    prompt = DESIGN_STRATEGY_PROMPT.format(
        room_type=user_requirements["room_type"],
        dimensions=user_requirements["dimensions"],
        budget=user_requirements["budget"],
        currency=user_requirements["currency"],
        style=user_requirements["style"],
        existing_furniture=user_requirements["existing_furniture"],
        requirements=user_requirements["requirements"],
        room_analysis=room_analysis,
        knowledge=knowledge_text,
    )

    schema = DesignStrategy.model_json_schema()

    system_message = """
        You are an expert interior design assistant.

        Return ONLY a valid JSON object. Do not use Markdown or code fences.

        The user's specified room type is authoritative.
        Design only that type of room.

        Ground every recommendation in the provided room analysis,
        existing furniture, user requirements, and retrieved knowledge.

        Do not invent furniture or room features.
        Do not recommend replacing existing furniture unless requested.
        Prefer practical improvements that preserve usable walking space.

        For a bedroom, focus on the bed, bedside furniture, bedroom
        lighting, storage, colors, and bedroom layout. Do not recommend
        a sofa, media wall, TV stand, or coffee table unless explicitly
        requested by the user.

        Product selection is handled by a separate workflow node.
        Do not invent product names or prices.

        For improvement_priorities, use categories that can be mapped
        to actual product catalog categories where products are needed.
        For example, use "lighting" or "storage" rather than vague
        categories such as "space utilization" when recommending products.
        Furniture rearrangement can be recommended without requiring
        a product purchase.

        Return all seven required fields:
        design_summary, furniture_changes, lighting_plan, storage_plan,
        color_plan, improvement_priorities, explanation.

        Each improvement priority must contain category, priority,
        and reason. Priority must be required, recommended, or optional.
        Use arrays for list fields and follow the supplied JSON schema.
        """

    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": system_message,
            },
            {
                "role": "user",
                "content": (
                    "Create a design strategy using the following "
                    "actual user and room information.\n\n"
                    f"{prompt}\n\n"
                    "Required JSON schema:\n"
                    f"{schema}\n\n"
                    "Before responding, verify that the design matches "
                    f"this room type: {user_requirements['room_type']}. "
                    "Do not describe a different room."
                ),
            },
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
        max_completion_tokens=3000,
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError(
            "Groq returned an empty design strategy."
        )

    strategy = DesignStrategy.model_validate_json(content)

    # Additional safeguard: reject a strategy that clearly describes
    # a different room instead of silently passing it downstream.
    summary = strategy.design_summary.lower()

    if (
        user_requirements["room_type"].lower() == "bedroom"
        and "living room" in summary
    ):
        raise ValueError(
            "Groq generated a living-room strategy for a bedroom. "
            "Check DESIGN_STRATEGY_PROMPT and the supplied room data."
        )

    print("Design strategy generated successfully.")

    return {
        **state,
        "design_strategy": strategy.model_dump(),
    }



def normalize_product_category(category):

    category = category.lower()

    if "storage" in category:
        return "storage"

    if "lighting" in category or "light" in category:
        return "lighting"

    if "furniture" in category:
        return "furniture"

    if "rug" in category:
        return "rug"

    return None


def build_product_keywords(strategy):
    """
    Extract useful product-matching keywords from the design strategy.
    """
    keyword_map = {
        "storage": [
            "storage",
            "organizer",
            "shelf",
            "wall-mounted",
            "under-bed",
            "basket",
            "container",
        ],
        "lighting": [
            "lighting",
            "lamp",
            "study",
            "task",
            "desk",
            "warm",
            "led",
        ],
        "rug": [
            "rug",
            "area rug",
            "floor",
        ],
        "furniture": [
            "furniture",
            "table",
            "chair",
        ],
    }

    # Combine the plan's recommendations into searchable text.
    strategy_text = " ".join(
        str(value)
        for key in (
            "storage_plan",
            "lighting_plan",
            "furniture_changes",
            "color_plan",
            "design_summary",
            "explanation",
        )
        for value in (
            strategy.get(key, [])
            if isinstance(strategy.get(key, []), list)
            else [strategy.get(key, "")]
        )
    ).lower()

    return {
        category: [
            keyword
            for keyword in keywords
            if keyword in strategy_text
        ]
        for category, keywords in keyword_map.items()
    }


# def search_products_node(state):

#     print("\nImprovement priorities:")
    

#     print("Searching products...")

#     strategy = state["design_strategy"]
#     user_requirements = state["user_requirements"]

#     priorities = strategy["improvement_priorities"]
#     keywords_by_category = build_product_keywords(strategy)

#     for improvement in priorities:
#         print(improvement)
    
#     required_categories = []
#     recommended_categories = []
#     optional_categories = []

#     for improvement in priorities:

#         category = normalize_product_category(
#             improvement["category"]
#         )

#         if category is None:
#             continue

#         priority = str(improvement["priority"]).lower()

#         if priority == "required":

#             required_categories.append(category)

#         elif priority == "recommended":

#             recommended_categories.append(category)

#         elif priority == "optional":

#             optional_categories.append(category)

#     required_categories = list(
#         dict.fromkeys(required_categories)
#     )

#     recommended_categories = list(
#         dict.fromkeys(recommended_categories)
#     )

#     optional_categories = list(
#         dict.fromkeys(optional_categories)
#     )

#     required_products = select_products(
#         categories=required_categories,
#         style=user_requirements["style"],
#         keywords_by_category=keywords_by_category
#     )

#     for product in required_products:
#         product["priority"] = "required"

#     recommended_products = select_products(
#         categories=recommended_categories,
#         style=user_requirements["style"],
#         keywords_by_category=keywords_by_category
#     )

#     for product in recommended_products:
#         product["priority"] = "recommended"

#     optional_products = select_products(
#         categories=optional_categories,
#         style=user_requirements["style"],
#         keywords_by_category=keywords_by_category
#     )

#     for product in optional_products:
#         product["priority"] = "optional"

#     products = (
#         required_products
#         + recommended_products
#         + optional_products
#     )

#     print("\nSelected products:")

#     for product in products:

#         print(
#             f"- {product['name']} "
#             f"({product['price']} PKR) "
#             f"[{product['priority']}]"
#         )

#     return {
#         **state,
#         "selected_products": products,
#         "available_products": products
#     }


def search_products_node(state):
    print("\nImprovement priorities:")
    print("Searching products...")

    strategy = state["design_strategy"]
    user_requirements = state["user_requirements"]

    priorities = strategy["improvement_priorities"]
    keywords_by_category = build_product_keywords(strategy)

    for improvement in priorities:
        print(improvement)

    required_categories = []
    recommended_categories = []
    optional_categories = []

    for improvement in priorities:
        category = normalize_product_category(
            improvement["category"]
        )

        # Ignore improvements that do not map to a real
        # product category in the catalog.
        if category is None:
            continue

        priority = str(improvement["priority"]).lower()

        if priority == "required":
            required_categories.append(category)
        elif priority == "recommended":
            recommended_categories.append(category)
        elif priority == "optional":
            optional_categories.append(category)

    required_categories = list(dict.fromkeys(required_categories))
    recommended_categories = list(dict.fromkeys(recommended_categories))
    optional_categories = list(dict.fromkeys(optional_categories))

    # Select required products first.
    required_products = select_products(
        categories=required_categories,
        style=user_requirements["style"],
        keywords_by_category=keywords_by_category,
    )

    selected_ids = {
        product["id"] for product in required_products
    }

    for product in required_products:
        product["priority"] = "required"

    # Select recommended products, excluding existing selections.
    recommended_products = select_products(
        categories=recommended_categories,
        style=user_requirements["style"],
        keywords_by_category=keywords_by_category,
        exclude_ids=selected_ids,
    )

    selected_ids.update(
        product["id"] for product in recommended_products
    )

    for product in recommended_products:
        product["priority"] = "recommended"

    # Select optional products, excluding higher-priority selections.
    optional_products = select_products(
        categories=optional_categories,
        style=user_requirements["style"],
        keywords_by_category=keywords_by_category,
        exclude_ids=selected_ids,
    )

    for product in optional_products:
        product["priority"] = "optional"

    # Defensive deduplication: keep the highest-priority occurrence.
    products = []
    seen_product_ids = set()

    for product in (
        required_products
        + recommended_products
        + optional_products
    ):
        product_id = product["id"]

        if product_id in seen_product_ids:
            print(
                f"Skipping duplicate product: {product['name']}"
            )
            continue

        seen_product_ids.add(product_id)
        products.append(product)

    print("\nSelected products:")

    for product in products:
        print(
            f"- {product['name']} "
            f"({product['price']} PKR) "
            f"[{product['priority']}]"
        )

    return {
        **state,
        "selected_products": products,
        "available_products": products,
    }


def check_budget_node(state):

    print("Checking budget...")

    user_requirements = state["user_requirements"]

    selected_products = state["selected_products"]

    budget = user_requirements["budget"]

    budget_result = calculate_budget(
        items=selected_products,
        budget=budget
    )

    return {
        **state,
        "budget_result": budget_result
    }

MAX_BUDGET_ADJUSTMENT_ATTEMPTS = 3


def budget_decision(state):
    budget = float(state["user_requirements"]["budget"])

    total = sum(
        float(product["price"])
        for product in state.get("selected_products", [])
    )

    if total <= budget:
        return "within_budget"

    attempts = state.get("budget_adjustment_attempts", 0)

    if attempts >= MAX_BUDGET_ADJUSTMENT_ATTEMPTS:
        return "budget_limit_reached"

    return "over_budget"

def handle_over_budget_node(state):
    """
    Try cheaper alternatives first. If the total is
    still too high, remove optional products first,
    followed by recommended products.

    Required products are preserved whenever possible.
    """

    print("Optimizing product selection...")

    products = [
        dict(product)
        for product in state.get("selected_products", [])
    ]

    requirements = state["user_requirements"]
    budget = float(requirements["budget"])
    style = requirements.get("style")

    current_total = sum(
        float(product["price"])
        for product in products
    )

    adjustment_made = False

    # Stop immediately if already within budget.
    if current_total <= budget:
        return {
            **state,
            "selected_products": products,
            "budget_adjustment_attempts": (
                state.get("budget_adjustment_attempts", 0) + 1
            ),
            "budget_adjustment_made": False,
        }

    # STEP 1: Try cheaper alternatives.
    # Process expensive items first.
    for index in sorted(
        range(len(products)),
        key=lambda i: float(products[i]["price"]),
        reverse=True,
    ):
        product = products[index]

        # alternative = find_cheaper_alternative(
        #     product=product,
        #     style=style,
        # )

        # Exclude IDs of all other currently selected products.
        already_selected_ids = {
            item["id"]
            for other_index, item in enumerate(products)
            if other_index != index
        }

        alternative = find_cheaper_alternative(
            product=product,
            style=style,
            exclude_ids=already_selected_ids,
        )

        if alternative:
            alternative = dict(alternative)

            # Preserve the original priority.
            alternative["priority"] = product.get(
                "priority", "recommended"
            )

            if float(alternative["price"]) < float(
                product["price"]
            ):
                print(
                    f"Replacing {product['name']} with "
                    f"{alternative['name']}"
                )

                products[index] = alternative
                adjustment_made = True

    current_total = sum(
        float(product["price"])
        for product in products
    )

    print(f"Total after alternatives: {current_total:.2f}")

    # STEP 2: Remove lower-priority items if necessary.
    priority_order = {
        "optional": 0,
        "recommended": 1,
        "required": 2,
    }

    if current_total > budget:
        products.sort(
            key=lambda product: (
                priority_order.get(
                    str(product.get("priority", "recommended")).lower(),
                    1,
                ),
                -float(product["price"]),
            )
        )

        while products:
            current_total = sum(
                float(product["price"])
                for product in products
            )

            if current_total <= budget:
                break

            # Remove optional/recommended products first.
            # Required products are removed only if needed
            # to get under budget.
            removed = products.pop(0)

            print(
                f"Removed {removed['name']} "
                f"({removed['price']} PKR)"
            )

            adjustment_made = True

    attempts = state.get("budget_adjustment_attempts", 0) + 1

    return {
        **state,
        "selected_products": products,
        "budget_adjustment_attempts": attempts,
        "budget_adjustment_made": adjustment_made,
    }

def finalize_node(state):
    print("Finalizing plan...")

    requirements = state["user_requirements"]
    budget = float(requirements["budget"])
    products = state.get("selected_products", [])

    # Always recalculate from the final product list.
    total = sum(
        float(product["price"])
        for product in products
    )

    remaining = budget - total
    within_budget = total <= budget

    budget_result = {
        "items": products,
        "total": total,
        "budget": budget,
        "remaining": remaining,
        "within_budget": within_budget,
    }

    if within_budget:
        budget_status = "Within budget"
    else:
        budget_status = (
            "Over budget: suitable products could not "
            "be selected within the available catalog."
        )

    final_plan = {
        "design_strategy": state.get("design_strategy", {}),
        "selected_products": products,
        "budget_result": budget_result,
        "budget_status": budget_status,
    }

    return {
        **state,
        "budget_result": budget_result,
        "final_plan": final_plan,
    }

builder = StateGraph(
    DecoratorState
)


builder.add_node(
    "analyze_room",
    analyze_room_node
)

builder.add_node(
    "retrieve_knowledge",
    retrieve_knowledge_node
)

builder.add_node(
    "create_design_strategy",
    create_design_strategy_node
)

builder.add_node(
    "search_products",
    search_products_node
)

builder.add_node(
    "check_budget",
    check_budget_node
)

builder.add_node(
    "handle_over_budget",
    handle_over_budget_node
)


builder.add_node(
    "finalize",
    finalize_node
)


builder.add_edge(
    START,
    "analyze_room"
)

builder.add_edge(
    "analyze_room",
    "retrieve_knowledge"
)

builder.add_edge(
    "retrieve_knowledge",
    "create_design_strategy"
)

builder.add_edge(
    "create_design_strategy",
    "search_products"
)

builder.add_edge(
    "search_products",
    "check_budget"
)

builder.add_conditional_edges(

    "check_budget",

    budget_decision,

    {
        "within_budget": "finalize",

        "over_budget":
            "handle_over_budget",

        "budget_limit_reached":
            "finalize"
    }
)
builder.add_edge(
    "handle_over_budget",
    "check_budget"
)

builder.add_edge(
    "finalize",
    END
)


graph = builder.compile()