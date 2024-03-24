from prompts.math_problem import ProblemSolver

problem = """
    Mira the frog ate 12 flies on Monday, half as many flies on Tuesday, 4 grasshoppers,
    on Wednesday, and on Thursday, ate 3 more flies than they did on Monday. How many
    flies did Mira eat this week?
    """

solver = ProblemSolver(problem=problem)

# response = solver.call()
# print(response.content)
# Prompt version 1 output
# > 27 flies

"""
This answer is incorrect, but LLMs work better when asked to think through problems
step by step due to their sequentially tokenized nature. Before we edit the prompt, we
can save a version of it with:
`mirascope add math_problem`
in the CLI so we can always go back to the old version if we need!
"""

# response = solver.call()
# print(response.content)
# Prompt version 2 output
# > Let's add up the flies eaten each day to find out the total number of flies Mira ate:
#   12 (Monday) + 6 (Tuesday) + 0 (Wednesday) + 15 (Thursday) = 33 flies


"""
Call the `tags` property to see which version you're using, or any other tags you wish
to add to your prompt for easy tracking:
"""
# print(solver.tags)
# > ['version:0002']


"""
If we want, we can even implement a third version where instead of using `OpenAICall`,
we use `OpenAIExtractor` to extract the solving process and solution into a Pydantic
schema!
"""
# print(solver.tags)
# > ['version:0003']
#
# print(solver.extract())
# > solving_steps='Calculate the number of flies eaten each day: ...'
#   answer=33
