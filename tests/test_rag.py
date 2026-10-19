# from src.rag import (
#     build_knowledge_base,
#     retrieve_knowledge
# )


# print(
#     "Building knowledge base..."
# )


# count = build_knowledge_base()


# print(
#     f"Indexed {count} chunks."
# )


# print(
#     "\nSearching knowledge base...\n"
# )


# results = retrieve_knowledge(

#     "I have a small minimalist bedroom "
#     "and need more storage and better "
#     "lighting."
# )


# for index, result in enumerate(
#     results,
#     start=1
# ):

#     print(
#         f"\n--- Result {index} ---"
#     )

#     print(
#         f"Source: {result['source']}"
#     )

#     print(
#         result["content"]
#     )

from src.rag import (
    build_knowledge_base,
    retrieve_knowledge
)


print("Building knowledge base...")

count = build_knowledge_base()

print(
    f"Knowledge base built with {count} chunks."
)


print("\nTesting retrieval...")

query = """
Small minimalist bedroom with limited natural light,
limited storage, a study table, and a low budget.
Need better lighting and additional storage.
"""

results = retrieve_knowledge(
    query,
    top_k=6
)


print("\nRetrieved knowledge:\n")

for index, result in enumerate(
    results,
    start=1
):

    print(
        f"\n--- Result {index} ---"
    )

    print(
        f"Source: {result['source']}"
    )

    print(
        f"Category: {result['category']}"
    )

    print(
        result["content"]
    )