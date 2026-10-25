
from src.rag import retrieve_knowledge


TEST_CASES = [
    {
        "query": "How can I make a small room appear larger using colors?",
        "expected_source": "color_theory.txt",
    },
    {
        "query": "What is the difference between ambient and task lighting?",
        "expected_source": "lighting.txt",
    },
    {
        "query": "How should I arrange furniture to maintain clear walking paths?",
        "expected_source": "furniture_placement.txt",
    },
    {
        "query": "What storage solutions are suitable for a small bedroom?",
        "expected_source": "storage.txt",
    },
    {
        "query": "What are the main characteristics of minimalist interior design?",
        "expected_source": "minimalist.txt",
    },
    {
    "query": "How do proportion, balance, and circulation affect interior design?",
    "expected_source": "design_principles.txt",
    },
]


def main():
    passed = 0

    for index, test in enumerate(TEST_CASES, start=1):
        print(f"\n{'=' * 65}")
        print(f"TEST {index}: {test['query']}")
        print("=" * 65)

        results = retrieve_knowledge(
            test["query"],
            top_k=3,
        )

        sources = [item["source"] for item in results]

        print("Retrieved sources:", sources)

        success = test["expected_source"] in sources

        if success:
            passed += 1
            print("RESULT: PASS")
        else:
            print(
                "RESULT: FAIL — expected source not found:",
                test["expected_source"],
            )

    print(f"\nEvaluation: {passed}/{len(TEST_CASES)} tests passed.")


if __name__ == "__main__":
    main()
