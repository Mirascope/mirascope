from mirascope import llm

model = llm.use_model("anthropic/claude-sonnet-4-5", max_tokens=40)
response = model.call(messages=[llm.messages.user("Write a long story about a bear.")])

# finish_reason is None when the response completes normally
# It's set when the response was cut off or stopped abnormally
if response.finish_reason == llm.FinishReason.MAX_TOKENS:
    print("Response was truncated due to token limit")
elif response.finish_reason is None:
    print("Response completed normally")
