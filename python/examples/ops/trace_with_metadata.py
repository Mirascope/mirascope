from mirascope import ops


@ops.trace(tags=["production", "ml-pipeline"], metadata={"version": "1.0"})
def analyze_sentiment(text: str) -> str:
    # Sentiment analysis logic here
    return "positive" if "good" in text.lower() else "neutral"


trace = analyze_sentiment.wrapped("This product is really good!")
print(trace.result)  # "positive"
