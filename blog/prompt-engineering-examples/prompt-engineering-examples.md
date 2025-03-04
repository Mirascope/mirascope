---
title: Prompt Engineering Examples and Techniques
description: >
  Learn about prompt engineering examples and techniques for designing clear AI requests. Get the best LLM outputs with our list of practical tips and strategies.
authors:
  - willbakst
categories:
  - Tips & Inspiration
date: 2024-07-11
slug: prompt-engineering-examples
---

# Prompt Engineering Examples and Techniques

If there’s one certainty when it comes to prompt engineering it’s this: **the more you put into your prompts in terms of clarity, richness of context, and specificity of detail, the better the model outputs you’ll receive.**

Prompt engineering is the process of structuring and refining your inputs that go into the LLM to get the best outputs. And if you build LLM applications, then getting the model to output the best results possible is important to providing a good user experience for your application.

This is why adherence to best practices is key when it comes to prompting. But in order to bridge the gap between best practice _in theory_ and actual practice, we thought it useful to present a number of prompt engineering examples. These examples not only provide useful snippets for your own use cases, but they illustrate ways in which best practices are actually applied.

<!-- more -->

In this article, we’ll provide three levels of examples: we’ll start with prompts for basic everyday tasks in prompt engineering (perhaps using ChatGPT) in the context of question answering. Afterwards, we’ll describe a type of prompt that’s hardly discussed: multi-turn prompts. 

And we’ll conclude with Python examples of prompts using our own LLM toolkit for building applications, [Mirascope](https://github.com/mirascope/mirascope), which facilitates best practices in prompting like version control and colocation of prompts with calls to the language model.

## Examples of Basic Prompts

Here are six prompt engineering examples that are commonly used:

### 1. Zero-Shot Prompting

Pre-trained language models like GPT-3 or GPT-4 can generate outputs without requiring specific examples of the task at hand. This is effective for general requests that don’t need structured responses or specialized knowledge.

Example:

```plaintext
Can you recommend science-fiction books?
```

Expected response:

```plaintext
Dune by Frank Herbert, Neuromancer by William Gibson, Ender's Game by Orson Scott Card, 
The Hitchhiker's Guide to the Galaxy by Douglas Adams, and Foundation by Isaac Asimov.
```

### 2. Few-Shot Prompting

Giving the language model a few examples of the task as training data allows it to understand the desired output format and the nature of the task. Few-shot prompting is especially useful when the task is specific or requires responses in a particular format.

Example:

```plaintext
Convert the following temperatures from Celsius to Fahrenheit:

0°C to °F: 32°F
25°C to °F: 77°F
-10°C to °F: 14°F

100°C to °F:
```

Expected response:

```plaintext
212°F
```

### 3. Text Summarization

This involves getting the LLM to condense a given text into a shorter version that retains the main points and essential information. It’s useful for quickly extracting key insights from longer texts, such as articles, reports, or documents.

Example:

```plaintext
Summarize the following article:
"The city council has approved a new plan to revitalize the downtown area. The plan 
includes building new parks, renovating old buildings, and improving public 
transportation. The council believes these changes will attract more businesses and 
tourists to the area, boosting the local economy. Construction is set to begin next 
year and will be completed in phases over the next five years."
```

Expected response:

```plaintext
The city council approved a plan to revitalize downtown by building new parks, 
renovating buildings, and improving public transportation. The aim is to attract 
businesses and tourists, boosting the economy. Construction will start next year 
and finish in five years.
```

### 4. Text Classification

Here you’re getting the model to categorize text into predefined classes or labels. This technique is useful for tasks such as sentiment analysis, spam detection, topic categorization, and others. By providing clear examples and a well-defined set of categories, the model can accurately classify new text based on its content.

```plaintext
Classify the following email text as either spam or not spam: "I can make you $1000 
in just an hour. Interested?"
```

Expected response:

```plaintext
Spam
```

### 5. Information Extraction

You guide a language model to identify and extract specific pieces of information from a given text. This is useful for when you need to pull out relevant details, like names, dates, or key facts, from unstructured data. This kind of prompt requires you to clearly define the type of information needed, along with examples, to help the model accurately extract the required information.

Example:

```plaintext
From the following meeting notes, extract the key points discussed and the action items: 
"In today's meeting, we discussed the upcoming product launch, marketing strategies, 
and assigned tasks. John will handle the social media campaign, and Mary will oversee 
the product development."
```

Expected response:

```plaintext
Key Points Discussed:

1. Upcoming product launch.
2. Marketing strategies.

Action Items:

1. John will handle the social media campaign.
2. Mary will oversee the product development.
```

### 6. Chain-of-Thought Prompting (CoT)

You get the LLM to reason through a series of steps or ideas so that it breaks down complex tasks into manageable parts, leading to more accurate responses. You’re basically getting it to first arrive at an intermediate response, which informs the final part of the response.

Example:

```plaintext
Solve the following math problem step by step:
A store had 150 apples. They sold 30 apples in the morning and 50 apples 
in the afternoon. How many apples are left?

Start with the initial number of apples.
Subtract the apples sold in the morning.
Subtract the apples sold in the afternoon.
Provide the final count of apples left.
```

Expected response:

```plaintext
1. Start with the initial number of apples: 150
2. Subtract the apples sold in the morning: 150 - 30 = 120
3. Subtract the apples sold in the afternoon: 120 - 50 = 70
4. The final count of apples left is 70.
```

## Using Multi-Turn Prompts

All the prompts above have one thing in common: they’re generated by a single LLM call, meaning there’s no interactivity between model and user.

**A useful prompting technique few talk about is also well suited for complex prompts, and that’s multi-turn question-response requests**. These involve an interactive process between the user and the AI, where the AI engages in dialog requiring multiple exchanges to reach the final output.

Multi-turn prompts have similarities with [prompt chaining](https://mirascope.com/blog/prompt-chaining) (i.e., output of the last prompt as input to next) **but multi-step prompting involves the user in a back-and-forth dialog in a process of co-creation, collaboration, and fine-tuning**.

Here are some common examples of multi-turn prompts:

* Write a memo in which you get the AI to ask follow-up questions about the tone you want, points to mention, and the audience, to produce a sharper output.
* A “Choose your own adventure game,” where you select the game's theme and then request the AI to provide you with a number of play options at every subsequent turn.

These prompts provide tailored interactions since they gather additional information and preferences from the user before generating the next response.

### Multi-Turn Prompt Example: Write a Post about Prompt Engineering

Although most people probably ask ChatGPT to generate blog posts using a single prompt—albeit subsequently iterating their prompt until they’re satisfied with the output—we’d like to use such an example to show the effectiveness of multi-turn prompting.

#### 1. Our Initial Prompt

```plaintext
I need help writing a blog post about prompt engineering. 

Before we get started, please ask clarifying questions so you can best help me.
```

#### 2. Response from ChatGPT

```plaintext
Sure, I'd be happy to help you write a blog post about prompt engineering! To get 
started, I'll ask you a few clarifying questions to better understand your needs 
and preferences:

1. Target Audience: Who is the primary audience for this blog post? Are they AI 
professionals, developers, beginners in AI, or a general audience interested 
in technology?

2. Tone and Style: What tone would you like the blog post to have? Should it 
be professional, casual, technical, or conversational?

3. Key Points: Are there specific key points or topics you want to cover in 
the blog post? For example, definitions, examples, best practices, advanced 
techniques, NLP, etc.

4. Length: How long do you want the blog post to be? (e.g., 500-700 words, 
1000-1500 words)

5.Examples: Do you have any specific examples or case studies you want to 
include in the blog post?

6. Structure: Do you have a preferred structure or format for the blog post? 
(e.g., introduction, body, conclusion, headings, subheadings)

7. Purpose: What is the main purpose of the blog post? Is it to inform, 
educate, entertain, or persuade your audience?

Once I have the answers to these questions, I can better assist you in 
crafting a comprehensive and engaging blog post on prompt engineering.
```

#### 3. Our response to the Clarifying Questions

```plaintext
1. Target Audience: Developers working with large language models and building 
applications based on these.

2. Tone and Style: Casual and conversational.

3. Key Points: Examples and best practices.

4. Length: 1200 words.

5. Examples: No concrete examples at this time.

6. Structure: Introduction, body, conclusion, headings, subheadings

7. Purpose: To inform our target audience.
```

#### 4. ChatGPT Prompts Us Once More with Clarifying Questions

```plaintext
Further clarifying questions:

1. Introduction: Is there any specific hook or opening statement you’d like to use to 
grab the readers' attention?

2. What is Prompt Engineering?: Do you have any particular definitions or explanations 
you prefer to use when describing prompt engineering?

3. Examples of Effective Prompt Engineering:
- Do you want to include hypothetical examples here, or should I create some based on 
common use cases?
- Are there particular types of tasks (e.g., email drafting, creative writing) you want 
these examples to focus on?

4. Best Practices:
- Are there any additional best practices specific to your experience or insights that 
you want to emphasize?

5. Advanced Techniques:
- Do you have any preferences for which advanced techniques to highlight or any insights 
on them you want to share?

6. Common Pitfalls:
- Are there specific challenges you've encountered or observed that you’d like to highlight 
in this section?

7. Conclusion:
- Any specific calls to action or final thoughts you want to leave the readers with?
```

#### 5. Our Response to the Latest Clarifying Questions

```plaintext
1. Introduction: Is there any specific hook, specific task, or opening statement you’d like to use to grab the readers'attention? Answer: mention a challenge one typically encounters in prompt engineering.

2. What is Prompt Engineering?: Do you have any particular definitions or explanations you prefer to use when describing prompt engineering? Answer: none in particular.

3. Examples of Effective Prompt Engineering:
- Do you want to include hypothetical examples here, or should I create some based on common use cases? Answer: yes please create one based on common use cases.
- Are there particular types of tasks (e.g., email drafting, creative writing) you want these examples to focus on? Answer: surprise me.

4. Best Practices:
- Are there any additional best practices specific to your experience or insights that you want to emphasize? Answer: yes, mention the importance of colocating a prompt with its LLM call.

5. Advanced Techniques:
- Do you have any preferences for which advanced techniques to highlight or any insights on them you want to share? Answer: none.

6. Common Pitfalls:
- Are there specific challenges you've encountered or observed that you’d like to highlight in this section? Answer: mention occasional LLM hallucinations.

7. Conclusion:
- Any specific calls to action or final thoughts you want to leave the readers with? Answer: yes, ask them to check out Mirascope's GitHub page.
```

The LLM’s output is much more in line with what we want and expect than had we used single-turn prompts to generate the output in one go.

```plaintext
Introduction
Imagine spending hours crafting the perfect prompt for your artificial model, only to receive responses that are completely off the mark. As developers working with large language models (LLMs) and generative AI, this is a challenge we often face in fields like data analysis and computer science. The art and science of prompt engineering techniques are crucial to harnessing the full potential of these powerful tools based on capabilities like machine learning. In this blog post, we'll explore what real-world prompt engineering entails, provide examples and best practices, delve into advanced techniques, and highlight common pitfalls to avoid.

What is Prompt Engineering?

Prompt engineering is the practice of designing and structuring an AI prompt to guide artificial intelligence models that use natural language processing in generating accurate and relevant responses. It's about creating the right questions or instructions as datasets that enable the AI to understand the task at hand and deliver the desired results. For developers working with AI tools, mastering prompt engineering is essential for building and optimizing effective AI-driven applications like chatbots.

Examples of Effective Prompt Engineering

To illustrate effective prompt engineering, let's look at a few hypothetical scenarios that showcase different types of tasks:

Example 1: Email Drafting
Imagine you need the AI to draft a professional email for a meeting request. A poorly crafted prompt might be:

"Write an email for a meeting."

This lacks specificity and context. A better prompt would be:

"You are an executive assistant. Write a formal email requesting a meeting with a potential client, John Doe, to discuss our new project proposal. Mention possible dates and times for the meeting, and ask for his availability."

This revised prompt provides a clear role, context, and specific instructions, leading to a more accurate and useful response...
```

## Best Practices for Prompt Engineering

While the above are examples of different types of prompts, doing prompt _engineering_ at scale to develop LLM-based applications like chatbots will necessarily involve using code to generate and manage the prompt examples shown above. When developing in code, you should follow certain best practices to manage your prompts.

[We’ve shared several frustrations](https://mirascope.com/blog/engineers-should-handle-prompting-llms) with not adhering to best practices in the past—especially before best practices, or even prompt engineering, were a thing—like having to spend time hunting down the causes of errors when your code isn’t colocated with your calls. Or prompts becoming unmanageable past several versions when changes weren’t tracked.

Or, still, writing massive amounts of boilerplate for the first versions of the OpenAI SDK, whose code is (still) autogenerated and without the additional conveniences we’re building on top of Mirascope.

Our article on [best practices](https://mirascope.com/blog/prompt-engineering-best-practices) goes more in depth on the guiding principles we’ve developed around prompt engineering, and suffice it to say, our development practices are more efficient because of them.

It’s also why we built Mirascope. We wanted to simplify our workflows so we could focus on what matters most: building innovative applications without the overhead of managing complex and repetitive code.

A few examples of how Mirascope ensures your development efforts are efficient and scalable:

* We believe that everything that impacts the quality of a call should live together. To that end, you’ll often find the LLM call and all its parameters neatly encapsulated within our prompt classes.
* The LLM call should be the central organizing unit around which everything, including the prompt, [gets versioned and tested](https://mirascope.com/blog/prompt-versioning).
* The quality of your inputs makes all the difference to the quality and reliability of your outputs, and so should be constrained, e.g., for type safety, adherence to a schema, etc. We handle all the tedious Python typing details, ensuring you have a clean interface with proper type hints and linting to avoid annoying bugs.

To illustrate these principles, we’ll show how the multi-turn prompt, described in the previous section, would be implemented in both OpenAI or Mirascope:

### Multi-Turn Prompt Example Using the OpenAI SDK

In the code sample below, we use the OpenAI SDK to get the LLM to write a blog article for us, setting up a multi-turn chat using GPT-4o:

```python
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam


def multi_turn_chat():
    client, history = OpenAI(), []
    while True:
        query = input("You: ")
        if query in ["exit", "quit"]:
            break
        user_message: ChatCompletionMessageParam = {"role": "user", "content": query}
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant.\nYour task is to help the user write a blog post.",
                },
                *history,
                user_message,
            ],
        )
        message = response.choices[0].message
        print(f"Assistant: {message.content}")
        history += [user_message, message]


multi_turn_chat()
# > You: I need help writing a blog post...
```

The code above continuously prompts the user for input, sends the input along with the conversation history to the OpenAI API, processes the response, and maintains the context of the conversation. The chat continues until the user types in “exit” or “quit.”

### Multi-Turn Prompt Example Using Mirascope

Below, we similarly show how we build a multi-turn prompt using Mirascope:

```python
from openai.types.chat import ChatCompletionMessageParam

from mirascope.core import openai, prompt_template


@openai.call("gpt-4o-mini")
@prompt_template(
    """
    SYSTEM:
    You are a helpful assistant.
    Your task is to help the user write a blog post.

    MESSAGES: {history}
    USER: {query}
    """
)
def respond(query: str, history: list[ChatCompletionMessageParam]): ...


def multi_turn_chat():
    history = []
    while True:
        query = input("You: ")
        if query in ["exit", "quit"]:
            break
        response = respond(query, history)
        print(f"Assistant: {response.content}")
        history += [response.user_message_param, response.message_param]


multi_turn_chat()
# > You: I need help writing a blog post...
```

Here, we’re doing essentially the same thing as with the previous code for the OpenAI SDK, except that:

* We use the decorator `@openai.call` to define the API call function, making the code more concise and encapsulated than OpenAI’s above, which defines the API call within its `while` loop. You can also easily use another model provider beyond OpenAI just by switching the decorator without having to change anything else. Compare this with using the [Anthropic SDK](https://github.com/anthropics/anthropic-sdk-python), for example, where you'd have to change a lot more because they don't have the same interfaces.
* We use placeholders within the function docstring to dynamically insert the system message, history, and user input, which simplifies the construction process. OpenAI, on the other hand, constructs the `messages` list manually within its loop.
* We use attributes of the response object (`response.content`, `response.user_message_param`, `response.message_param`) to handle the response and update the history. This abstracts away the complexity involved in parsing and handling the response, whereas OpenAI requires manually accessing and parsing response elements, which can lead to more verbose code.

Overall, we abstract away repetitive tasks like constructing message lists as much as possible, reducing the amount of boilerplate code and improving readability.

Note that for a simple example like the above, the benefits of using Mirascope may not shine as greatly as they do for more complex use cases; however, even these simple primitives become very powerful because they improve readability and reusability of code (which is important as your system becomes more complex).

## Mirascope Helps You Do Effective Prompt Engineering

Our philosophy is: building blocks over [frameworks](https://mirascope.com/blog/prompt-flow-vs-langchain), so we can build our own tools in Python without needing to learn new abstractions. Mirascope lets you work with LLMs in the Python you already know, and its discrete modules slot right into your existing workflows, without you needing to adopt an entire rigid framework.

Want to learn more? You can find more Mirascope code samples both on our [documentation site](https://mirascope.com) and the [GitHub repository](https://github.com/mirascope/mirascope).
