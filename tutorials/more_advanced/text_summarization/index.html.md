# Text Summarization

In this recipe, we show some techniques to improve an LLM’s ability to summarize a long text from simple (e.g. `"Summarize this text: {text}..."`) to more complex prompting and chaining techniques. We will use OpenAI’s GPT-4o-mini model (128k input token limit), but you can use any model you’d like to implement these summarization techniques, as long as they have a large context window.

<div class="admonition tip">
<p class="admonition-title">Mirascope Concepts Used</p>
<ul>
<li><a href="../../../learn/prompts/">Prompts</a></li>
<li><a href="../../../learn/calls/">Calls</a></li>
<li><a href="../../../learn/response_models/">Response Models</a></li>
</ul>
</div>


<div class="admonition note">
<p class="admonition-title">Background</p>
<p>
    Large Language Models (LLMs) have revolutionized text summarization by enabling more coherent and contextually aware abstractive summaries. Unlike earlier models that primarily extracted or rearranged existing sentences, LLMs can generate novel text that captures the essence of longer documents while maintaining readability and factual accuracy.

</p>
</div>

## Setup

Let's start by installing Mirascope and its dependencies:


```python
!pip install "mirascope[openai]"
```


```python
import os

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"
# Set the appropriate API key for the provider you're using
```

## Simple Call

For our examples, we’ll use the [Wikipedia article on python](https://en.wikipedia.org/wiki/Python_(programming_language)). We will be referring to this article as `wikipedia-python.txt`.

The command below will download the article to your local machine by using the `curl` command. If you don't have `curl` installed, you can download the article manually from the link above and save it as `wikipedia-python.html`.


```python
!curl "https://en.wikipedia.org/wiki/Python_(programming_language)" -o wikipedia-python.html
```

      % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                     Dload  Upload   Total   Spent    Left  Speed
    100  651k  100  651k    0     0   506k      0  0:00:01  0:00:01 --:--:--  506k


Install beautifulsoup4 to parse the HTML file.


```python
!pip install beautifulsoup4
```

We will be using a simple call as our baseline:


```python
from bs4 import BeautifulSoup
from mirascope.core import openai, prompt_template


def get_text_from_html(file_path: str) -> str:
    with open(file_path) as file:
        html_text = file.read()
    return BeautifulSoup(html_text, "html.parser").get_text()


text = get_text_from_html("wikipedia-python.html")


@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    Summarize the following text:
    {text}
    """
)
def simple_summarize_text(text: str): ...


print(simple_summarize_text(text))
```

    Python is a high-level, general-purpose programming language designed for code readability and simplicity. Created by Guido van Rossum and first released in 1991, Python supports multiple programming paradigms, including procedural, object-oriented, and functional programming. Its design emphasizes dynamic typing, garbage collection, and a comprehensive standard library, often referred to as having a "batteries included" philosophy.
    
    Key milestones in Python's history include the release of Python 2.0 in 2000 and Python 3.0 in 2008, which introduced major changes and was not fully backwards compatible with Python 2.x. The latter version aimed to improve language simplicity and efficiency, while the support for Python 2.7 officially ended in 2020.
    
    Python's unique syntax utilizes significant whitespace for block delimiters, avoids complex punctuation, and provides an intuitive style suited for beginner and expert programmers alike. 
    
    Python boasts a vast ecosystem with numerous libraries and frameworks that extend its capabilities, particularly in areas like web development, data analysis, scientific computing, and machine learning, making it a popular choice among developers globally. It is consistently ranked among the top programming languages due to its versatility and community support. The language is influenced by numerous predecessors and has significantly impacted the development of many new languages. 
    
    Recent versions have focused on performance boosts, improved error reporting, and maintaining compatibility with prior code while moving forward with enhancements. Overall, Python's design philosophy, rich features, and strong community have contributed to its widespread adoption across various domains.


LLMs excel at summarizing shorter texts, but they often struggle with longer documents, failing to capture the overall structure while sometimes including minor, irrelevant details that detract from the summary's coherence and relevance.

One simple update we can make is to improve our prompt by providing an initial outline of the text then adhere to this outline to create its summary.

# Simple Call with Outline

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
def summarize_text_with_outline(text: str): ...


print(summarize_text_with_outline(text))
```

    ### Outline
    
    1. **Introduction**
       - Overview of Python
       - Characteristics (high-level, general-purpose, dynamic typing)
       - Popularity and usage 
    
    2. **History**
       - Development by Guido van Rossum
       - Key milestones (Python 0.9.0, 2.0, 3.0)
       - Transition from Python 2 to 3
       - Release management and versions
    
    3. **Design Philosophy and Features**
       - Multi-paradigm programming language
       - Emphasis on readability and simplicity
       - The Zen of Python
       - Extensibility and modularity
       - Language clarity vs. functionality
    
    4. **Syntax and Semantics**
       - Code readability features
       - Usage of indentation for block delimitation
       - Types of statements and control flow constructs
       - Expressions and operator usage
    
    5. **Programming Examples**
       - Simple example programs demonstrating Python features
    
    6. **Libraries**
       - Overview of Python’s standard library
       - Third-party packages and Python Package Index (PyPI)
       - Use cases in various domains (web, data analysis, etc.)
    
    7. **Development Environments**
       - Integrated Development Environment (IDE) options
       - Other programming shells
    
    8. **Implementations**
       - Overview of CPython as the reference implementation
       - Other adaptations like PyPy, MicroPython, etc.
       - Cross-compilation to other languages
    
    9. **Development Process**
       - Python Enhancement Proposal (PEP) process 
       - Community input and version management
    
    10. **Popularity**
        - Rankings in programming language communities
        - Major organizations using Python
    
    11. **Uses of Python**
        - Application in web development, data science, machine learning, etc.
        - Adoption in various industries and problem domains
    
    12. **Languages Influenced by Python**
        - Overview of languages that took inspiration from Python’s design 
    
    ### Summary
    
    Python is a high-level, multi-paradigm programming language renowned for its readability and extensive standard library. Developed by Guido van Rossum, Python was first released in 1991, evolving significantly with the introduction of versions 2.0 and 3.0, transitioning away from Python 2's legacy features. 
    
    The design philosophy of Python emphasizes clarity and simplicity, captured in the guiding principles known as the Zen of Python, which advocate for beautiful, explicit, and straightforward code while also allowing for extensibility through modules. This modularity has made Python popular for adding programmable interfaces to applications.
    
    Python’s syntax is intentionally designed to enhance readability, utilizing indentation to define code blocks, a practice that differentiates it from many other languages which rely on braces or keywords. The language supports various programming constructs including statements for control flow, exception handling, and function definitions. 
    
    Moreover, Python offers a robust standard library known as "batteries included," and hosts a thriving ecosystem of third-party packages on PyPI, catering to diverse applications ranging from web development to data analytics and machine learning. 
    
    Various Integrated Development Environments (IDEs) and shells facilitate Python development, while CPython serves as the primary reference implementation, with alternatives like PyPy enhancing performance through just-in-time compilation.
    
    Development of Python is community-driven through the Python Enhancement Proposal (PEP) process, which encourages input on new features and code standards. Python consistently ranks among the most popular programming languages and is widely adopted in major industries, influencing numerous other programming languages with its design principles.


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
def summarize_text_chaining(text: str) -> openai.OpenAIDynamicConfig:
    segmented_summary = summarize_by_section(text)
    return {
        "computed_fields": {
            "outline": segmented_summary.outline,
            "summaries": segmented_summary.section_summaries,
        }
    }


print(summarize_text_chaining(text))
```

    Python was created in the late 1980s by Guido van Rossum as a successor to the ABC programming language. The first version, Python 0.9.0, was released in 1991. Major versions like Python 2.0 in 2000 and Python 3.0 in 2008 introduced significant changes. Python 2.7.18 was the last release of Python 2, while Python 3.x continues to evolve.
    
    Python is designed to emphasize code readability, using significant indentation. It supports multiple paradigms, including procedural, object-oriented, and functional programming. Its comprehensive standard library and dynamic typing are notable features.
    
    Python syntax uses indentation to define blocks, rather than curly braces or keywords. It includes various statements and control flows like assignment, if, for, while, try, except, and more. The language allows dynamic typing and has a robust set of built-in methods and operators for handling different data types.
    
    A Hello, World! program and a factorial calculation program demonstrate Python's straightforward syntax and readability. The language is known for its simplicity and ease of use, making it accessible for beginners and powerful for experienced programmers.
    
    The standard library in Python is vast, offering modules for internet protocols, string operations, web services tools, and operating system interfaces. The Python Package Index (PyPI) hosts a large collection of third-party modules for various tasks.
    
    Python supports several integrated development environments (IDEs) like PyCharm and Jupyter Notebook. It also offers basic tools like IDLE for beginners. Many advanced IDEs provide additional features like auto-completion, debugging, and syntax highlighting.
    
    CPython is the reference implementation, but there are others like PyPy, Jython, and IronPython. Variants such as MicroPython are designed for microcontrollers. Some older implementations like Unladen Swallow are no longer actively maintained.
    
    Python's development is guided by a community-driven process, primarily through Python Enhancement Proposals (PEPs). The language's development is led by the Python Software Foundation and a steering council elected by core developers.
    
    Python offers tools like Sphinx and pydoc for generating API documentation. These tools help in creating comprehensive and accessible documentation for various Python projects.
    
    Named after the British comedy group Monty Python, the language includes various playful references to the group in its documentation and culture. The term Pythonic is often used to describe idiomatic Python code.
    
    Python is highly popular, consistently ranking among the top programming languages. It is widely used by major organizations like Google, NASA, and Facebook, and has a strong presence in the scientific and data analysis communities.
    
    Python is versatile, used for web development, scientific computing, data analysis, artificial intelligence, and more. Frameworks like Django and Flask support web development, while libraries like NumPy and SciPy enable scientific research.
    
    Python has influenced many programming languages, including Julia, Swift, and Go, borrowing its design philosophy and syntax to various extents.


<div class="admonition tip">
<p class="admonition-title">Additional Real-World Applications</p>
<ul>
<li><b>Meeting Notes</b>: Convert meeting from speech-to-text then summarize the text for reference.</li>
<li><b>Education</b>: Create study guides or slides from textbook material using summaries.</li>
<li><b>Productivity</b>: Summarize email chains, slack threads, word documents for your day-to-day.</li>
</ul>
</div>

When adapting this recipe to your specific use-case, consider the following:
    - Refine your prompts to provide clear instructions and relevant context for text summarization.
    - Experiment with different model providers and version to balance quality and speed.
    - Provide a feedback loop, use an LLM to evaluate the quality of the summary based on a criteria and feed that back into the prompt for refinement.


