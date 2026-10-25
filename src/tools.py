# import json


# PRODUCT_FILE = (
#     "data/products/products.json"
# )


# def load_products():

#     with open(
#         PRODUCT_FILE,
#         "r",
#         encoding="utf-8"
#     ) as file:

#         return json.load(file)

# def search_products(
#     category=None,
#     style=None
# ):
#     products = load_products()

#     results = []

#     for product in products:

#         if category:

#             if product["category"].lower() != category.lower():
#                 continue

#         if style:

#             product_styles = [
#                 item.lower()
#                 for item in product["styles"]
#             ]

#             if style.lower() not in product_styles:
#                 continue

#         results.append(product)

#     return results

# def select_products(
#     categories,
#     style
# ):
#     products = load_products()

#     selected = []

#     for category in categories:

#         matches = search_products(
#             category=category,
#             style=style
#         )

#         if not matches:
#             continue

#         # Choose the cheapest suitable product
#         best_product = min(
#             matches,
#             key=lambda item: item["price"]
#         )

#         selected.append(
#             best_product
#         )

#     return selected

# def find_cheaper_alternative(
#     product,
#     style=None,
#     max_price=None
# ):
#     products = load_products()

#     alternatives = []

#     for candidate in products:

#         # Do not select the same product
#         if candidate["id"] == product["id"]:
#             continue

#         # Prefer the same category
#         if candidate["category"] != product["category"]:
#             continue

#         # Respect the preferred style
#         if style:
#             candidate_styles = [
#                 item.lower()
#                 for item in candidate["styles"]
#             ]

#             if style.lower() not in candidate_styles:
#                 continue

#         # Candidate must actually be cheaper
#         if candidate["price"] >= product["price"]:
#             continue

#         # Optional maximum price
#         if max_price is not None:
#             if candidate["price"] > max_price:
#                 continue

#         alternatives.append(candidate)

#     # Cheapest suitable alternative
#     alternatives.sort(
#         key=lambda item: item["price"]
#     )

#     if alternatives:
#         return alternatives[0]

#     return None

# def calculate_budget(
#     items,
#     budget
# ):
#     total = sum(
#         item["price"]
#         for item in items
#     )

#     remaining = budget - total

#     return {
#         "items": items,
#         "total": total,
#         "budget": budget,
#         "remaining": remaining,
#         "within_budget": total <= budget
#     }


import json
from pathlib import Path


# Resolve the product file relative to the project root.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PRODUCT_FILE = PROJECT_ROOT / "data" / "products" / "products.json"


def load_products():
    with open(PRODUCT_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def search_products(category=None, style=None):
    products = load_products()
    results = []

    for product in products:
        if category:
            if product["category"].lower() != category.lower():
                continue

        if style:
            product_styles = [
                item.lower() for item in product["styles"]
            ]

            if style.lower() not in product_styles:
                continue

        results.append(product)

    return results


def _relevance_score(product, keywords):
    """
    Give a product a score based on keyword matches
    in its name, category, and description.
    """
    if not keywords:
        return 0

    searchable_text = " ".join([
        product.get("name", ""),
        product.get("category", ""),
        product.get("description", ""),
        " ".join(product.get("styles", []))
    ]).lower()

    score = 0

    for keyword in keywords:
        keyword = keyword.lower().strip()

        if keyword and keyword in searchable_text:
            score += 1

    return score


# def select_products(
#     categories,
#     style,
#     keywords_by_category=None
# ):
#     """
#     Select one suitable product per category.

#     Products with more relevant keyword matches rank first.
#     If relevance is tied, the cheaper product ranks first.

#     Existing calls using only categories and style still work.
#     """
#     selected = []
#     selected_ids = set()
#     keywords_by_category = keywords_by_category or {}

#     for category in categories:
#         matches = search_products(
#             category=category,
#             style=style
#         )

#         if not matches:
#             continue

#         keywords = keywords_by_category.get(
#             category.lower(), []
#         )

#         # Most relevant first, then cheapest.
#         matches.sort(
#             key=lambda product: (
#                 -_relevance_score(product, keywords),
#                 product["price"]
#             )
#         )

#         best_product = next(
#             (
#                 product
#                 for product in matches
#                 if product["id"] not in selected_ids
#             ),
#             None
#         )

#         if best_product:
#             selected.append(best_product)
#             selected_ids.add(best_product["id"])

#     return selected


def select_products(
    categories,
    style,
    keywords_by_category=None,
    max_products_per_category=2,
    max_price=None,
):
    """
    Select multiple relevant products per category.

    Products with more keyword matches rank first.
    Cheaper products rank first when relevance is tied.

    Args:
        categories: Product categories to search.
        style: Preferred interior design style.
        keywords_by_category: Relevant keywords per category.
        max_products_per_category: Maximum products per category.
        max_price: Optional maximum price for each selected product.
    """
    selected = []
    selected_ids = set()
    keywords_by_category = keywords_by_category or {}

    for category in categories:
        matches = search_products(
            category=category,
            style=style
        )

        if not matches:
            continue

        keywords = keywords_by_category.get(
            category.lower(), []
        )

        # Keep products within the optional per-product price limit.
        if max_price is not None:
            matches = [
                product for product in matches
                if float(product["price"]) <= float(max_price)
            ]

        # Most relevant first, then cheapest.
        matches.sort(
            key=lambda product: (
                -_relevance_score(product, keywords),
                float(product["price"])
            )
        )

        category_count = 0

        for product in matches:
            if product["id"] in selected_ids:
                continue

            selected.append(product)
            selected_ids.add(product["id"])
            category_count += 1

            if category_count >= max_products_per_category:
                break

    return selected



# def find_cheaper_alternative(
#     product,
#     style=None,
#     max_price=None
# ):
#     products = load_products()
#     alternatives = []

#     for candidate in products:
#         if candidate["id"] == product["id"]:
#             continue

#         if candidate["category"].lower() != product["category"].lower():
#             continue

#         if style:
#             candidate_styles = [
#                 item.lower() for item in candidate["styles"]
#             ]

#             if style.lower() not in candidate_styles:
#                 continue

#         if candidate["price"] >= product["price"]:
#             continue

#         if max_price is not None and candidate["price"] > max_price:
#             continue

#         alternatives.append(candidate)

#     alternatives.sort(key=lambda item: item["price"])

#     return alternatives[0] if alternatives else None

def find_cheaper_alternative(
    product,
    style=None,
    max_price=None
):
    products = load_products()
    alternatives = []

    for candidate in products:
        if candidate["id"] == product["id"]:
            continue

        if candidate["category"].lower() != product["category"].lower():
            continue

        if style:
            candidate_styles = [
                item.lower() for item in candidate["styles"]
            ]

            if style.lower() not in candidate_styles:
                continue

        if candidate["price"] >= product["price"]:
            continue

        if max_price is not None and candidate["price"] > max_price:
            continue

        alternatives.append(candidate)

    alternatives.sort(key=lambda item: item["price"])

    return alternatives[0] if alternatives else None


def calculate_budget(items, budget):
    total = sum(item["price"] for item in items)
    remaining = budget - total

    return {
        "items": items,
        "total": total,
        "budget": budget,
        "remaining": remaining,
        "within_budget": total <= budget
    }
