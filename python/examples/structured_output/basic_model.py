from mirascope import llm

model = llm.Model("openai/gpt-4o-mini")
response = model.call("List 3 fantasy books.", format=list[str])
books = response.parse()
print(books)
# ['The Name of the Wind', 'Mistborn', 'The Way of Kings']
