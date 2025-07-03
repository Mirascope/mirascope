from mirascope import llm


@llm.call("openai:gpt-4o-mini")
def detailed_recommendation(genre: str, years: int, age_group: str) -> str:
    return f"""
    Please recommend a {genre} book that meets the following criteria:
    
    - Published within the last {years} years
    - Suitable for {age_group} readers
    - Has received critical acclaim or awards
    
    Please include a brief summary and explain why you chose this particular book.
    """
