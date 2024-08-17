# Output Parsers

Output Parsers in Mirascope provide a flexible way to process and structure the raw output from Large Language Models (LLMs). They allow you to transform the LLM's response into a more usable format, enabling easier integration with your application logic and improving the overall reliability of your LLM-powered features.

## How Output Parsers Work

Output Parsers are functions that take the call response object as input and return an output of a specified type. When you supply an output parser to a `call` decorator, it modifies the return type of the decorated function to match the output type of the parser.

Here's a basic example of how to use an Output Parser:

```python
from mirascope.core import anthropic, prompt_template
from pydantic import BaseModel


class Book(BaseModel):
    title: str
    author: str


def parse_book_recommendation(response: anthropic.AnthropicCallResponse) -> Book:
    title, author = response.content.split(" by ")
    return Book(title=title, author=author)


@anthropic.call(
    model="claude-3-5-sonnet-20240620", output_parser=parse_book_recommendation
)
@prompt_template("Recommend a {genre} book in the format Title by Author")
def recommend_book(genre: str):
    ...


book = recommend_book("science fiction")
print(f"Title: {book.title}")
print(f"Author: {book.author}")
```

In this example, the `parse_book_recommendation` function serves as an Output Parser, transforming the raw response into a structured `Book` instance.

### Type Safety and Proper Hints

When using output parsers with Mirascope's call decorator, you benefit from accurate type hints that reflect the parser's output type.

In the above example, your IDE will recognize `book` as a `Book` instance, providing appropriate autocompletion and type checking. This enhances code reliability and helps catch potential type-related errors early in the development process.

## Custom XML Parser for Anthropic Claude

Some LLMs handle particular structure requests quite well. For example, Anthropic's Claude model is particularly adept at handling XML structures. Let's create a more complex example using a custom XML parser:

```python
import xml.etree.ElementTree as ET

from mirascope.core import anthropic, prompt_template
from pydantic import BaseModel


class Book(BaseModel):
    title: str
    author: str
    year: int
    summary: str


def parse_book_xml(response: anthropic.AnthropicCallResponse) -> Book | None:
    try:
        root = ET.fromstring(response.content)
        if (node := root.find("title")) is None or not (title := node.text):
            raise ValueError("Missing title")
        if (node := root.find("author")) is None or not (author := node.text):
            raise ValueError("Missing author")
        if (node := root.find("year")) is None or not (year := node.text):
            raise ValueError("Missing year")
        if (node := root.find("summary")) is None or not (summary := node.text):
            raise ValueError("Missing summary")
        return Book(title=title, author=author, year=int(year), summary=summary)
    except (ET.ParseError, ValueError) as e:
        print(f"Error parsing XML: {e}")
        return None


@anthropic.call(model="claude-3-5-sonnet-20240620", output_parser=parse_book_xml)
@prompt_template(
    """
    Recommend a {genre} book. Provide the information in the following XML format:
    <book>
        <title>Book Title</title>
        <author>Author Name</author>
        <year>Publication Year</year>
        <summary>Brief summary of the book</summary>
    </book>
                 
    Output ONLY the XML and no other text.
    """
)
def recommend_book(genre: str):
    ...


book = recommend_book("science fiction")
if book:
    print(f"Title: {book.title}")
    print(f"Author: {book.author}")
    print(f"Year: {book.year}")
    print(f"Summary: {book.summary}")
else:
    print("Failed to parse the recommendation.")
```

This example demonstrates how to create a custom XML parser that works with Anthropic's Claude model. The parser extracts structured information from the XML output, making it easy to work with the recommendation in your application.

## Best Practices

- **Align with Prompt Engineering**: Design your prompts to generate outputs that match your parser's expectations. This improves consistency and reliability.
- **Handle Parsing Errors**: Always implement error handling in your parsers. LLMs may occasionally produce outputs that don't conform to the expected structure.
- **Gradual Refinement**: Start with simple parsers and gradually increase complexity as you refine your prompts and understand the model's output patterns.
- **Provide Clear Instructions**: In your prompts, be explicit about the structure you expect the LLM to produce. This helps ensure the output is parseable.
- **Validate Parsed Output**: After parsing, validate the extracted information to ensure it meets your application's requirements.
- **Consider Fallback Strategies**: Implement fallback strategies for cases where parsing fails, such as requesting a reformatted response from the LLM. Check out our [tenacity integration](../integrations/tenacity.md) for more details on how to easily reinsert caught errors into subsequent retries.

## Limitations and Considerations

- **Output Variability**: Even with well-engineered prompts, LLM outputs can vary. Your parsers should be robust enough to handle slight variations.
- **Performance Impact**: Complex parsing operations may impact the overall performance of your application. Consider this when designing your parsers.
- **Model-Specific Behaviors**: Different models may have varying capabilities in producing structured outputs. Test your parsers across different models if you plan to switch or use multiple models.
- **Security Considerations**: When parsing XML or other structured formats, be aware of potential security issues like XML entity expansion attacks. Use secure parsing methods when dealing with untrusted input.

By leveraging Output Parsers effectively, you can create more robust and reliable LLM-powered applications, ensuring that the raw model outputs are transformed into structured data that's easy to work with in your application logic.
