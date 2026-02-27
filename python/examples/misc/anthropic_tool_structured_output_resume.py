from mirascope import llm


@llm.call("anthropic/claude-sonnet-4-5", format=int)
def lucky_number():
    return "Choose a lucky number between 1 and 10"


result = lucky_number()
second_result = result.resume("Ok, now choose a different lucky number")
