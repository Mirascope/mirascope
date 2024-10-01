from pydantic import BaseModel, Field

from mirascope.core import openai, prompt_template


class RelevantContext(BaseModel):
    context_text: str = Field(
        description="""Context text related to the question\
            (includes all content except unrelated sentences)"""
    )
    detailed_question: str = Field(description="Detailed question:")


@openai.call(model="gpt-4o-mini", response_model=RelevantContext)
@prompt_template(
    """
    Given the following text by a user, extract the part that is related and useful,
    so that using that text alone would be good context for providing an accurate and
    correct answer to the question portion of the text. Please include the actual
    question or query that the user is asking. Separate this into two categories
    labeled with ”Context text related to the question (includes all content except
    unrelated sentences):” and ”Detailed question:”. Do not use list.
    Text by User: {query}
    """
)
def remove_irrelevant_info(query: str):
    """Reduces a query down to its relevant context and question"""


@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    Original user query (possibly biased): {query}
    Unbiased context: {context_text}
    Given the above unbiased context, answer the following: {detailed_question}
    """
)
def s2a(query: str) -> openai.OpenAIDynamicConfig:
    """Executes the flow of the System to Attention technique."""
    relevant_context = remove_irrelevant_info(query=query)
    # Uncomment to see intermediate responses
    # print(relevant_context)
    context_text = relevant_context.context_text
    detailed_question = relevant_context.detailed_question
    return {
        "computed_fields": {
            "context_text": context_text,
            "detailed_question": detailed_question,
        }
    }


query = """Sunnyvale is a city in California.
Sunnyvale has many parks. Sunnyvale city is
close to the mountains. Many notable people
are born in Sunnyvale.
In which city was San Jose’s mayor Sam
Liccardo born?"""

print(s2a(query=query))
# > Sam Liccardo, the mayor of San Jose, was born in San Jose, California.


# Intermediate Responses

# relevant_context = remove_irrelevant_info(query=query)
# > context_text='Sunnyvale is a city in California.\nSunnyvale has many parks. Sunnyvale city is close to the mountains. Many notable people are born in Sunnyvale.' detailed_question='In which city was San Jose’s mayor Sam Liccardo born?'
