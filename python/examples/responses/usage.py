from mirascope import llm

model = llm.use_model("openai/gpt-4o")
response = model.call("Write a haiku about programming.")

if response.usage:
    print(f"Input tokens: {response.usage.input_tokens}")
    print(f"Output tokens: {response.usage.output_tokens}")
    print(f"Total tokens: {response.usage.total_tokens}")
