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



def select_products(
    categories,
    style,
    keywords_by_category=None,
    max_products_per_category=2,
    max_price=None,
    exclude_ids=None,
):
    """
    Select relevant products without duplicates.

    Products with more keyword matches rank first.
    Cheaper products rank first when relevance is tied.

    Args:
        categories: Product categories to search.
        style: Preferred interior design style.
        keywords_by_category: Relevant keywords per category.
        max_products_per_category: Maximum products per category.
        max_price: Optional maximum price per product.
        exclude_ids: Product IDs already selected elsewhere.
    """
    selected = []
    selected_ids = set(exclude_ids or [])
    keywords_by_category = keywords_by_category or {}

    for category in categories:
        matches = search_products(
            category=category,
            style=style,
        )

        keywords = keywords_by_category.get(
            category.lower(), []
        )

        if max_price is not None:
            matches = [
                product for product in matches
                if float(product["price"]) <= float(max_price)
            ]

        matches.sort(
            key=lambda product: (
                -_relevance_score(product, keywords),
                float(product["price"]),
            )
        )

        category_count = 0

        for product in matches:
            product_id = product["id"]

            if product_id in selected_ids:
                continue

            selected.append(product)
            selected_ids.add(product_id)
            category_count += 1

            if category_count >= max_products_per_category:
                break

    return selected



def find_cheaper_alternative(
    product,
    style=None,
    exclude_ids=None,
):
    """
    Find a cheaper product in the same category
    without selecting a duplicate.
    """
    exclude_ids = set(exclude_ids or [])
    products = load_products()

    current_price = float(product["price"])
    current_category = str(
        product.get("category", "")
    ).lower()

    candidates = []

    for candidate in products:
        candidate_id = candidate["id"]

        if candidate_id in exclude_ids:
            continue

        if candidate_id == product["id"]:
            continue

        if str(candidate.get("category", "")).lower() != current_category:
            continue

        candidate_price = float(candidate["price"])

        if candidate_price >= current_price:
            continue

        candidate_styles = [
            item.lower()
            for item in candidate.get("styles", [])
        ]

        if style and style.lower() not in candidate_styles:
            continue

        candidates.append(candidate)

    if not candidates:
        return None

    return min(
        candidates,
        key=lambda item: float(item["price"]),
    )




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
