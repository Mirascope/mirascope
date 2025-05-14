# Dynamic Configuration & Chaining

This notebook provides a detailed introduction to using Dynamic Configuration and Chaining in Mirascope. We'll cover various examples ranging from basic usage to more complex chaining techniques.

## Setup

First, let's install Mirascope and set up our environment. We'll use OpenAI for our examples, but you can adapt these to other providers supported by Mirascope. For more information on supported providers, see the [Calls documentation](../../../learn/calls).


```python
!pip install "mirascope[openai]"
```


```python
import os

os.environ["OPENAI_API_KEY"] = "your-api-key-here"
```

## Dynamic Configuration

Dynamic Configuration in Mirascope allows you to modify the behavior of LLM calls at runtime based on input arguments or other conditions.

### Basic Usage


```python
from mirascope.core import BaseDynamicConfig, Messages, openai


@openai.call("gpt-4o-mini")
def recommend_book(genre: str, creativity: float) -> BaseDynamicConfig:
    return {
        "messages": [Messages.User(f"Recommend a {genre} book")],
        "call_params": {"temperature": creativity},
    }


# Low creativity recommendation
response = recommend_book("mystery", 0.2)
print("Low creativity:", response.content)

# High creativity recommendation
response = recommend_book("mystery", 0.8)
print("High creativity:", response.content)
```

    Low creativity: I recommend "The Guest List" by Lucy Foley. This gripping mystery unfolds during a glamorous wedding on a remote Irish island, where tensions among the guests rise and secrets are revealed. When a murder occurs, everyone becomes a suspect, and the story alternates between different perspectives, keeping you guessing until the very end. It's a compelling read with well-developed characters and a twisty plot that will keep you on the edge of your seat!
    High creativity: I recommend "The Girl with the Dragon Tattoo" by Stieg Larsson. This gripping mystery combines elements of crime, family saga, and social commentary. It follows journalist Mikael Blomkvist and hacker Lisbeth Salander as they investigate a decades-old disappearance amidst a backdrop of dark family secrets and corporate corruption. The complex characters and intricate plot make it a compelling read for mystery enthusiasts. Enjoy!


### Computed Fields

When using the `Messages.Type` return for writing prompt templates, you can inject computed fields directly into the formatted strings:


```python
@openai.call("gpt-4o-mini")
def recommend_book_by_age(genre: str, age: int) -> Messages.Type:
    reading_level = "adult"
    if age < 12:
        reading_level = "elementary"
    elif age < 18:
        reading_level = "young adult"
    return f"Recommend a {genre} book with a reading level of {reading_level}"


response = recommend_book_by_age("fantasy", 15)
print(response.content)
```

    I recommend **"An Ember in the Ashes"** by Sabaa Tahir. This young adult fantasy novel is set in a brutal, ancient Rome-inspired world where the oppressed must fight against a tyrannical regime. The story follows Laia, a young woman who becomes a spy for the resistance to save her brother, and Elias, a soldier who wants to escape the oppressive society. The book is rich in world-building, features complex characters, and explores themes of freedom, loyalty, and sacrifice. It's an engaging read for young adults looking for an exciting fantasy adventure!


When using string templates, you can use computed fields to dynamically generate or modify template variables used in your prompt. For more information on prompt templates, see the [Prompts documentation](../../../learn/prompts).


```python
from mirascope.core import prompt_template


@openai.call("gpt-4o-mini")
@prompt_template("Recommend a {genre} book with a reading level of {reading_level}")
def recommend_book_by_age(genre: str, age: int) -> openai.OpenAIDynamicConfig:
    reading_level = "adult"
    if age < 12:
        reading_level = "elementary"
    elif age < 18:
        reading_level = "young adult"
    return {"computed_fields": {"reading_level": reading_level}}


response = recommend_book_by_age("fantasy", 15)
print(response.content)
```

    I recommend "An Ember in the Ashes" by Sabaa Tahir. This gripping fantasy novel is set in a world inspired by ancient Rome, where a fierce soldier and a rebellious scholar find their destinies intertwined. With themes of bravery, sacrifice, and love, it's an engaging read suitable for young adult audiences. The rich world-building and complex characters make it a standout in the young adult fantasy genre. Enjoy your reading!


### Dynamic Tools

You can dynamically configure which tools are available to the LLM based on runtime conditions. Here's a simple example using a basic tool function:


```python
def format_book(title: str, author: str, genre: str) -> str:
    """Format a book recommendation."""
    return f"{title} by {author} ({genre})"


@openai.call("gpt-4o-mini")
def recommend_book_with_tool(genre: str) -> openai.OpenAIDynamicConfig:
    return {
        "messages": [Messages.User(f"Recommend a {genre} book")],
        "tools": [format_book],
    }


response = recommend_book_with_tool("mystery")
if response.tool:
    print(response.tool.call())
else:
    print(response.content)
```

    The Girl with the Dragon Tattoo by Stieg Larsson (Mystery)


For more advanced usage of tools, including the `BaseToolKit` class, please refer to the [Tools documentation](../../../learn/tools) and the [Tools and Agents Tutorial](../tools_and_agents).

## Chaining

Chaining in Mirascope allows you to combine multiple LLM calls or operations in a sequence to solve complex tasks. Let's explore two main approaches to chaining: function-based chaining and chaining with computed fields.

### Function-based Chaining

In function-based chaining, you call multiple functions in sequence, passing the output of one function as input to the next. This approach requires you to manage the sequence of calls manually.


```python
@openai.call("gpt-4o-mini")
def summarize(text: str) -> str:
    return f"Summarize this text: {text}"


@openai.call("gpt-4o-mini")
def translate(text: str, language: str) -> str:
    return f"Translate this text to {language}: {text}"


original_text = "Long English text here..."
summary = summarize(original_text)
translation = translate(summary.content, "french")
print(translation.content)
```

    Bien sûr ! Veuillez fournir le long texte en anglais que vous souhaitez que je résume.


### Nested Chaining

You can easily create a single function that calls the entire chain simply by calling each part of the chain in the function body of the corresponding parent:


```python
@openai.call("gpt-4o-mini")
def summarize(text: str) -> str:
    return f"Summarize this text: {text}"


@openai.call("gpt-4o-mini")
def summarize_and_translate(text: str, language: str) -> str:
    summary = summarize(original_text)
    return f"Translate this text to {language}: {summary.content}"


original_text = "Long English text here..."
translation = summarize_and_translate(original_text, "french")
print(translation.content)
```

    Bien sûr ! Veuillez fournir le texte que vous souhaitez que je résume, et je ferai de mon mieux pour vous aider.


### Chaining with Computed Fields

Chaining with computed fields allows you to better trace your nested chains since the full chain of operations will exist in the response of the single function (rather than having to call and track each part of the chain separately).


```python
@openai.call("gpt-4o-mini")
def summarize(text: str) -> str:
    return f"Summarize this text: {text}"


@openai.call("gpt-4o-mini")
@prompt_template("Translate this text to {language}: {summary}")
def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
    return {"computed_fields": {"summary": summarize(text)}}


response = summarize_and_translate("Long English text here...", "french")
print("Translation:", response.content)
print(
    "\nComputed fields (including summary):", response.dynamic_config["computed_fields"]
)
```

    Translation: Bien sûr ! Veuillez fournir le texte que vous aimeriez que je résume, et je serai heureux de vous aider.
    
    Computed fields (including summary): {'summary': OpenAICallResponse(metadata={}, response=ChatCompletion(id='chatcmpl-ABSRkdlz6phtmOBWqwVigidqET2tr', choices=[Choice(finish_reason='stop', index=0, logprobs=None, message=ChatCompletionMessage(content="Of course! Please provide the text you'd like me to summarize, and I'll be happy to help.", refusal=None, role='assistant', function_call=None, tool_calls=None))], created=1727294320, model='gpt-4o-mini-2024-07-18', object='chat.completion', service_tier=None, system_fingerprint='fp_1bb46167f9', usage=CompletionUsage(completion_tokens=20, prompt_tokens=18, total_tokens=38, completion_tokens_details={'reasoning_tokens': 0})), tool_types=None, prompt_template=None, fn_args={'text': 'Long English text here...'}, dynamic_config={'messages': [BaseMessageParam(role='user', content='Summarize this text: Long English text here...')]}, messages=[{'role': 'user', 'content': 'Summarize this text: Long English text here...'}], call_params={}, call_kwargs={'model': 'gpt-4o-mini', 'messages': [{'role': 'user', 'content': 'Summarize this text: Long English text here...'}]}, user_message_param={'content': 'Summarize this text: Long English text here...', 'role': 'user'}, start_time=1727294320238.506, end_time=1727294320929.094, message_param={'content': "Of course! Please provide the text you'd like me to summarize, and I'll be happy to help.", 'refusal': None, 'role': 'assistant', 'tool_calls': None}, tools=None, tool=None)}


As you can see, with computed fields, you get access to both the final translation and the intermediate summary in a single response. This approach provides better traceability and can be particularly useful for debugging and understanding the entire chain of operations without the need to manage multiple separate function calls.

Of course, you can always put the computed fields in the dynamic configuration without using string templates for the same effect:


```python
@openai.call("gpt-4o-mini")
def summarize(text: str) -> str:
    return f"Summarize this text: {text}"


@openai.call("gpt-4o-mini")
def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
    summary = summarize(text)
    return {
        "messages": [
            Messages.User(f"Translate this text to {language}: {summary.content}"),
        ],
        "computed_fields": {"summary": summary},
    }


response = summarize_and_translate("Long English text here...", "french")
print("Translation:", response.content)
print(
    "\nComputed fields (including summary):", response.dynamic_config["computed_fields"]
)
```

    Translation: Bien sûr ! Veuillez fournir le texte que vous aimeriez que je résume.
    
    Computed fields (including summary): {'summary': OpenAICallResponse(metadata={}, response=ChatCompletion(id='chatcmpl-ABSRz6D82ecWKlAU7VUmWU4wbqiaY', choices=[Choice(finish_reason='stop', index=0, logprobs=None, message=ChatCompletionMessage(content="Sure! Please provide the text you'd like me to summarize.", refusal=None, role='assistant', function_call=None, tool_calls=None))], created=1727294335, model='gpt-4o-mini-2024-07-18', object='chat.completion', service_tier=None, system_fingerprint='fp_1bb46167f9', usage=CompletionUsage(completion_tokens=12, prompt_tokens=18, total_tokens=30, completion_tokens_details={'reasoning_tokens': 0})), tool_types=None, prompt_template=None, fn_args={'text': 'Long English text here...'}, dynamic_config={'messages': [BaseMessageParam(role='user', content='Summarize this text: Long English text here...')]}, messages=[{'role': 'user', 'content': 'Summarize this text: Long English text here...'}], call_params={}, call_kwargs={'model': 'gpt-4o-mini', 'messages': [{'role': 'user', 'content': 'Summarize this text: Long English text here...'}]}, user_message_param={'content': 'Summarize this text: Long English text here...', 'role': 'user'}, start_time=1727294335206.361, end_time=1727294335879.617, message_param={'content': "Sure! Please provide the text you'd like me to summarize.", 'refusal': None, 'role': 'assistant', 'tool_calls': None}, tools=None, tool=None)}


## Error Handling in Chains

Implementing robust error handling is crucial in complex chains:


```python
from openai import OpenAIError


@openai.call("gpt-4o-mini")
def summarize(text: str) -> str:
    return f"Summarize this text: {text}"


@openai.call("gpt-4o-mini")
def translate(text: str, language: str) -> str:
    return f"Translate this text to {language}: {text}"


def process_text_with_error_handling(text: str, target_language: str):
    try:
        summary = summarize(text).content
    except OpenAIError as e:
        print(f"Error during summarization: {e}")
        summary = text  # Fallback to original text if summarization fails

    try:
        translation = translate(summary, target_language).content
        return translation
    except OpenAIError as e:
        print(f"Error during translation: {e}")
        return summary  # Fallback to summary if translation fails


result = process_text_with_error_handling("Long text here...", "French")
print("Processed Result:", result)
```

    Processed Result: Bien sûr ! Veuillez fournir le texte que vous souhaiteriez que je résume.


## Conclusion

This notebook has demonstrated various techniques for using Dynamic Configuration and Chaining in Mirascope. These powerful features allow you to create flexible, efficient, and complex LLM-powered applications. By combining these techniques, you can build sophisticated AI systems that can adapt to different inputs and requirements while maintaining robustness and traceability.

Remember to always consider error handling, especially in complex chains, to ensure your applications are resilient to potential issues that may arise during LLM calls or processing steps.

If you like what you've seen so far, [give us a star](https://github.com/Mirascope/mirascope) and [join our community](https://join.slack.com/t/mirascope-community/shared_invite/zt-2ilqhvmki-FB6LWluInUCkkjYD3oSjNA).
