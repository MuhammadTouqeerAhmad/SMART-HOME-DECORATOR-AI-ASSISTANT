# def calculate_budget(items):

#     total = 0

#     for item in items:

#         total += item["price"]

#     return {
#         "total": total,
#         "items": items
#     }

# import json


# def search_products(
#     category=None,
#     style=None
# ):

#     with open(
#         "data/products/products.json",
#         "r",
#         encoding="utf-8"
#     ) as file:

#         products = json.load(file)


#     results = []

#     for product in products:

#         if category:

#             if product["category"] != category:
#                 continue

#         if style:

#             if style.lower() not in [
#                 s.lower()
#                 for s in product["styles"]
#             ]:
#                 continue

#         results.append(product)

#     return results

import json


PRODUCT_FILE = (
    "data/products/products.json"
)


def load_products():

    with open(
        PRODUCT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# def search_products(
#     category=None,
#     style=None
# ):

#     products = load_products()

#     results = []


#     for product in products:

#         if category:

#             if product["category"] != category:

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

def search_products(
    category=None,
    style=None
):
    products = load_products()

    results = []

    for product in products:

        if category:

            if product["category"].lower() != category.lower():
                continue

        if style:

            product_styles = [
                item.lower()
                for item in product["styles"]
            ]

            if style.lower() not in product_styles:
                continue

        results.append(product)

    return results




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

#         if matches:
#             selected.append(
#                 matches[0]
#             )

#     return selected
def select_products(
    categories,
    style
):
    products = load_products()

    selected = []

    for category in categories:

        matches = search_products(
            category=category,
            style=style
        )

        if not matches:
            continue

        # Choose the cheapest suitable product
        best_product = min(
            matches,
            key=lambda item: item["price"]
        )

        selected.append(
            best_product
        )

    return selected

def find_cheaper_alternative(
    product,
    style=None,
    max_price=None
):
    products = load_products()

    alternatives = []

    for candidate in products:

        # Do not select the same product
        if candidate["id"] == product["id"]:
            continue

        # Prefer the same category
        if candidate["category"] != product["category"]:
            continue

        # Respect the preferred style
        if style:
            candidate_styles = [
                item.lower()
                for item in candidate["styles"]
            ]

            if style.lower() not in candidate_styles:
                continue

        # Candidate must actually be cheaper
        if candidate["price"] >= product["price"]:
            continue

        # Optional maximum price
        if max_price is not None:
            if candidate["price"] > max_price:
                continue

        alternatives.append(candidate)

    # Cheapest suitable alternative
    alternatives.sort(
        key=lambda item: item["price"]
    )

    if alternatives:
        return alternatives[0]

    return None

# def calculate_budget(items):

#     total = sum(
#         item["price"]
#         for item in items
#     )

#     return {
#         "items": items,
#         "total": total
#     }

def calculate_budget(
    items,
    budget
):
    total = sum(
        item["price"]
        for item in items
    )

    remaining = budget - total

    return {
        "items": items,
        "total": total,
        "budget": budget,
        "remaining": remaining,
        "within_budget": total <= budget
    }