import logfire
from dotenv import load_dotenv
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from openai.types.chat import ChatCompletionMessageParam

from mirascope.base.prompts import tags
from mirascope.logfire import with_logfire
from mirascope.openai import OpenAICall, OpenAICallParams

logfire.configure()
load_dotenv()


# @tags(["version:0001"])
# class LeetcodeSolver(OpenAICall):
#     prompt_template = """
#     SYSTEM: You are an expert software engineer that can solve any leetcode problem.

#     Send back only the leetcode problem solution in python.

#     USER:
#     {question}
#     """

#     question: str

#     call_params = OpenAICallParams(
#         max_tokens=1000,
#         temperature=0.1,
#     )


def get_leetcode_question(url: str) -> str:
    """Given a leetcode url, return the question content."""
    transport = AIOHTTPTransport(url="https://leetcode.com/graphql")
    title_slug = url.split("/")[-1]
    client = Client(transport=transport)
    query = gql(
        """
        query questionContent($titleSlug: String!) {
            question(titleSlug: $titleSlug) {
                content
            }
        }
        """
    )
    result = client.execute(query, variable_values={"titleSlug": title_slug})
    return result["question"]["content"]


@tags(["version:0002"])
@with_logfire
class LeetcodeSolver(OpenAICall):
    prompt_template = """
    SYSTEM: You are an expert software engineer that can solve any leetcode problem.

    Send back only the leetcode problem solution in python.

    USER:
    {question}
    """

    url: str

    @property
    def question(self):
        return get_leetcode_question(self.url)

    call_params = OpenAICallParams(
        max_tokens=1000,
        temperature=0.1,
    )


leetcode_solver = LeetcodeSolver(
    url="https://leetcode.com/problems/median-of-two-sorted-arrays"
)
solution = leetcode_solver.call()
print(solution.content)


# def get_leetcode_question(url: str) -> str:
#     """Given a leetcode url, return the question content."""
#     transport = AIOHTTPTransport(url="https://leetcode.com/graphql")
#     title_slug = url.split("/")[-1]
#     client = Client(transport=transport)
#     query = gql(
#         """
#         query questionContent($titleSlug: String!) {
#             question(titleSlug: $titleSlug) {
#                 content
#             }
#         }
#         """
#     )
#     result = client.execute(query, variable_values={"titleSlug": title_slug})
#     return result["question"]["content"]


# @tags(["version:0003"])
# @with_logfire
# class CodingChallengeSolver(OpenAICall):
#     prompt_template = """
#     SYSTEM: You are an expert software engineer that can solve any coding challenge problem.

#     If the coding challenge has a link to a leetcode problem, use the provided tool to get the question content.

#     MESSAGES:
#     {history}

#     USER:
#     {question}
#     """
#     history: list[ChatCompletionMessageParam] = []
#     question: str

#     call_params = OpenAICallParams(
#         max_tokens=1000, temperature=0.1, tools=[get_leetcode_question]
#     )


# coding_challenge_solver = CodingChallengeSolver(
#     question="Can you help me solve this leetcode problem?: https://leetcode.com/problems/sudoku-solver"
# )
# response = coding_challenge_solver.call()
# coding_challenge_solver.history += [
#     {"role": "user", "content": coding_challenge_solver.question},
#     response.message.model_dump(),  # type: ignore
# ]

# tool = response.tool
# if tool:
#     print("Tool arguments:", tool.args)
#     # > {'location': 'Tokyo, Japan', 'unit': 'fahrenheit'}
#     output = tool.fn(**tool.args)
#     print("Tool output:", output)
#     # > It is 10 degrees fahrenheit in Tokyo, Japan

#     # reinsert the tool call into the chat messages through history
#     # NOTE: this should be more convenient, e.g. `tool.message_param`
#     coding_challenge_solver.history += [
#         {
#             "role": "tool",
#             "content": output,
#             "tool_call_id": tool.tool_call.id,
#             "name": tool.__class__.__name__,
#         },  # type: ignore
#     ]
#     # Set no question so there isn't a user message
#     coding_challenge_solver.question = ""
# else:
#     print(response.content)  # if no tool, print the content of the response

# # Call the LLM again with the history including the tool call
# response = coding_challenge_solver.call()
# print("After Tools Response:", response.content)
