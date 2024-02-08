# SQuAD 2.0: Extracting Answers To Questions From Context Using Mirascope

The SQuAD 2.0 Dataset is a dataset for question-answering. Each question is either impossible to answer given the context paragraph or has answers exactly as written in the paragraph. It turns out that it's quite difficult to get an LLM to ignore it's world knowledge and output "<No Answer>" if the paragraph does not contain the answer. For this recipe, we'll be using a modified version of the dataset, restricting our questions to a single article (Geology) and removing all of the impossible questions.

!!! note

    The [`geology-squad.json`](https://raw.githubusercontent.com/Mirascope/datasets/main/geology-squad.json) modified version of the dataset is on our GitHub along with the [full code](https://github.com/Mirascope/mirascope/tree/main/cookbook/extraction_examples/squad_extraction) for this recipe.

The first step is loading the dataset. We've written a helper function `load_geology_squad` that will load and return a `list[QuestionWithContext]`, defined below:

```python
from pydantic import BaseModel

class QuestionWithContext(BaseModel):
    """A question with it's answers and context."""

    id: str
    question: str
    context: str
    answers: list[str]
```

## Initial Basic Extraction

To extract an answer to a question, we can use the [`OpenAIChat.extract`](../api/chat/models/openai_chat.md/#mirascope.chat.models.OpenAIChat.extract) method to extract the answer. First, let's create a super basic schema and prompt for asking the question and extracting an answer:

```shell
$ mirascope init; touch prompts/question.py
```

```python
# prompts/question.py
from mirascope import Prompt
from pydantic import BaseModel, Field


class ExtractedAnswer(BaseModel):
    """The anwer to a question about a paragraph of text."""

    answer: str


class QuestionPrompt(Prompt):
    """
    Paragraph: {paragraph}

    Question: {question}
    """

    paragraph: str
    question: str
```

Next we'll define the schema we want to extract from the paragraph and a function to extract the schema from a given question:

```python
from pydantic import BaseModel

from config import Settings
from prompts.question import ExtractedAnswer, QuestionPrompt

settings = Settings()
chat = OpenAIChat(model="gpt-3.5-turbo-1106", api_key=settings.openai_api_key)


def extract_answer(question: QuestionWithContext) -> str:
    """Returns the extracted `str` answer to `question`."""
    return chat.extract(
        ExtractedAnswer,
        QuestionPrompt(paragraph=question.context, question=question.question),
        retries=2,  # retry up to 2 more times on validation error
    ).answer
```

Now we just need to load the data and extract our answers:

```python
import json

from squad import load_geology_squad

extracted_answers = {
    question.id: extract_answer(question)
    for question in load_geology_squad()
}
with open("geology-squad-answers-v1.json", "w") as f:
    json.dump(extracted_answers, f)
```

Running the included modified version of the SQuAD eval script gives us the following breakdown on metrics, which we can use to see how well our system is working:

```shell
$ python eval.py geology-squad.json geology-squad-answers-v1.json
```

```
{
  "exact": 79.3103448275862,
  "f1": 89.4777077966733,
  "total": 116,
}
```

Exact match is determined with a raw string match, whereas F1 score is calculated by token to account for partial matches. With our simple script, we were able to get nearly 80% exact match and an F1 score of nearly 90 on our 116 examples. Before we move on, let's include this metadata in the docstring of our prompt file and version it with the CLI:

```shell
$ mirascope add question
```

## Engineering A Better Prompt By Analyzing Results In Oxen

Now let's make the script even better. To better understand where our LLM is making mistakes, we can upload a transformed version of our data to [Oxen](https://oxen.ai) and dig around a little.

!!! note

    The [`push_to_oxen.py`](https://github.com/Mirascope/mirascope/tree/main/cookbook/extraction_examples/squad_extraction/push_to_oxen.py) script shows how we upload each prompt version's answer for analysis.

[INSERT IMAGE HERE]

Two things stick out immediately about the extracted answers:

1. Often long or a full sentence instead of a short, concise answer.
2. Not an exact match with the context paragraph.

Let's update our schema and our prompt so that the LLM tries to extract more concise answers that better match the context paragraph:

```python
from mirascope import Prompt, messages

from pydantic import BaseModel

class ExtractedAnswer(BaseModel):
    """The answer to a question about a paragraph of text."""

    answer: str = Field(
        ...,
        description=(
            "The extracted answer to the question. This answer is as concise "
            "as possible, most often just a single word. It is also an exact "
            "text match with text in the provided context."
        ),
    )


@messages
class QuestionPrompt(Prompt):
    """
    SYSTEM:
    You will be asked a question after you read a paragraph. Your task is to
    answer the question based on the information in the paragraph. Your answer
    should be an exact text match to text from the paragraph. Your answer should
    also be one or two words at most is possible.

    USER:
    Paragraph: {paragraph}

    USER:
    Question: {question}
    """

    paragraph: str
    question: str
```

```shell
$ python extract_answers.py v2
$ python eval.py geology-squad.json geology-squad-answers-v2.json
```

```
{
  "exact": 85.34482758620689,
  "f1": 91.55579573683022,
  "total": 116,
}
```

```shell
$ mirascope add question
```

So just by updating our schema and prompt we've improved the performance of the extraction script by ~6% for exact match and ~1% for F1. We can see in Oxen that there are far fewer incorrect extracted answers:

[INSERT IMAGE HERE]
