# from typing import TypedDict

# from langgraph.graph import StateGraph, START, END

# from src.tools import search_products, calculate_budget
# from google import genai

# from src.config import GEMINI_API_KEY
# from src.models import DesignStrategy
# from src.prompts import DESIGN_STRATEGY_PROMPT


# client = genai.Client(
#     api_key=GEMINI_API_KEY
# )

# # ==========================================
# # STATE
# # ==========================================

# class DecoratorState(TypedDict):

#     user_requirements: dict
#     room_analysis: dict
#     retrieved_knowledge: list
#     available_products: list
#     selected_products: list
#     budget_result: dict
#     design_strategy: dict
#     user_feedback: str
#     final_plan: dict


# # ==========================================
# # NODES
# # ==========================================

# def analyze_room_node(state):

#     return {
#         "room_analysis": state.get(
#             "room_analysis",
#             {}
#         )
#     }


# def retrieve_knowledge_node(state):

#     room_type = (
#         state["user_requirements"]
#         ["room_type"]
#     )

#     style = (
#         state["user_requirements"]
#         ["style"]
#     )

#     knowledge = [
#         f"Design knowledge for {room_type}",
#         f"Design knowledge for {style}"
#     ]

#     return {
#         "retrieved_knowledge": knowledge
#     }


# def product_search_node(state):

#     requirements = state[
#         "user_requirements"
#     ]

#     style = requirements["style"]

#     products = search_products(
#         style=style
#     )

#     return {
#         "available_products": products
#     }


#     # Your Gemini design strategy code goes here

#     # For now, if you already have your
#     # Gemini implementation, keep that code.
# def design_strategy_node(state):

#     requirements = state[
#         "user_requirements"
#     ]

#     prompt = DESIGN_STRATEGY_PROMPT.format(

#         room_type=requirements["room_type"],

#         dimensions=requirements["dimensions"],

#         budget=requirements["budget"],

#         currency=requirements["currency"],

#         style=requirements["style"],

#         existing_furniture=requirements[
#             "existing_furniture"
#         ],

#         requirements=requirements[
#             "requirements"
#         ],

#         room_analysis=state[
#             "room_analysis"
#         ],

#         knowledge=state[
#             "retrieved_knowledge"
#         ],

#         products=state[
#             "available_products"
#         ]
#     )


#     interaction = client.interactions.create(

#         model="gemini-3.6-flash",

#         input=prompt,

#         response_format={

#             "type": "text",

#             "mime_type": "application/json",

#             "schema":
#                 DesignStrategy
#                 .model_json_schema()
#         }
#     )


#     strategy = DesignStrategy.model_validate_json(
#         interaction.output_text
#     )


#     return {
#         "design_strategy":
#             strategy.model_dump()
#     }



# def budget_node(state):

#     strategy = state[
#         "design_strategy"
#     ]

#     selected_products = (
#         strategy["recommended_products"]
#     )

#     items = []

#     for product in selected_products:

#         items.append({
#             "name": product["name"],
#             "price": product["price"],
#             "product_id": product["product_id"]
#         })

#     result = calculate_budget(items)

#     budget = (
#         state["user_requirements"]
#         ["budget"]
#     )

#     if result["total"] <= budget:

#         status = "within_budget"

#     else:

#         status = "over_budget"

#     return {
#         "selected_products": items,

#         "budget_result": {
#             "total": result["total"],
#             "budget": budget,
#             "status": status
#         }
#     }


# # ==========================================
# # CONDITIONAL DECISION
# # ==========================================

# def budget_decision(state):

#     status = (
#         state["budget_result"]
#         ["status"]
#     )

#     if status == "within_budget":

#         return "finalize"

#     return "reduce_cost"


# # ==========================================
# # OVER-BUDGET NODE
# # ==========================================

# def reduce_cost_node(state):

#     print(
#         "Budget exceeded. "
#         "Looking for cheaper alternatives..."
#     )

#     return {
#         "budget_result": {
#             **state["budget_result"],
#             "status": "needs_revision"
#         }
#     }


# # ==========================================
# # FINAL NODE
# # ==========================================

# def finalize_node(state):

#     design_strategy = (
#         state["design_strategy"]
#     )

#     budget_result = (
#         state["budget_result"]
#     )

#     final_plan = {

#         "design_strategy":
#             design_strategy,

#         "selected_products":
#             state["selected_products"],

#         "budget":
#             budget_result
#     }

#     return {
#         "final_plan": final_plan
#     }


# # ==========================================
# # GRAPH
# # ==========================================

# builder = StateGraph(
#     DecoratorState
# )


# builder.add_node(
#     "analyze_room",
#     analyze_room_node
# )

# builder.add_node(
#     "retrieve_knowledge",
#     retrieve_knowledge_node
# )

# builder.add_node(
#     "search_products",
#     product_search_node
# )

# builder.add_node(
#     "create_design_strategy",
#     design_strategy_node
# )

# builder.add_node(
#     "check_budget",
#     budget_node
# )

# builder.add_node(
#     "reduce_cost",
#     reduce_cost_node
# )

# builder.add_node(
#     "finalize",
#     finalize_node
# )


# # ==========================================
# # EDGES
# # ==========================================

# builder.add_edge(
#     START,
#     "analyze_room"
# )

# builder.add_edge(
#     "analyze_room",
#     "retrieve_knowledge"
# )

# builder.add_edge(
#     "retrieve_knowledge",
#     "search_products"
# )

# builder.add_edge(
#     "search_products",
#     "create_design_strategy"
# )

# builder.add_edge(
#     "create_design_strategy",
#     "check_budget"
# )


# builder.add_conditional_edges(

#     "check_budget",

#     budget_decision,

#     {
#         "finalize":
#             "finalize",

#         "reduce_cost":
#             "reduce_cost"
#     }
# )


# builder.add_edge(
#     "reduce_cost",
#     "finalize"
# )

# builder.add_edge(
#     "finalize",
#     END
# )


# graph = builder.compile()

# if __name__ == "__main__":

#     result = graph.invoke({

#         "user_requirements": {

#             "room_type": "Bedroom",

#             "dimensions": "10 × 12 ft",

#             "budget": 30000,

#             "currency": "PKR",

#             "style": "Minimalist",

#             "existing_furniture": (
#                 "Bed, wardrobe, study table and chair"
#             ),

#             "requirements": (
#                 "I need more storage and better lighting."
#             )
#         },

#         "room_analysis": {},

#         "retrieved_knowledge": [],

#         "available_products": [],

#         "selected_products": [],

#         "budget_result": {},

#         "design_strategy": {},

#         "user_feedback": "",

#         "final_plan": {}
#     })


#     print("\n========== FINAL RESULT ==========\n")

#     print(result)

from typing import TypedDict
from google import genai
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


client = genai.Client(
    api_key=GEMINI_API_KEY
)

MODEL_NAME = "gemini-3.6-flash"

class DecoratorState(TypedDict):

    user_requirements: dict

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

    return state


# def retrieve_knowledge_node(state):

#     print("Retrieving design knowledge...")

#     return state

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


# def create_design_strategy_node(state):

#     print("Creating design strategy...")

#     return state

def create_design_strategy_node(state):

    print("Creating design strategy...")

    user_requirements = state["user_requirements"]

    room_analysis = state["room_analysis"]

    knowledge = state["retrieved_knowledge"]

    knowledge_text = "\n\n".join(
        [
            (
                f"Source: {item['source']}\n"
                f"{item['content']}"
            )
            for item in knowledge
        ]
    )

    prompt = DESIGN_STRATEGY_PROMPT.format(

        room_type=user_requirements["room_type"],

        dimensions=user_requirements["dimensions"],

        budget=user_requirements["budget"],

        currency=user_requirements["currency"],

        style=user_requirements["style"],

        existing_furniture=
            user_requirements["existing_furniture"],

        requirements=
            user_requirements["requirements"],

        room_analysis=room_analysis,

        knowledge=knowledge_text
    )

    interaction = client.interactions.create(

        model=MODEL_NAME,

        input=prompt,

        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema":
                DesignStrategy.model_json_schema()
        }
    )

    strategy = DesignStrategy.model_validate_json(
        interaction.output_text
    )

    return {
        **state,
        "design_strategy":
            strategy.model_dump()
    }

# def search_products_node(state):

#     print("Searching products...")

#     return state

# def search_products_node(state):

#     print("Searching products...")

#     strategy = state["design_strategy"]

#     user_requirements = state["user_requirements"]

#     categories = []

#     if strategy["storage_plan"]:
#         categories.append("storage")

#     if strategy["lighting_plan"]:
#         categories.append("lighting")

#     if strategy["furniture_changes"]:
#         categories.append("furniture")

#     categories = list(
#         dict.fromkeys(categories)
#     )

#     products = select_products(
#         categories=categories,
#         style=user_requirements["style"]
#     )

#     return {
#         **state,
#         "selected_products": products,
#         "available_products": products
#     }
# def search_products_node(state):

#     print("Searching products...")

#     strategy = state["design_strategy"]
#     user_requirements = state["user_requirements"]

#     categories = []

#     if strategy["storage_plan"]:
#         categories.append("storage")

#     if strategy["lighting_plan"]:
#         categories.append("lighting")

#     # Furniture is currently treated as optional.
#     # We don't want it to automatically consume the budget.
#     if strategy["furniture_changes"]:
#         categories.append("furniture")

#     categories = list(
#         dict.fromkeys(categories)
#     )

#     products = select_products(
#         categories=categories,
#         style=user_requirements["style"]
#     )

#     return {
#         **state,
#         "selected_products": products,
#         "available_products": products
#     }

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

def search_products_node(state):

    print("\nImprovement priorities:")
    

    print("Searching products...")

    strategy = state["design_strategy"]
    user_requirements = state["user_requirements"]

    priorities = strategy["improvement_priorities"]

    for improvement in priorities:
        print(improvement)
    
    required_categories = []
    recommended_categories = []
    optional_categories = []

    for improvement in priorities:

        category = normalize_product_category(
            improvement["category"]
        )

        if category is None:
            continue

        priority = str(improvement["priority"]).lower()

        if priority == "required":

            required_categories.append(category)

        elif priority == "recommended":

            recommended_categories.append(category)

        elif priority == "optional":

            optional_categories.append(category)

    required_categories = list(
        dict.fromkeys(required_categories)
    )

    recommended_categories = list(
        dict.fromkeys(recommended_categories)
    )

    optional_categories = list(
        dict.fromkeys(optional_categories)
    )

    required_products = select_products(
        categories=required_categories,
        style=user_requirements["style"]
    )

    for product in required_products:
        product["priority"] = "required"

    recommended_products = select_products(
        categories=recommended_categories,
        style=user_requirements["style"]
    )

    for product in recommended_products:
        product["priority"] = "recommended"

    optional_products = select_products(
        categories=optional_categories,
        style=user_requirements["style"]
    )

    for product in optional_products:
        product["priority"] = "optional"

    products = (
        required_products
        + recommended_products
        + optional_products
    )

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
        "available_products": products
    }

# def search_products_node(state):

#     print("Searching products...")

#     strategy = state["design_strategy"]
#     user_requirements = state["user_requirements"]

#     priorities = strategy["improvement_priorities"]

#     # Required categories
#     required_categories = []

#     # Recommended categories
#     recommended_categories = []

#     # Optional categories
#     optional_categories = []

#     for improvement in priorities:

#         category = improvement["category"].lower()
#         priority = improvement["priority"].lower()

#         # Map LLM categories to our product categories
#         if "storage" in category:
#             category = "storage"

#         elif "lighting" in category:
#             category = "lighting"

#         elif "furniture" in category:
#             category = "furniture"

#         elif "rug" in category:
#             category = "rug"

#         else:
#             continue

#         if priority == "required":

#             required_categories.append(category)

#         elif priority == "recommended":

#             recommended_categories.append(category)

#         elif priority == "optional":

#             optional_categories.append(category)

#     # Remove duplicate categories while preserving order
#     required_categories = list(
#         dict.fromkeys(required_categories)
#     )

#     recommended_categories = list(
#         dict.fromkeys(recommended_categories)
#     )

#     optional_categories = list(
#         dict.fromkeys(optional_categories)
#     )

#     # -------------------------------------------------
#     # Select products according to priority
#     # -------------------------------------------------

#     required_products = select_products(
#         categories=required_categories,
#         style=user_requirements["style"]
#     )

#     recommended_products = select_products(
#         categories=recommended_categories,
#         style=user_requirements["style"]
#     )

#     optional_products = select_products(
#         categories=optional_categories,
#         style=user_requirements["style"]
#     )

#     # -------------------------------------------------
#     # Keep priority information with each product
#     # -------------------------------------------------

#     for product in required_products:
#         product["priority"] = "required"

#     for product in recommended_products:
#         product["priority"] = "recommended"

#     for product in optional_products:
#         product["priority"] = "optional"

#     products = (
#         required_products
#         + recommended_products
#         + optional_products
#     )

#     return {
#         **state,
#         "selected_products": products,
#         "available_products": products
#     }
# def check_budget_node(state):

#     print("Checking budget...")

#     return state
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

# def budget_decision(state):

#     budget_result = state["budget_result"]

#     if budget_result["within_budget"]:
#         return "within_budget"

#     return "over_budget"

def budget_decision(state):

    budget_result = state["budget_result"]

    attempts = state["budget_adjustment_attempts"]

    # Product selection is within the budget
    if budget_result["within_budget"]:
        return "within_budget"

    # Prevent infinite adjustment loops
    if attempts >= 3:
        return "budget_limit_reached"

    return "over_budget"

# def handle_over_budget_node(state):

#     print("Budget exceeded. Adjusting product selection...")

#     return state


# def handle_over_budget_node(state):

#     print(
#         "Budget exceeded. Looking for cheaper alternatives..."
#     )

#     attempts = state["budget_adjustment_attempts"]

#     if attempts >= 3:

#         print(
#         "Maximum budget adjustment attempts reached."
#         )

#         return {
#         **state,
#         "budget_adjustment_attempts": attempts + 1
#         }
    
#     products = state["selected_products"]

#     user_requirements = state["user_requirements"]

#     budget = user_requirements["budget"]

#     style = user_requirements["style"]

#     adjusted_products = list(products)

#     # Process the most expensive products first
#     products_by_price = sorted(
#         products,
#         key=lambda item: item["price"],
#         reverse=True
#     )

#     for product in products_by_price:

#         current_total = sum(
#             item["price"]
#             for item in adjusted_products
#         )

#         if current_total <= budget:
#             break

#         remaining_budget = (
#             budget - (
#                 current_total - product["price"]
#             )
#         )

#         alternative = find_cheaper_alternative(
#             product=product,
#             style=style,
#             max_price=remaining_budget
#         )

#         if alternative:

#             adjusted_products = [
#                 (
#                     alternative
#                     if item["id"] == product["id"]
#                     else item
#                 )
#                 for item in adjusted_products
#             ]

#     return {
#         **state,
#         "selected_products": adjusted_products,
#         "budget_adjustment_attempts": attempts + 1
#     }

# def handle_over_budget_node(state):

#     print(
#         "Budget exceeded. Looking for cheaper alternatives..."
#     )

#     products = state["selected_products"]

#     user_requirements = state["user_requirements"]

#     budget = user_requirements["budget"]

#     style = user_requirements["style"]

#     current_total = sum(
#         product["price"]
#         for product in products
#     )

#     adjusted_products = list(products)
#     adjustment_made = False
#     # Sort expensive products first
#     products_by_price = sorted(
#         adjusted_products,
#         key=lambda item: item["price"],
#         reverse=True
#     )

#     for product in products_by_price:

#         current_total = sum(
#             item["price"]
#             for item in adjusted_products
#         )

#         if current_total <= budget:
#             break

#         # How much money can we spend on this product
#         # while keeping the complete selection within budget?
#         other_products_total = (
#             current_total - product["price"]
#         )

#         maximum_allowed_price = (
#             budget - other_products_total
#         )

#         alternative = find_cheaper_alternative(
#             product=product,
#             style=style,
#             max_price=maximum_allowed_price
#         )

#         if alternative:

#             print(
#                 f"Replacing {product['name']} "
#                 f"with {alternative['name']}"
#             )

#             adjusted_products = [
#                 (
#                     alternative
#                     if item["id"] == product["id"]
#                     else item
#                 )
#                 for item in adjusted_products
#             ]
#             adjustment_made = True
#             # Recalculate immediately
#             current_total = sum(
#                 item["price"]
#                 for item in adjusted_products
#             )

#             if current_total <= budget:
#                 break

#     return {
#         **state,
#         "selected_products": adjusted_products,
#         "budget_adjustment_attempts":
#             state["budget_adjustment_attempts"] + 1,
#         "budget_adjustment_made": adjustment_made
#     }

# def handle_over_budget_node(state):

#     print(
#         "Budget exceeded. Optimizing product selection..."
#     )

#     products = list(
#         state["selected_products"]
#     )

#     user_requirements = state["user_requirements"]

#     budget = user_requirements["budget"]

#     style = user_requirements["style"]

#     adjustment_made = False

#     # -------------------------------------------------
#     # STEP 1: Try cheaper alternatives
#     # -------------------------------------------------

#     products_by_price = sorted(
#         products,
#         key=lambda item: item["price"],
#         reverse=True
#     )

#     for product in products_by_price:

#         current_total = sum(
#             item["price"]
#             for item in products
#         )

#         if current_total <= budget:
#             break

#         other_products_total = (
#             current_total - product["price"]
#         )

#         maximum_allowed_price = (
#             budget - other_products_total
#         )

#         if maximum_allowed_price <= 0:
#             continue

#         alternative = find_cheaper_alternative(
#             product=product,
#             style=style,
#             max_price=maximum_allowed_price
#         )

#         if alternative:

#             print(
#                 f"Replacing "
#                 f"{product['name']} "
#                 f"with "
#                 f"{alternative['name']}"
#             )

#             products = [
#                 (
#                     alternative
#                     if item["id"] == product["id"]
#                     else item
#                 )
#                 for item in products
#             ]

#             adjustment_made = True

#     # -------------------------------------------------
#     # STEP 2: Remove products if still over budget
#     # -------------------------------------------------

#     current_total = sum(
#         item["price"]
#         for item in products
#     )

#     if current_total > budget:

#         print(
#             "Still over budget. "
#             "Removing lower-priority products..."
#         )

#         # Remove the most expensive products first.
#         # This guarantees the total moves toward
#         # the user's budget.
#         products = sorted(
#             products,
#             key=lambda item: item["price"],
#             reverse=True
#         )

#         while products:

#             current_total = sum(
#                 item["price"]
#                 for item in products
#             )

#             if current_total <= budget:
#                 break

#             removed = products.pop(0)

#             print(
#                 f"Removing {removed['name']} "
#                 f"({removed['price']} PKR)"
#             )

#             adjustment_made = True

#     return {
#         **state,

#         "selected_products": products,

#         "budget_adjustment_attempts":
#             state["budget_adjustment_attempts"] + 1,

#         "budget_adjustment_made":
#             adjustment_made
#     }

def handle_over_budget_node(state):

    print(
        "Budget exceeded. Optimizing product selection..."
    )

    products = list(
        state["selected_products"]
    )

    user_requirements = state["user_requirements"]

    budget = user_requirements["budget"]

    style = user_requirements["style"]

    adjustment_made = False

    # -------------------------------------------------
    # STEP 1
    # Replace expensive products with cheaper
    # alternatives wherever possible.
    # -------------------------------------------------

    products_by_price = sorted(
        products,
        key=lambda item: item["price"],
        reverse=True
    )

    for product in products_by_price:

        alternative = find_cheaper_alternative(
            product=product,
            style=style
        )

        if alternative:

            print(
                f"Replacing "
                f"{product['name']} "
                f"with "
                f"{alternative['name']}"
            )

            products = [
                (
                    alternative
                    if item["id"] == product["id"]
                    else item
                )
                for item in products
            ]

            adjustment_made = True

    # -------------------------------------------------
    # STEP 2
    # Check the new total after cheaper alternatives.
    # -------------------------------------------------

    current_total = sum(
        item["price"]
        for item in products
    )

    print(
        f"Total after cheaper alternatives: "
        f"{current_total} PKR"
    )

    # -------------------------------------------------
    # STEP 3
    # If still over budget, remove products.
    # -------------------------------------------------
    if current_total > budget:

        print(
        "Still over budget. "
        "Removing lowest-priority products..."
        )

        priority_order = {
            "optional": 0,
            "recommended": 1,
            "required": 2
        }

        products = sorted(
            products,
            key=lambda item: (
                priority_order.get(
                    item.get("priority", "recommended"),
                    1
                ),
                -item["price"]
            )
        )

        while products:

            current_total = sum(
                item["price"]
                for item in products
            )

            if current_total <= budget:
                break

            removed = products.pop(0)

            print(
                f"Removing "
                f"{removed['name']} "
                f"({removed['price']} PKR) "
                f"[{removed.get('priority', 'unknown')}]"
            )

            adjustment_made = True
    # if current_total > budget:

    #     print(
    #         "Still over budget. "
    #         "Removing products..."
    #     )

    #     products = sorted(
    #         products,
    #         key=lambda item: item["price"],
    #         reverse=True
    #     )

    #     while products:

    #         current_total = sum(
    #             item["price"]
    #             for item in products
    #         )

    #         if current_total <= budget:
    #             break

    #         removed = products.pop(0)

    #         print(
    #             f"Removing "
    #             f"{removed['name']} "
    #             f"({removed['price']} PKR)"
    #         )

    #         adjustment_made = True

    return {
        **state,

        "selected_products": products,

        "budget_adjustment_attempts":
            state["budget_adjustment_attempts"] + 1,

        "budget_adjustment_made":
            adjustment_made
    }
# def finalize_node(state):

#     print("Finalizing plan...")

#     return state

def finalize_node(state):

    print("Finalizing plan...")

    budget_result = state["budget_result"]

    if budget_result["within_budget"]:

        budget_status = "Within budget"

    else:

        budget_status = (
            "Could not meet the requested budget "
            "with the available products."
        )

    final_plan = {
        "design_strategy":
            state["design_strategy"],

        "selected_products":
            state["selected_products"],

        "budget_result":
            budget_result,

        "budget_status":
            budget_status
    }

    return {
        **state,
        "final_plan": final_plan
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
# builder.add_conditional_edges(

#     "check_budget",

#     budget_decision,

#     {
#         "within_budget": "finalize",
#         "over_budget": "handle_over_budget"
#     }
# )

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
# builder.add_edge(
#     "handle_over_budget",
#     "finalize"
# )

# builder.add_edge(
#     "check_budget",
#     "finalize"
# )

builder.add_edge(
    "finalize",
    END
)


graph = builder.compile()