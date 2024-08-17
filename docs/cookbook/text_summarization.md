# Text Summarization

In this recipe, we show some techniques to improve an LLM’s ability to summarize a long text from simple (e.g. `"Summarize this text: {text}..."`) to more complex prompting and chaining techniques. We will use OpenAI’s GPT-4o-mini model (128k input token limit), but you can use any model you’d like to implement these summarization techniques, as long as they have a large context window.

??? tip "Mirascope Concepts Used"

    - [Calls](../learn/calls.md)
    - [Chaining](../learn/chaining.md)
    - [Response Model](../learn/response_models.md)

!!! note "Background"

    Large Language Models (LLMs) have revolutionized text summarization by enabling more coherent and contextually aware abstractive summaries. Unlike earlier models that primarily extracted or rearranged existing sentences, LLMs can generate novel text that captures the essence of longer documents while maintaining readability and factual accuracy.

## Simple Call

For our examples, we’ll use the [Wikipedia article on python](https://en.wikipedia.org/wiki/Python_(programming_language)). We will be referring to this article as `wikipedia-python.txt`.

We will be using a simple call as our baseline:

```python
from mirascope.core import openai, prompt_template

text = ""
with open("wikipedia-python.txt") as file:
    text = file.read()

@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    Summarize the following text:
    {text}
    """
)
def summarize_text(text: str): ...


print(summarize_text(text))
# > Python is a versatile, high-level programming language known for its emphasis 
#   on readability and simplicity, using significant indentation for code blocks. 
#   Created in the late 1980s by Guido van Rossum and first released in 1991, Python 
#   has evolved through various significant versions, including Python 2.0 in 2000 
#   and Python 3.0 in 2008, the latter being a major revision with backward 
#   incompatibility. Python supports multiple programming paradigms, including 
#   procedural, object-oriented, and functional programming, and is celebrated for 
#   its extensive standard library.
#
#   Python employs dynamic typing and garbage collection and has been widely 
#   adopted in fields like machine learning, scientific computing, and web 
#   development. It includes numerous frameworks (e.g., Django, Flask), libraries 
#   (e.g., NumPy, SciPy), and tools for tasks ranging from numerical data 
#   manipulation to artificial intelligence.
#
#   The language's design philosophy is characterized by the "Zen of Python," which 
#   promotes principles like simplicity and explicitness while allowing for 
#   extensibility through modules. Python's community-driven development is 
#   facilitated through a process called Python Enhancement Proposal (PEP), ensuring 
#   contributions from its user base.
#
#   Despite its advantages, Python has faced criticism for performance compared to 
#   other languages, but various implementations (like CPython and PyPy) have been 
#   developed to address these concerns, with advancements in runtime efficiency. 
#   Python's popularity continues to grow, being ranked among the top programming 
#   languages globally, and is used by major organizations in various applications. 
#   The language embraces fun in programming culture, as evidenced by its name, 
#   inspired by the comedy group Monty Python.
```

LLMs excel at summarizing shorter texts, but they often struggle with longer documents, failing to capture the overall structure while sometimes including minor, irrelevant details that detract from the summary's coherence and relevance.

One simple update we can make is to improve our prompt by providing an initial outline of the text then adhere to this outline to create its summary.

## Simple Call with Outline

This prompt engineering technique is an example of [Chain of Thought](https://www.promptingguide.ai/techniques/cot) (CoT), forcing the model to write out its thinking process. It also involves little work and can be done by modifying the text of the single call. With an outline, the summary is less likely to lose the general structure of the text.

```python
@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    Summarize the following text by first creating an outline with a nested structure,
    listing all major topics in the text with subpoints for each of the major points.
    The number of subpoints for each topic should correspond to the length and
    importance of the major point within the text. Then create the actual summary using
    the outline.
    {text}
    """
)
def summarize_text(text: str): ...


print(summarize_text(text))
# > ## Outline
#   
#   ### I. Introduction to Python
#      - A. Definition
#      - B. Design Philosophy
#      - C. Features
#        1. Dynamic typing
#        2. Garbage collection
#        3. Multi-paradigm support
#   
#   ### II. History and Development
#      - A. Origin
#        1. Creator: Guido van Rossum
#        2. ABC programming language as predecessor
#      - B. Major Releases
#        1. Initial release and features
#        2. Python 2.0 (2000)
#        3. Python 3.0 (2008)
#        4. End of Python 2
#      - C. Evolution of Leadership
#        1. Van Rossum’s role
#        2. Transition to Steering Council
#   
#   ### III. Popularity and Usage
#      - A. Current ranking
#      - B. Communities and Industries
#      - C. Common applications
#        1. Web development
#        2. Scientific computing
#        3. Machine learning and AI
#   
#   ### IV. Programming Paradigms and Features
#      - A. Multi-paradigm support
#      - B. Syntax specificities
#        1. Readability and whitespace
#        2. Dynamic typing
#   
#   ### V. Language Constructs
#      - A. Statements
#      - B. Expressions
#      - C. Methods and Functions
#      - D. Error handling and exceptions
#   
#   ### VI. Libraries and Frameworks
#      - A. Standard Library
#      - B. Third-party Libraries
#        1. PyPI
#        2. Popular libraries for various domains
#   
#   ### VII. Implementations and Performance
#      - A. CPython
#      - B. Alternative implementations
#        1. PyPy
#        2. MicroPython
#        3. Others (Cython, Numba, etc.)
#      - C. Performance considerations
#   
#   ### VIII. Development and Community
#      - A. PEP process
#      - B. Community engagement
#      - C. Major conferences
#   
#   ### IX. Impact on Other Languages
#      - A. Influence on new languages
#      - B. Language design philosophies
#   
#   ### X. Tools and IDEs
#      - A. Integrated development environments
#      - B. REPL and other shells
#   
#   ### XI. Conclusion
#      - A. Summary of Python’s significance
#      - B. Future of Python
#   
#   ---
#   
#   ## Summary
#
#   Python is a versatile, high-level programming language with a strong emphasis
#   on code readability, characterized by significant indentation. It supports
#   dynamic typing and is made to be usable across multiple programming paradigms,
#   including procedural, object-oriented, and functional programming. Its
#   comprehensive standard library contributes to its reputation as a "batteries
#   included" language.
#
#   Developed by Guido van Rossum in the late 1980s to serve as a successor to
#   the ABC programming language, Python's first version was released in 1991,
#   followed by Python 2.0 in 2000 and the non-backward-compatible Python 3.0 in
#   2008. Python 2 reached its end of life in 2020, and since then, Python has
#   evolved under the guidance of a Steering Council elected by active developers.
#
#   Python ranks among the top programming languages globally, finding
#   applications in various sectors like web development, scientific computing,
#   and machine learning. Its syntax promotes readability, using whitespace to
#   define code blocks, which contrasts with many other languages that rely on
#   punctuation.
#
#   The language includes various constructs such as assignment statements,
#   control flow statements, and exception handling, allowing for comprehensive
#   programming capabilities. The standard library is extensive, and the Python
#   Package Index (PyPI) houses over 523,000 third-party packages, extending
#   Python’s functionality.
#
#   CPython is the reference implementation of Python, but there are alternative
#   implementations like PyPy, which enhances performance through just-in-time
#   compilation. The language’s development is managed through the Python
#   Enhancement Proposal (PEP) process, fostering community engagement and
#   refinement of the language.
#
#   Python's design has influenced numerous other programming languages,
#   incorporating its philosophies into their syntax and structure. Integrated
#   development environments such as IDLE and various other shells enhance the
#   coding experience, contributing to Python's widespread appeal.
#
#   In conclusion, Python’s user-friendly design and extensive capabilities
#   continue to place it at the forefront of programming languages, making it a
#   significant tool for developers and a staple of the programming community.
```

By providing an outline, we enable the LLM to better adhere to the original article's structure, resulting in a more coherent and representative summary.

For our next iteration, we'll explore segmenting the document by topic, requesting summaries for each section, and then composing a comprehensive summary using both the outline and these individual segment summaries.

## Segment then Summarize

This more comprehensive approach not only ensures that the model adheres to the original text's structure but also naturally produces a summary whose length is proportional to the source document, as we combine summaries from each subtopic.

To apply this technique, we create a `SegmentedSummary` Pydantic `BaseModel` to contain the outline and section summaries, and extract it in a chained call from the original summarize_text() call:

```python
from pydantic import BaseModel, Field


class SegmentedSummary(BaseModel):
    outline: str = Field(
        ...,
        description="A high level outline of major sections by topic in the text",
    )
    section_summaries: list[str] = Field(
        ..., description="A list of detailed summaries for each section in the outline"
    )


@openai.call(model="gpt-4o", response_model=SegmentedSummary)
@prompt_template(
    """
    Extract a high level outline and summary for each section of the following text:
    {text}
    """
)
def summarize_by_section(text): ...


@openai.call(model="gpt-4o")
@prompt_template(
    """
    The following contains a high level outline of a text along with summaries of a
    text that has been segmented by topic. Create a composite, larger summary by putting
    together the summaries according to the outline.
    Outline:
    {outline}

    Summaries:
    {summaries}
    """
)
def summarize_text(text: str) -> openai.OpenAIDynamicConfig:
    segmented_summary = summarize_by_section(text)
    return {
        "computed_fields": {
            "outline": segmented_summary.outline,
            "summaries": segmented_summary.section_summaries,
        }
    }


print(summarize_text(text))
# > Python is a high-level, general-purpose programming language designed for
#   code readability and simplicity. It supports various programming paradigms 
#   and is known for its comprehensive standard library. Python's design 
#   philosophy emphasizes readability and simplicity, aligning with the Zen of 
#   Python principles. Created by Guido van Rossum in the late 1980s, Python has 
#   undergone significant development, including major versions Python 2 and 
#   Python 3.
#   
#   Python supports multiple paradigms such as object-oriented, structured, 
#   functional, and aspect-oriented programming. It offers support for dynamic 
#   typing, memory management, and late binding. Key features of Python include 
#   dynamic typing, reference counting, cycle-detecting garbage collection, and 
#   a robust standard library, all contributing to its readability and efficiency.
#   
#   Python is widely used and consistently ranks among the top programming 
#   languages. It has a large community and is particularly popular in scientific
#    computing, web development, and artificial intelligence. Various Python 
#   implementations like CPython, PyPy, and Jython exist to cater to different 
#   performance needs, with enhancements achievable through JIT compilers, 
#   extensions, and alternative implementations.
#   
#   The syntax of Python is clean and straightforward, making it accessible to 
#   both novice and experienced programmers. Python uses indentation to define 
#   code blocks and supports a comprehensive range of statements and expressions, 
#   emphasizing simplicity and readability.
#   
#   A significant advantage of Python is its extensive standard library, which 
#   supports numerous tasks, along with a vast repository of third-party packages 
#   hosted on PyPI. This versatility and adaptability enable Python to be used 
#   in diverse domains including web development, scientific computing, 
#   artificial intelligence, and more. Python's wide range of applications also 
#   includes being embedded in software products and having support across many 
#   operating systems.
#   
#   Python has not only established itself as a versatile language but also 
#   influenced many others with its design philosophy and syntax. Languages 
#   like Ruby, Julia, and Go have drawn inspiration from Python in various 
#   aspects, showcasing its broad impact on the programming landscape.
```

!!! tip "Additional Real-World Applications"
    - **Meeting Notes**: Convert meeting from speech-to-text then summarize the text for reference.
    - **Education**: Create study guides or slides from textbook material using summaries.
    - **Productivity**: Summarize email chains, slack threads, word documents for your day-to-day.

When adapting this recipe to your specific use-case, consider the following:
    - Refine your prompts to provide clear instructions and relevant context for text summarization.
    - Experiment with different model providers and version to balance quality and speed.
    - Provide a feedback loop, use an LLM to evaluate the quality of the summary based on a criteria and feed that back into the prompt for refinement.

