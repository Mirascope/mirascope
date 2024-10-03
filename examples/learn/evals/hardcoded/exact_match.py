def exact_match_eval(output: str, expected: list[str]) -> bool:
    return all(phrase in output for phrase in expected)


# Example usage
output = "The capital of France is Paris, and it's known for the Eiffel Tower."
expected = ["capital of France", "Paris", "Eiffel Tower"]
result = exact_match_eval(output, expected)
print(result)  # Output: True
