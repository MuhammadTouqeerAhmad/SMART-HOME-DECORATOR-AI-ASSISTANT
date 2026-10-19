from src.llm import ask_gemini


response = ask_gemini(
    "You are a home decoration assistant. "
    "Explain modern minimalist interior design "
    "in three simple sentences."
)


print(response)