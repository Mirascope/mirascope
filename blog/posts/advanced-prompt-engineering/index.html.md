---
title: A Guide to Advanced Prompt Engineering
description: >
  Learn how advanced prompt engineering techniques like in-context learning and few-shot prompts can boost LLM performance and accuracy.
authors:
  - willbakst
categories:
  - Tips & Inspiration
date: 2024-11-11
slug: advanced-prompt-engineering
---

# A Guide to Advanced Prompt Engineering

Advanced prompt engineering – which usually involves techniques such as few-shot learning, multi-step reasoning, and sophisticated prompting – enriches prompts with greater context and guidance to get better answers from the language model.

This is in contrast to basic prompting where you give the LLM simpler, direct instructions.

The more complex the task, **the greater the need to structure prompts to guide the model with reasoning steps, external information, and specific examples**.

Done right, advanced prompt engineering techniques let you do some pretty impressive things, for instance:

* Not only write about Ernest Hemingway but write *like* Hemingway.  
* Generate product descriptions solely from e-commerce images, automatically extracting features like color, size, and material.  
* Fact check a debate or conversation in real time by allowing agents to search multiple web sources and present the most accurate information with citations.  
* Troubleshoot internal IT issues using a bot that identifies common issues and suggests solutions from the company’s knowledge base.

<!-- more -->

The key is you can’t achieve these results (with today’s language models) with a simple request (i.e., a basic prompt), so your prompts will require thought, effort, and iteration, and (in many cases) a framework to orchestrate the model’s responses.

This is where you need advanced prompt engineering, which some refer to as a new kind of programming. And we’d agree: at the very least, it’s programming in human rather than computer language, and requires thoughtful design and iteration.

With that in mind, we created this guide to outline some techniques for writing advanced prompts more effectively to influence the model’s output.

Our own interest in prompting, in order to build, refine, and experiment with LLM agents, began with our experiences using the first versions of the OpenAI SDK, which we found frustrating because of how much unnecessary boilerplate we felt we had to write. We also found other libraries at the time were not exactly production ready.

This led us to design [Mirascope](https://github.com/mirascope/mirascope), a modular toolkit for interacting with language models and developing clean, well-organized queries.

## Advanced Prompt Engineering Strategies

The [strategies](https://mirascope.com/blog/prompt-engineering-best-practices) below guide LLMs to generate more accurate and context-aware outputs by embedding structures, examples, and external data modules into prompts.

### Use In-Context Learning to Write Better Prompts

The fact that API calls are stateless requires that we build full context directly into our generative AI prompts.

This is where in-context learning comes into play: the model uses the information in the current prompt as temporary memory to understand the task at hand and to better predict the next words, phrases, or sentences in its responses.

This means you can add a few examples of, say, sentiment analysis in your prompt, and the model will infer that it needs to do sentiment analysis on a new piece of text without your explicit instruction.

Below, we show different ways to incorporate in-context learning in your prompts.

#### Use Few-Shot Prompts to Teach the Model

In few-shot prompting, you send multiple examples (i.e, “input-output pairs”) showing the format or pattern in which you want the natural language model to answer.

This allows the model to generalize task requirements so it can leverage its existing knowledge to accomplish different tasks.

In this few-shot prompt, we include several examples of classifying customer feedback as either positive or negative:

```plaintext
Instruction:
You are tasked with performing sentiment analysis on customer feedback regarding the customer service department of a corporate food catering company. Your goal is to classify whether the sentiment expressed in the feedback is "positive" or "negative." Below are several examples of feedback along with their corresponding sentiment classifications to guide your understanding of the task. After reviewing these examples, classify the sentiment of the new feedback provided. Respond only with "positive" or "negative."

Examples:

1. "The customer service representative was incredibly helpful! They quickly resolved my issue and made sure I was satisfied with the outcome."
Sentiment: positive

2. "I’ve been trying to reach the customer support team for days, and no one has responded. This is unacceptable."
Sentiment: negative

3. "The team was very attentive to our needs and made sure we had everything set up for our event. It was a pleasure working with them."
Sentiment: positive

4. "The service was delayed, and the representative I spoke to was rude. I won’t be using this catering service again."
Sentiment: negative

Now, analyze the sentiment of the following feedback:

"The support team was polite but took way too long to get back to me. It made planning much more stressful than it should have been."

Classify the sentiment of the feedback:
# Output: negative
```

The examples clarify the instructions by providing further details on how the model should classify customer sentiment.

#### Define Clear Roles to Set Context

Specifying roles you want the model to assume, like AI assistant, technical advisor, or a creative persona like a novelist, also helps guide its tone, style, and output to better match your task.

For instance, you can describe roles in prompts for fitness advice or creative writing:

```plaintext
You are a professional fitness coach with extensive experience in helping individuals improve their endurance. Based on this expertise, create a personalized cardio workout plan that minimizes joint strain.

You are a novelist known for your vivid descriptions and deep character development. Write an engaging opening paragraph for a mystery novel, set in a small coastal town, where a sudden disappearance shocks the close-knit community.
```

In a programmatic context, roles offer a structured way to manage interactions and maintain clear context over multiple exchanges.

So you could specify roles such as SYSTEM, USER, and ASSISTANT to further refine the interaction by setting different responsibilities and behaviors for each role. For example:

* SYSTEM indicates the role or expertise the model should embody.  
* USER defines the input provided by the user.  
* ASSISTANT specifies the response expected from the model.

Below, we prompt the SYSTEM to assume the role of an insightful fitness coach, the USER to express feedback and specific workout preferences, and the ASSISTANT to provide personalized, low-impact cardio recommendations based on the USER’s past experiences and physical limitations:

```plaintext
SYSTEM
You are the world’s most insightful fitness coach, known for creating personalized workout routines that align with individual goals, fitness levels, and unique physical needs. When giving advice, always consider the user’s past workouts, preferences, and any physical limitations. Provide detailed explanations for each recommendation, including how it benefits the user’s specific goals.

USER:
Can you suggest a HIIT workout for endurance?

ASSISTANT:
Given your previous mention of knee discomfort, I recommend a modified low-impact HIIT routine that reduces joint strain. We can use exercises like cycling or swimming intervals that provide cardio benefits without the high impact on your knees.

USER:
That sounds good. Now, can you suggest a low-impact cardio routine for improving endurance?

ASSISTANT:
For improving endurance while minimizing knee strain, I suggest a low-impact routine focused on brisk walking or swimming. Both provide excellent cardiovascular benefits with minimal joint impact. I can also include some gentle strength exercises to build supporting muscles around your knees.
```

Such roles define the structure and expectations of the conversation to a higher degree and are usually [used in conjunction with code](https://mirascope.com/learn/prompts) that dynamically manages the flow of interactions, ensuring consistent responses tailored to user inputs and context.

#### Leverage Prompt Templates for Consistency

A prompt template is a reusable set of instructions that can be customized with specific details each time it's used. Instead of rewriting the entire prompt, you can simply fill in the template with the necessary information, ensuring consistency across prompts.

In a coding context, you can add placeholders like `{variable}` to alter specific parts of the instruction during runtime (i.e., prompt execution) to allow automatic insertion of values into the prompt, like user input or context-specific information, while allowing the main instruction to stay the same.

For example, you can experiment with the prompt below by specifying values for `{diet_type}`, such as “keto,” “vegan,” or “gluten free”:

```plaintext
You are a nutritionist specializing in creating personalized meal plans. Based on the {diet_type} diet, suggest a healthy meal plan for the day.
```

At runtime the variable is resolved to the defined value and the entire prompt is sent to the LLM as text:

```plaintext
You are a nutritionist specializing in creating personalized meal plans. Based on the vegan diet, suggest a healthy meal plan for the day.

```

Prompt templates help maintain a consistent format across your interactions, reducing the risk of variability or ambiguity in the prompt structure and making the model’s outputs more predictable.

For good reason, the usage of prompt templates is widespread among many advanced prompt engineering libraries and frameworks such as [LangChain](https://mirascope.com/blog/langchain-prompt-template).

For those applying prompt engineering in code, Mirascope offers an easy way to [bind prompt templates](https://mirascope.com/learn/prompts) to functions and classes.

#### Chain Calls Together to Do Complex Tasks

Prompt chaining, a popular prompting method, involves breaking down a large, multifaceted prompt into smaller, more manageable sub-tasks to be implemented in sequence.

Each subtask is a prompt with its own LLM call, so the output of one call becomes input to the next. This allows the model to fully process the refined outputs of each intermediate step before proceeding to the next, leading to more accurate and coherent final results.

For example, say you need to summarize a very lengthy legal document and then analyze whether certain clauses align with recent case law.

With chaining, rather than entering both tasks in a single query (especially considering the length of the document), you’d first prompt the model to summarize the document itself to produce a more concise representation of its key points. After reviewing the output, you might then ask the model to analyze specific clauses using the summary as context.

The summary serves as a clean input to the next task, allowing the model to focus on the legal analysis rather than juggling both tasks at once:

First prompt:

```plaintext
Summarize the following contract in no more than three sentences: [Insert contract text].
```

Output:

```plaintext
The contract is a service agreement between Company A and Company B. It outlines the scope of services, payment terms, and termination conditions. Company B agrees to provide IT support for a period of one year, subject to renewal [...rest of summary].
```

Second prompt (chained to the output of the first prompt):

```plaintext
Based on the summary provided, does the termination clause align with recent case law regarding service contracts in California?
```

Output:

```plaintext
The termination clause in the summary seems to be a standard provision, but recent case law in California has indicated that service contracts must allow for a minimum 30-day notice period. You should verify if the contract specifies this time frame.
```

The above prompts show the basics of how prompt chaining works, but for those interested in intuitive ways of chaining LLM calls, Mirascope allows you to use [computed fields and functions](https://mirascope.com/blog/prompt-chaining).

### Version Prompts to Track and Iterate

It’s helpful to use version control to keep a clear record of changes and revert to earlier prompts if necessary.

We recommend using a [prompt management system](https://mirascope.com/blog/prompt-versioning) to track and document changes, compare different versions, and easily revert to previous iterations.

Using version control also allows you to maintain separate prompt versions across different models so you can customize prompts for each model’s unique capabilities or context.

An example of a prompt versioning system is [Lilypad](https://lilypad.so/docs), which you can download and install in your local workspace. In Lilypad, every LLM call is automatically versioned and traced for you so you don't have to worry about manually managing your prompts.

### Integrate Data from External Sources

Adding data from external systems and applications allows LLMs to move beyond simple text generation and do more in-depth, complex operations based on dynamic, real-world inputs.

Models then become capable of retrieving real-time data, executing intricate workflows, and making informed decisions based on specific use cases and situational data.

When building LLM-driven applications, it might be necessary to use [data orchestration](https://mirascope.com/blog/llm-orchestration) to coordinate flows between the model’s inputs and external systems, and to ensure the desired output is appropriately routed or processed.

This can mean connecting to databases, leveraging APIs, or pulling in real-time information from external applications — all while maintaining the integrity and relevance of the data to the user’s needs.

Below are two popular applications incorporating external data:

#### Use Automated Search

Large language models can tap into external tools and data sources like news databases, weather services, or custom APIs via search queries driven by user inputs.

Being able to access the most recent information improves the accuracy of the model’s response and allows it to respond with precise details that may not be available within its pre-trained, existing knowledge.

Our tutorial on [building a web search agent](https://mirascope.com/tutorials/agents/web_search_agent/) that uses DuckDuckGo to find information relating to your queries provides more details about how automated search works.

#### Retrieval Augmented Generation

Unlike web search, knowledge prompting through retrieval augmented generation (RAG) provides answers using a specific knowledge base.

On the one hand, answers from RAG are confined to both the LLM’s own knowledge and that of the attached database. On the other, RAG gives you highly relevant and accurate information for domain-specific queries.

RAG enables all kinds of applications. For instance, RAG could be implemented as a front-line chatbot assisting customers by retrieving policy-specific information and answering questions.

The basic mechanism of how RAG works is this. Factual information from the knowledge base is incorporated into the prompt to enrich it contextually and to improve the quality of responses while drastically reducing hallucinations.

The broad steps in this pipeline are:

1. First, identify the information or datasets for the RAG to use. This will usually be unstructured, like blog articles, PDFs, and image files. Prepare the content for the next step by parsing it and splitting it into logical sections, and chunking it into sections suitable for encoding it into vectors (if you’re using vectorization in the first place).  
2. Encode the chunks into vectors using an embedding model. Embedding models convert text or other data into numerical representations that capture the semantic meaning of the content, which allows the system to efficiently analyze and compare relationships between different pieces of information.  
3. Load the vectorized content into a central repository or database, often referred to as a vector store.  
4. When a user submits a query, the system similarly encodes it as a vector, which it then matches with the archived content in the vector store using a search algorithm (e.g.,  cosine similarity or dot product).
5. The system retrieves the content and combines it with the user’s query as a prompt to send to the language model. This is what we refer to as a contextually enriched prompt; it gives the model more complete information to consider than a single question.

For detailed information on how RAG works, our blog post on [building LLM pipelines](https://mirascope.com/blog/llm-pipeline) shows how to set this up using Mirascope’s advanced prompt engineering features.

## 6 Advanced Prompting Techniques

Below we explore six [sophisticated techniques](https://mirascope.com/blog/prompt-engineering-examples) for improving model reasoning, consistency, and ability to modify its approach based on the prompt or task at hand:

* Rephrase and Respond (RaR)  
* Chain of Thought (CoT)  
* Self-Ask  
* Tree of Thought (ToT)  
* Chain of Verification  
* Self-Consistency

### 1. Rephrase and Respond (RaR)

A prompt that gets the model to think through a problem step by step is rephrase and respond, where you first ask it to rephrase and expand on a question before providing its response.

This allows the model to better understand and clarify the original query, especially if the prompt is vague or lacks detail.

In the example below, we start with a rather brief and unclear prompt. By using RaR, the model rephrases the question before responding.

First prompt:

```plaintext
A coin is heads up. Aluino flips the coin. Arthur flips the coin. Is the coin still heads up? Flip means reverse. Rephrase and expand the question, and respond
```

Response:

```plaintext
A coin starts with the heads side facing up. If Aluino flips the coin, it will land with the tails side facing up. Then Arthur flips the coin again. After these two sequences of flips, can we say that the coin is still heads up?

To analyze the scenario, let’s break down the actions step by step:
1. Initial State: The coin starts with the heads side facing up.
2. Aluino Flips the Coin: When Aluino flips the coin, it reverses its position. Since the coin initially was heads up, after Aluino’s flip, the coin will now be tails up.
3. Arthur Flips the Coin: Next, Arthur takes his turn to flip the coin. Given that the current state of the coin is tails up, flipping it will reverse it again, resulting in the coin now being heads up.
At the end of these actions, after both Aluino and Arthur have flipped the coin, the final state of the coin is heads up once more.
```

You can also see a version of this [RaR prompt in Python](https://mirascope.com/tutorials/prompt_engineering/text_based/rephrase_and_respond/) in our code tutorials.

### 2. Chain of Thought (CoT)

Chain-of-thought prompting encourages the model to break a problem down into smaller, logical steps for separate consideration rather than just providing the answer immediately.

This mirrors how a human might tackle a complex problem, and is effective for tasks requiring critical thinking, like math, reasoning tasks, and problem-solving scenarios.

You’re basically asking the model to think aloud and explain each step of the process leading to the final answer.

Example:

```plaintext
Olivia has $23. She bought five bagels for $3 each. How much money does she have left? Let's think step by step.
```

Response:

```plaintext
First, let’s determine how much money Olivia spent on the bagels:
Price of one bagel = $3
Number of bagels = 5
Total cost of the bagels = $3 × 5 = $15

Now, let’s subtract the total cost from Olivia’s initial amount:
Olivia started with $23
She spent $15
Amount left = $23 - $15 = $8
So, Olivia has $8 left after buying the bagels.
```

You can also check out our code tutorial for creating both zero- and few-shot variants of [CoT prompts](https://mirascope.com/tutorials/prompt_engineering/text_based/chain_of_thought/) using Mirascope.

### 3. Self-Ask Prompt

This prompt encourages the model to process complex queries by asking itself clarifying questions, which it in turn answers step by step before arriving at the final conclusion.

Self-ask is great for tackling ambiguous or multi-faceted questions, ensuring the model considers all relevant aspects before responding.

Compared with CoT, Self-Ask is more focused on questioning and clarifying ambiguities before answering, since it prompts the model to identify gaps in understanding or missing details.

Example:

```plaintext
Using the Self-Ask method, when does monsoon season end in the state where area code 575 is located? If follow-up questions are needed, please ask and answer them before providing the final answer.
```

Response:

```plaintext
Are follow-up questions needed here: Yes.
Follow-up question: Which state is area code 575 located in?
Intermediate answer: The area code 575 is located in New Mexico.
Follow-up question: When does monsoon season end in New Mexico?
Intermediate answer: Monsoon season in New Mexico typically ends in mid-September.
Final Answer: Monsoon season in the state where area code 575 is located (New Mexico) typically ends in mid-September.
```

Our [self-ask prompt coding recipe](https://mirascope.com/tutorials/prompt_engineering/text_based/self_ask/) shows you how to implement both basic and enhanced (with dynamic example selection) versions.

### 4. Tree of Thought (ToT)

A [Tree-of-Thought Prompt](https://mirascope.com/blog/llm-prompt) allows a language model to explore multiple potential solutions or reasoning paths for a given task, rather than follow a single line of reasoning.

ToT prompts the model to evaluate different approaches and weigh the pros and cons of each in order to choose the optimal optimal solution. This enlists the model’s problem-solving capabilities by letting it consider a variety of options before arriving at the final answer.

This method’s problem-solving approach has three steps:

1. Generate different approaches to solving a problem.  
2. Evaluate the merits of each approach, considering both the advantages and disadvantages.  
3. Discard less viable paths and converge on the best solution based on its evaluation.

Example:

```plaintext
Design a new smartphone model for the mid-range market. Generate at least three different design approaches, evaluating the pros and cons of each, and then recommend the best design based on your analysis.
```

Response:

```plaintext
Approach 1: Minimalist Design
Pros: Simple, sleek design with fewer distractions. Lower production costs due to fewer components. Appeals to users who prefer clean, user-friendly interfaces.
Cons: Lacks premium features that may attract tech enthusiasts. Limited room for differentiation from other brands. May not appeal to customers who prioritize cutting-edge technology.

Approach 2: Camera-Centric Design
Pros: High-quality camera system with multiple lenses and advanced AI features for photography. Appeals to users who prioritize mobile photography and content creation. Strong marketing potential through the camera's performance.
Cons: Higher production costs due to the advanced camera hardware. Might sacrifice other features like battery life or overall performance. May alienate customers who don't prioritize camera quality.
Approach 3: Battery Life and Durability Focus

Pros: Large battery for extended usage, rugged build for durability, and water resistance. Appeals to users who need a reliable device for work, travel, or outdoor activities. Differentiates itself from other models based on reliability.
Cons: Bulky design, which may not be aesthetically appealing. Sacrifices some of the cutting-edge features like high refresh rate displays or advanced camera systems.
Final Conclusion:
After evaluating the pros and cons, the Camera-Centric Design seems the best option for the mid-range market. While it comes at a slightly higher cost, the advanced camera features will appeal to content creators and tech enthusiasts, making it a strong differentiator in a competitive space.
```

### 5. Chain of Verification (CoV)

This prompt improves an LLM’s response accuracy by implementing a self-verification process:

* After the LLM provides an initial answer to a query, the Chain of Verification prompts the model to create a set of verification questions based on the key facts in the initial response. These questions are designed to ensure that each piece of information provided is factually accurate and relevant to the original query.  
* Each verification question is then answered separately by the LLM, which "fact-checks" the original response. The answers to these questions help determine if the initial answer was correct or contained any errors.  
* Once the verification process is complete, the model uses the results from the fact-checking step to revise the initial response, ensuring the final answer is more accurate and reliable. If the verification reveals any errors, they are corrected in the final output.

CoV is focused on post-answer validation, revisiting the model’s initial output and systematically checking the facts rather than just reasoning through the process.

Example:

```plaintext
List five famous scientists and their primary field of contribution. Please make sure that all the facts are verified correctly by generating and answering verification questions for each scientist's field of contribution. After the verification process, update the list with any necessary corrections. This is very important.
```

Output:

```plaintext
Preliminary List of Scientists and Their Fields:
- Albert Einstein - Physics (Theory of Relativity)
- Marie Curie - Chemistry/Physics (Radioactivity)
- Isaac Newton - Physics/Mathematics (Classical Mechanics, Laws of Motion)
- Charles Darwin - Biology (Theory of Evolution)
- Niels Bohr - Physics (Quantum Mechanics)

Verification Questions
1. Albert Einstein:
Question: Is Einstein primarily known for contributions in the field of physics, specifically for his development of the theory of relativity?
Expected Answer: Yes, Einstein is renowned for his theories of special and general relativity, which revolutionized our understanding of space, time, and gravity.
2. Marie Curie:
Question: Did Marie Curie primarily contribute to both chemistry and physics through her pioneering work on radioactivity?
Expected Answer: Yes, Marie Curie won two Nobel Prizes—one in Physics (1903) for her work on radioactivity and one in Chemistry (1911) for her discovery of radium and polonium.
3. Isaac Newton:
Question: Is Newton’s primary contribution in the field of physics and mathematics, particularly with regard to the laws of motion and universal gravitation?
Expected Answer: Yes, Isaac Newton is most famous for his laws of motion and the law of universal gravitation, which laid the foundation for classical mechanics.
4. Charles Darwin:
Question: Is Darwin best known for his contributions to biology through his theory of evolution by natural selection?
Expected Answer: Yes, Charles Darwin's theory of evolution by natural selection is a cornerstone of modern biology.
5. Niels Bohr:
Question: Did Niels Bohr primarily contribute to the field of physics, particularly in the development of quantum mechanics and the structure of the atom?
Expected Answer: Yes, Niels Bohr made significant contributions to the development of quantum mechanics and the understanding of atomic structure, particularly with his model of the atom.

Verified List of Scientists and Their Fields:
- Albert Einstein - Physics (Theory of Relativity)
- Marie Curie - Chemistry/Physics (Radioactivity)
- Isaac Newton - Physics/Mathematics (Classical Mechanics, Laws of Motion)
- Charles Darwin - Biology (Theory of Evolution)
- Niels Bohr - Physics (Quantum Mechanics, Atomic Structure)
```

See our [coding tutorial](https://mirascope.com/tutorials/prompt_engineering/chaining_based/chain_of_verification/) for a complete example of building a CoV prompt using Python.

### 6. Self-Consistency

The self-consistency technique generates multiple answers through CoT prompting and then selects the most common or consistent answer.

This approach ensures accuracy and reliability, particularly in tasks involving complex reasoning like mathematics or symbolic problems.

How it works:

1. The LLM generates multiple responses to a single query, where each response is derived through a CoT reasoning process.  
2. The model then selects the most frequent answer from these multiple outputs, assuming that the most common answer is likely to be the most accurate. This avoids the risk of the model making an isolated error or generating a less accurate outlier.

Example:

```plaintext
Olivia has $23. She bought five bagels for $3 each. How much money does she have left? Please solve this problem by thinking step by step. Generate multiple answers using different approaches or considerations. After generating several responses, select the most frequent answer and explain why it is the best choice.
```

Response:

```plaintext
Step-by-step analysis:
Approach 1: Direct Subtraction Method
1. Initial money: Olivia has $23.
2. Cost of one bagel: Each bagel costs $3.
3. Total number of bagels: She buys 5 bagels.
4. Total cost of the bagels: 5 x 3 = 15 dollars.
5. Remaining money: 23 − 15 = 8 dollars.
Approach 2: Grouping method
1. Initial money: Olivia starts with $23.
2. Break down the expenses:
- Buying two bagels: 2 × 3 = 6 dollars.
- Buying three more bagels: 3 × 3 = 9 dollars.
3. Total cost: 6 + 9 = 15 dollars.
4. Remaining money: 23 − 15 = 8 dollars.
Approach 3: Counting backward
1. Start with $23.
2. Subtract $3 for each bagel:
- After buying the first bagel: 23 − 3 = 20.
- After the second bagel: 20 − 3 = 17.
- After the third bagel: 17 − 3 =14.
- After the fourth bagel: 14 − 3 = 11.
- After the fifth bagel: 11 − 3 = 8.
3. Olivia has $8 left.
Approach 4: Algebraic approach
Let x represent Olivia’s remaining money after buying 5 bagels.
1. Initial amount: $23.
2. Total cost: 3 × 5 = 15 dollars.
3. Equation: 23 − 15 = x.
4. Solve for x:x = 8.
Answer Evaluation:
All four approaches conclude that Olivia has $8 left.
Conclusion:
The most frequent and correct answer is $8. All approaches, whether direct subtraction, grouping, counting backward, or algebraic reasoning, reach the same result because they all properly account for the $15 spent on the bagels. This consistency makes $8 the best and accurate answer.

```

Our coding tutorial shows you how to construct both a basic version of the [self-consistency prompt](https://mirascope.com/tutorials/prompt_engineering/chaining_based/self_consistency/), as well as using automated answer extraction.

## Achieve Precision in Prompt Design with Mirascope

Ready to build smarter, more effective prompts? Mirascope allows you to construct advanced prompts for artificial intelligence applications using the Python you already know, and without needing to learn new, complex abstractions. Get started quickly building LLM-powered agents with our lightweight, modular toolkit.

You can find Mirascope code samples and tutorials both on our [documentation site](https://mirascope.com) and on our [GitHub page](https://github.com/mirascope/mirascope).
