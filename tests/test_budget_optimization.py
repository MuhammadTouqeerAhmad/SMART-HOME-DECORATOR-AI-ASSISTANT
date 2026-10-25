
from src.tools import calculate_budget


def test_within_budget():
    products = [
        {"id": 1, "name": "Desk lamp", "price": 3500},
        {"id": 2, "name": "Wall organizer", "price": 3000},
    ]

    result = calculate_budget(products, 10000)

    assert result["total"] == 6500
    assert result["remaining"] == 3500
    assert result["within_budget"] is True


def test_exact_budget():
    products = [
        {"id": 1, "name": "Shelf", "price": 4000},
        {"id": 2, "name": "Lamp", "price": 6000},
    ]

    result = calculate_budget(products, 10000)

    assert result["total"] == 10000
    assert result["remaining"] == 0
    assert result["within_budget"] is True


def test_over_budget():
    products = [
        {"id": 1, "name": "Lamp", "price": 7000},
        {"id": 2, "name": "Table", "price": 6500},
    ]

    result = calculate_budget(products, 10000)

    assert result["total"] == 13500
    assert result["remaining"] == -3500
    assert result["within_budget"] is False


if __name__ == "__main__":
    test_within_budget()
    test_exact_budget()
    test_over_budget()

    print("All budget calculation tests passed.")
