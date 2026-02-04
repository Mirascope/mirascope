from mirascope import llm

model = llm.retry_model("openai/gpt-4o-mini")
response = model.call("Recommend a fantasy book")
print(response.text())
# > The Name of the Wind by Patrick Rothfuss
