import re


def regex_eval(output: str, pattern: str) -> bool:
    return bool(re.search(pattern, output))


# Example usage
output = "My email is john.doe@example.com"
email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
result = regex_eval(output, email_pattern)
print(result)  # Output: True
