import re


def contains_email(output: str) -> bool:
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    return bool(re.search(email_pattern, output))


# Example usage
output = "My email is john.doe@example.com"
print(contains_email(output))
# Output: True
