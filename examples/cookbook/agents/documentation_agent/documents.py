retrieved_dummy_docs = [
    {"id": 0, "text": "Bob eats burgers every day.", "semantic_score": 0.8},
    {"id": 1, "text": "Bob's favorite food is not pizza.", "semantic_score": 0.9},
    {"id": 2, "text": "I ate at In-N-Out with Bob yesterday", "semantic_score": 0.5},
    {"id": 3, "text": "Bob said his favorite food is burgers", "semantic_score": 0.9},
]

retrieved_mirascope_docs = [
    {
        "id": 0,
        "text": 'Calls\n\n??? api "API Documentation"\n\n    `mirascope.core.anthropic.call`\n\n    `mirascope.core.cohere.call`\n\n    `mirascope.core.gemini.call`\n\n    `mirascope.core.groq.call`\n\n    `mirascope.core.litellm.call`\n\n    `mirascope.core.mistral.call`\n\n    `mirascope.core.openai.call`\n\nThe `call` decorator is a core feature of the Mirascope library, designed to simplify and streamline interactions with various Large Language Model (LLM) providers. This powerful tool allows you to transform Python functions into LLM API calls with minimal boilerplate code while providing type safety and consistency across different providers.\n\nThe primary purpose of the call decorator is to:\n\n- Abstract away the complexities of different LLM APIs\n- Provide a unified interface for making LLM calls\n- Enable easy switching between different LLM providers\n- Enhance code readability and maintainability\n\nBy using the `call` decorator, you can focus on designing your prompts and handling the LLM responses, rather than dealing with the intricacies of each provider\'s API.',
        "document_title": "Streamlining LLM API Calls with the Mirascope `call` Decorator",
        "semantic_score": 0.8055069858410866,
    },
    {
        "id": 1,
        "text": "Best Practices\n\n- Provider Flexibility: Design functions to be provider-agnostic, allowing easy switching between different LLM providers for comparison or fallback strategies.\n- Provider-Specific Prompts: Tailor prompts to leverage unique features of specific providers when needed, using provider-specific `call` decorators. For example, Anthropic is known to handle prompts with XML particularly well.\n- Error Handling: Implement robust error handling to manage API failures, timeouts, or content policy violations, ensuring your application's resilience. Check out our documentation on using Tenacity for how to easily add retries to your error handling logic.\n- Streaming for Long Tasks: Utilize streaming for long-running tasks or when providing real-time updates to users, improving the user experience. Check out the `Streams` documentation for more details.\n- Modular Function Design: Break down complex tasks into smaller, modular functions that can be chained together, enhancing reusability and maintainability. Check out the `Chaining` documentation for more details.\n- Custom Clients: Leverage custom clients when working with self-hosted models or specific API configurations, allowing for greater flexibility in deployment scenarios. For example, you can use open-source models by serving OpenAI compatible endpoints (e.g. with `vLLM`, `Ollama`, etc).\n- Structured Outputs: Use `response_models` to ensure consistency and type safety when you need structured data from your LLM calls. Check out the `Response Models` documentation for more details.\n- Parameterized Calls: Take advantage of `call_params` to customoize model behavior without changing your core function logic.\n\nMastering the `call` decorator is the next step towards building robust LLM applications with Mirascope that are flexible, efficient, and adaptable to various providers and use cases.",
        "document_title": '"Enhancing LLM Applications with Mirascope: Leveraging Provider Flexibility, Error Handling, Streaming, Modular Design, Custom Clients, Structured Outputs, and Parameterized Calls"',
        "semantic_score": 0.7942346509974936,
    },
    {
        "id": 2,
        "text": "Chaining\n\nChaining in Mirascope allows you to combine multiple LLM calls or operations in a sequence to solve complex tasks. Mirascope's approach to chaining leverages dynamic configuration and computed fields, providing a unique and powerful way to create sophisticated LLM-powered applications.",
        "document_title": "Unlocking the Power of Computed Fields with Dynamic Chaining using Mirascope",
        "semantic_score": 0.789576916251624,
    },
    {
        "id": 3,
        "text": "Learn Mirascope\n\nThis section is designed to help you master Mirascope, a toolkit for building AI-powered applications with Large Language Models (LLMs).\n\nMirascope is a powerful, flexible, and user-friendly library that simplifies the process of working with LLMs. Whether you're building chatbots, content generators, or complex AI-driven agent systems, Mirascope provides the tools you need to streamline your development process and create powerful, robust applications.\n\nOur documentation is tailored for developers who have at least some experience with Python and LLMs. Whether you're coming from other development tool libraries or have worked directly with provider SDKs and APIs, Mirascope offers a familiar but enhanced experience.",
        "document_title": "Mastering Mirascope: Building AI-Powered Applications with Large Language Models",
        "semantic_score": 0.7885296079125218,
    },
    {
        "id": 4,
        "text": "Type Safety with Streams\n\nMirascope's `call` decorator provides proper type hints and safety when working with streams. When you enable streaming, the return type of your function will accurately reflect the stream type.\n\nYour IDE will recognize the response object when streaming as a provider-specific `BaseStream` instance and provide appropriate autocompletion and type checking for its methods and properties, improving your development experience when working with streamed LLM responses.",
        "document_title": '"Streamlining Development with Mirascope\'s Stream Handling: Enhancing Type Safety and Development Experience"',
        "semantic_score": 0.7883500164705622,
    },
    {
        "id": 5,
        "text": "Async\n\nAsynchronous programming in Mirascope allows you to perform non-blocking operations, which can significantly improve the performance of your applications, especially when dealing with I/O-bound tasks like making API calls to Large Language Models (LLMs). This guide will walk you through how to use async features across various aspects of Mirascope.",
        "document_title": '"Maximizing Performance with Asynchronous Programming in Mirascope: A Comprehensive Guide"',
        "semantic_score": 0.7807998289837746,
    },
    {
        "id": 6,
        "text": "How It Works\n\n1. Each step in the chain is defined as a separate function decorated with a Mirascope LLM call decorator (e.g., `@openai.call`).\n2. The functions return a dynamic configuration dictionary that includes `computed_fields`.\n3. These `computed_fields` can contain the results of previous steps, allowing you to pass information through the chain.",
        "document_title": '"Implementing a Dynamic Configuration Chain using the Mirascope LLM Call Decorator"',
        "semantic_score": 0.7803585823340917,
    },
    {
        "id": 7,
        "text": "Core Components\n\nMirascope is built around the following core components, each designed to handle specific aspects of LLM interaction and application development. Here's a quick overview with links to detailed documentation:\n\n1. Prompts: Learn how to create and manage prompts effectively.\n\n2. Calls: Understand how to make calls to LLMs using Mirascope.\n\n3. Streams: Explore streaming responses for real-time applications.\n\n4. Tools: Discover how to extend LLM capabilities with custom tools.\n\n5. Dynamic Configuration: Learn to adjust LLM behavior at runtime.\n\n6. Chaining: Understand the art of chaining multiple LLM calls for complex tasks.\n\n7. JSON Mode: Work with structured data responses from LLMs.\n\n8. Response Models: Define and use structured output models with automatic validation.\n\n9. Output Parsers: Process and transform custom LLM output structures effectively.\n\n10. Async: Maximize efficiecy with asynchronous programming.\n\n11. Evals: Apply core components to build evaluation strategies for your LLM applications.\n\n12. Agents: Put everything together to build advanced AI agents using Mirascope.",
        "document_title": "Mirascope Core Components Overview: A Comprehensive Guide",
        "semantic_score": 0.780333191030996,
    },
    {
        "id": 8,
        "text": 'Chaining Without Computed Fields\n\nWhile using computed fields is the recommended approach in Mirascope, you can also chain calls without them:\n\n```python\nfrom mirascope.core import openai, prompt_template\n\n\n@openai.call(model="gpt-3.5-turbo")\n@prompt_template("Summarize this text: {text}")\ndef summarize(text: str): ...\n\n\n@openai.call(model="gpt-3.5-turbo")\n@prompt_template("Translate this text to {language}: {summary}")\ndef translate(summary: str, language: str): ...\n\n\ndef summarize_and_translate(original_text: str):\n    summary = summarize(original_text)\n    translation = translate(summary.content, "french")\n    return translation.content\n```',
        "document_title": "Maximizing Efficiency in Mirascope: Chaining Calls without Computed Fields",
        "semantic_score": 0.7802017775236598,
    },
    {
        "id": 9,
        "text": "Best Practices\n\n- **Use Computed Fields**: Leverage computed fields for better traceability and debugging.\n- **Modular Design**: Break down complex tasks into smaller, reusable functions.\n- **Error Handling**: Implement robust error handling at each step of your chain.\n- **Use Response Models**: Structure your intermediate outputs for better type safety and easier processing. Check out the `Response Models` documentation for more details.\n- **Asynchronous Operations**: Utilize async programming for parallel processing when appropriate. Check out the `Async` documentation for more details.\n- **Testing**: Test each component of your chain individually as well as the entire chain.\n- **Logging**: Use the `model_dump()` method to log the entire chain's execution for debugging and analysis. This pairs well with custom middleware.\n\nBy mastering Mirascope's chaining techniques, you can create sophisticated LLM-powered applications that tackle complex, multi-step problems with greater accuracy, control, and traceability.",
        "document_title": '"Optimizing Chain Processing with Mirascope: Advanced Techniques for Efficiency and Traceability"',
        "semantic_score": 0.7775126749469117,
    },
]

retrieved_mirascope_openai_docs = [
    {
        "id": 0,
        "text": 'Calls\n\n??? api "API Documentation"\n\n    `mirascope.core.anthropic.call`\n\n    `mirascope.core.cohere.call`\n\n    `mirascope.core.gemini.call`\n\n    `mirascope.core.groq.call`\n\n    `mirascope.core.litellm.call`\n\n    `mirascope.core.mistral.call`\n\n    `mirascope.core.openai.call`\n\nThe `call` decorator is a core feature of the Mirascope library, designed to simplify and streamline interactions with various Large Language Model (LLM) providers. This powerful tool allows you to transform Python functions into LLM API calls with minimal boilerplate code while providing type safety and consistency across different providers.\n\nThe primary purpose of the call decorator is to:\n\n- Abstract away the complexities of different LLM APIs\n- Provide a unified interface for making LLM calls\n- Enable easy switching between different LLM providers\n- Enhance code readability and maintainability\n\nBy using the `call` decorator, you can focus on designing your prompts and handling the LLM responses, rather than dealing with the intricacies of each provider\'s API.',
        "document_title": "Streamlining LLM API Calls with the Mirascope `call` Decorator",
        "semantic_score": 0.83407328653059,
    },
    {
        "id": 1,
        "text": "Best Practices\n\n- Provider Flexibility: Design functions to be provider-agnostic, allowing easy switching between different LLM providers for comparison or fallback strategies.\n- Provider-Specific Prompts: Tailor prompts to leverage unique features of specific providers when needed, using provider-specific `call` decorators. For example, Anthropic is known to handle prompts with XML particularly well.\n- Error Handling: Implement robust error handling to manage API failures, timeouts, or content policy violations, ensuring your application's resilience. Check out our documentation on using Tenacity for how to easily add retries to your error handling logic.\n- Streaming for Long Tasks: Utilize streaming for long-running tasks or when providing real-time updates to users, improving the user experience. Check out the `Streams` documentation for more details.\n- Modular Function Design: Break down complex tasks into smaller, modular functions that can be chained together, enhancing reusability and maintainability. Check out the `Chaining` documentation for more details.\n- Custom Clients: Leverage custom clients when working with self-hosted models or specific API configurations, allowing for greater flexibility in deployment scenarios. For example, you can use open-source models by serving OpenAI compatible endpoints (e.g. with `vLLM`, `Ollama`, etc).\n- Structured Outputs: Use `response_models` to ensure consistency and type safety when you need structured data from your LLM calls. Check out the `Response Models` documentation for more details.\n- Parameterized Calls: Take advantage of `call_params` to customoize model behavior without changing your core function logic.\n\nMastering the `call` decorator is the next step towards building robust LLM applications with Mirascope that are flexible, efficient, and adaptable to various providers and use cases.",
        "document_title": '"Enhancing LLM Applications with Mirascope: Leveraging Provider Flexibility, Error Handling, Streaming, Modular Design, Custom Clients, Structured Outputs, and Parameterized Calls"',
        "semantic_score": 0.8286298220674264,
    },
    {
        "id": 2,
        "text": 'Basic Agent Structure\n\nLet\'s start by creating a simple agent using Mirascope. We\'ll build a basic Librarian agent that can engage in conversations and maintain a history of interactions.\n\n```python\nfrom mirascope.core import openai, prompt_template\nfrom openai.types.chat import ChatCompletionMessageParam\nfrom pydantic import BaseModel\n\n\nclass Librarian(BaseModel):\n    history: list[ChatCompletionMessageParam] = []\n\n    @openai.call(model="gpt-4o-mini")\n    @prompt_template(\n        """\n        SYSTEM: You are a helpful librarian assistant.\n        MESSAGES: {self.history}\n        USER: {query}\n        """\n    )\n    def _call(self, query: str) -> openai.OpenAIDynamicConfig:\n        ...\n\n    def run(self):\n        while True:\n            query = input("User: ")\n            if query.lower() == "exit":\n                break\n\n            response = self._call(query)\n            print(f"Librarian: {response.content}")\n\n            if response.user_message_param:\n                self.history.append(response.user_message_param)\n            self.history.append(response.message_param)\n\n\nlibrarian = Librarian()\nlibrarian.run()\n```\n\nThis basic structure demonstrates some key concepts we\'ve covered in previous sections:\n\n- **State Management**: We use a Pydantic `BaseModel` to define our agent\'s state, in this case, the chat history as a list of message parameters.\n- **Core Logic**: The `_call` method encapsulates the main logic of our agent. It uses the `@openai.call` decorator to interface with the LLM.\n- **Prompt Engineering**: We use a multi-part prompt that includes a system message, conversation history, and the current user query.\n- **Accessed Attribute Injection**: We directly access and inject the `self.history` messages list.\n- **Conversation Loop**: The `run` method implements a simple loop that takes user input, processes it through the `_call` method, and updates the conversation history.\n\nThis basic agent can engage in conversations about books, maintaining context through its history. However, it doesn\'t yet have any special capabilities beyond what the base LLM can do. In the next section, we\'ll enhance our Librarian by adding tools, allowing it to perform more specific tasks related to book management.',
        "document_title": "Creating a Conversational Librarian Agent with Mirascope: A Comprehensive Guide",
        "semantic_score": 0.8279234194993406,
    },
    {
        "id": 3,
        "text": 'Chaining Without Computed Fields\n\nWhile using computed fields is the recommended approach in Mirascope, you can also chain calls without them:\n\n```python\nfrom mirascope.core import openai, prompt_template\n\n\n@openai.call(model="gpt-3.5-turbo")\n@prompt_template("Summarize this text: {text}")\ndef summarize(text: str): ...\n\n\n@openai.call(model="gpt-3.5-turbo")\n@prompt_template("Translate this text to {language}: {summary}")\ndef translate(summary: str, language: str): ...\n\n\ndef summarize_and_translate(original_text: str):\n    summary = summarize(original_text)\n    translation = translate(summary.content, "french")\n    return translation.content\n```',
        "document_title": "Maximizing Efficiency in Mirascope: Chaining Calls without Computed Fields",
        "semantic_score": 0.824450579422155,
    },
    {
        "id": 4,
        "text": 'Basic Usage and Syntax\n\nThe basic syntax for using the call decorator is straightforward:\n\n```python\nfrom mirascope.core import openai, prompt_template\n\n\n@openai.call("gpt-4o-mini")\n@prompt_template("Recommend a {genre} book")\ndef recommend_book(genre: str):\n    ...\n\nresponse = recommend_book("fantasy")\nprint(response.content)\n```\n\nIn this example, we\'re using OpenAI\'s `gpt-4o-mini` model to generate a book recommendation for a user-specified genre. The call decorator transforms the `recommend_book` function into an LLM API call. The function arguments are automatically injected into the prompt defined in the `@prompt_template` decorator.\n\n!!! info "Function Body"\n\n    In the above example, we\'ve used an ellipsis (`...`) for the function body, which returns `None`. If you\'d like, you can always explicitly `return None` to be extra clear. For now, you can safely ignore how we use the function body, which we cover in more detail in the documentation for dynamic configuration.',
        "document_title": '"Book Recommendations Generated by OpenAI\'s GPT-4o-mini Model"',
        "semantic_score": 0.8231210506584766,
    },
    {
        "id": 5,
        "text": 'Basic Usage and Syntax\n\nTo use streaming with Mirascope, you simply need to set the `stream` parameter to `True` in your `call` decorator. Here\'s a basic example:\n\n```python\nfrom mirascope.core import openai, prompt_template\n\n\n@openai.call(model="gpt-4o-mini", stream=True)\n@prompt_template("Recommend a {genre} book")\ndef recommend_book(genre: str):\n    ...\n\n\nfor chunk, _ in recommend_book("fantasy"):\n    print(chunk.content, end="", flush=True)\n```\n\nIn this example, the recommendation will be printed to the console as it\'s being generated, providing a real-time generation experience.',
        "document_title": "Real-Time Streaming Generation with Mirascope: A Comprehensive Guide and Basic Example",
        "semantic_score": 0.8229909528289471,
    },
    {
        "id": 6,
        "text": 'Error Handling\n\nWhen making LLM calls, it\'s important to handle potential errors. Mirascope preserves the original error messages from providers, allowing you to catch and handle them appropriately:\n\n```python\nfrom openai import OpenAIError\nfrom mirascope.core import openai, prompt_template\n\n\n@openai.call(model="gpt-4o-mini")\n@prompt_template("Recommend a {genre} book")\ndef recommend_book(genre: str):\n    ...\n\n\ntry:\n    response = recommend_book("fantasy")\n    print(response.content)\nexcept OpenAIError as e:\n    print(f"Error: {str(e)}")\n```\n\nBy catching provider-specific errors, you can implement appropriate error handling and fallback strategies in your application. You can of course always catch the base `Exception` instead of provider-specific exceptions.',
        "document_title": "Error Handling in LLM Calls with Mirascope: Best Practices and Guidelines",
        "semantic_score": 0.8223634414539764,
    },
    {
        "id": 7,
        "text": 'Custom Client\n\nMirascope allows you to use custom clients when making calls to LLM providers. This feature is particularly useful when you need to use specific client configurations, handle authentication in a custom way, or work with self-hosted models.\n\nTo use a custom client, you can pass it to the `call` decorator using the `client` parameter. Here\'s an example using a custom OpenAI client:\n\n```python\nfrom openai import OpenAI\nfrom mirascope.core import openai, prompt_template\n\n# Create a custom OpenAI client\ncustom_client = OpenAI(\n    api_key="your-api-key",\n    organization="your-organization-id",\n    base_url="https://your-custom-endpoint.com/v1"\n)\n\n\n@openai.call(model="gpt-4o-mini", client=custom_client)\n@prompt_template("Recommend a {genre} book")\ndef recommend_book(genre: str):\n    ...\n\n\nresponse = recommend_book("fantasy")\nprint(response.content)\n```\n\nAny custom client is supported so long as it has the same API as the original base client.',
        "document_title": "Leveraging Custom Clients for Advanced API Integration in Mirascope",
        "semantic_score": 0.8215701931438076,
    },
    {
        "id": 8,
        "text": "Learn Mirascope\n\nThis section is designed to help you master Mirascope, a toolkit for building AI-powered applications with Large Language Models (LLMs).\n\nMirascope is a powerful, flexible, and user-friendly library that simplifies the process of working with LLMs. Whether you're building chatbots, content generators, or complex AI-driven agent systems, Mirascope provides the tools you need to streamline your development process and create powerful, robust applications.\n\nOur documentation is tailored for developers who have at least some experience with Python and LLMs. Whether you're coming from other development tool libraries or have worked directly with provider SDKs and APIs, Mirascope offers a familiar but enhanced experience.",
        "document_title": "Mastering Mirascope: Building AI-Powered Applications with Large Language Models",
        "semantic_score": 0.8201184693633962,
    },
    {
        "id": 9,
        "text": "Core Components\n\nMirascope is built around the following core components, each designed to handle specific aspects of LLM interaction and application development. Here's a quick overview with links to detailed documentation:\n\n1. Prompts: Learn how to create and manage prompts effectively.\n\n2. Calls: Understand how to make calls to LLMs using Mirascope.\n\n3. Streams: Explore streaming responses for real-time applications.\n\n4. Tools: Discover how to extend LLM capabilities with custom tools.\n\n5. Dynamic Configuration: Learn to adjust LLM behavior at runtime.\n\n6. Chaining: Understand the art of chaining multiple LLM calls for complex tasks.\n\n7. JSON Mode: Work with structured data responses from LLMs.\n\n8. Response Models: Define and use structured output models with automatic validation.\n\n9. Output Parsers: Process and transform custom LLM output structures effectively.\n\n10. Async: Maximize efficiecy with asynchronous programming.\n\n11. Evals: Apply core components to build evaluation strategies for your LLM applications.\n\n12. Agents: Put everything together to build advanced AI agents using Mirascope.",
        "document_title": "Mirascope Core Components Overview: A Comprehensive Guide",
        "semantic_score": 0.8173439699130355,
    },
]

retrieved_mirascope_ollama_docs = [
    {
        "id": 0,
        "text": 'Custom Client\n\nMirascope allows you to use custom clients when making calls to LLM providers. This feature is particularly useful when you need to use specific client configurations, handle authentication in a custom way, or work with self-hosted models.\n\nTo use a custom client, you can pass it to the `call` decorator using the `client` parameter. Here\'s an example using a custom OpenAI client:\n\n```python\nfrom openai import OpenAI\nfrom mirascope.core import openai, prompt_template\n\n# Create a custom OpenAI client\ncustom_client = OpenAI(\n    api_key="your-api-key",\n    organization="your-organization-id",\n    base_url="https://your-custom-endpoint.com/v1"\n)\n\n\n@openai.call(model="gpt-4o-mini", client=custom_client)\n@prompt_template("Recommend a {genre} book")\ndef recommend_book(genre: str):\n    ...\n\n\nresponse = recommend_book("fantasy")\nprint(response.content)\n```\n\nAny custom client is supported so long as it has the same API as the original base client.',
        "document_title": "Leveraging Custom Clients for Advanced API Integration in Mirascope",
        "semantic_score": 0.7834900905480026,
    },
    {
        "id": 1,
        "text": "Using LLMs as Judges\n\nOne powerful approach to evaluating LLM outputs is to use other LLMs as judges. This method leverages the language understanding capabilities of LLMs to perform nuanced evaluations that might be difficult to achieve with hardcoded criteria.",
        "document_title": '"Utilizing Legal Language Models as Judges for Evaluating Legal Language Model Outputs"',
        "semantic_score": 0.7479278111931363,
    },
    {
        "id": 2,
        "text": "Tools\n\nTools are defined functions that a Large Language Model (LLM) can invoke to extend its capabilities. This greatly enhances the capabilities of LLMs by allowing them to perform specific tasks, access external data, interact with other systems, and more. This feature enables the create of more dynamic and interactic LLM applications.\n\n!!! info \"How Tools Are Called\"\n\n    When an LLM decides to use a tool, it indicates the tool name and argument values in its response. It's important to note that the LLM doesn't actually execute the function; instead, you are responsible for calling the tool and (optionally) providing the output back to the LLM in a subsequent interaction. For more details on such iterative tool-use flows, checkout our Agents documentation.\n\nMirascope provides a provider-agnostic way to define tools, which can be used across all supported LLM providers without modification.",
        "document_title": "Enhancing LLM Capabilities with Tools: A Comprehensive Guide",
        "semantic_score": 0.7463405594690803,
    },
    {
        "id": 3,
        "text": 'Basic Usage and Syntax\n\nThe basic syntax for using the call decorator is straightforward:\n\n```python\nfrom mirascope.core import openai, prompt_template\n\n\n@openai.call("gpt-4o-mini")\n@prompt_template("Recommend a {genre} book")\ndef recommend_book(genre: str):\n    ...\n\nresponse = recommend_book("fantasy")\nprint(response.content)\n```\n\nIn this example, we\'re using OpenAI\'s `gpt-4o-mini` model to generate a book recommendation for a user-specified genre. The call decorator transforms the `recommend_book` function into an LLM API call. The function arguments are automatically injected into the prompt defined in the `@prompt_template` decorator.\n\n!!! info "Function Body"\n\n    In the above example, we\'ve used an ellipsis (`...`) for the function body, which returns `None`. If you\'d like, you can always explicitly `return None` to be extra clear. For now, you can safely ignore how we use the function body, which we cover in more detail in the documentation for dynamic configuration.',
        "document_title": '"Book Recommendations Generated by OpenAI\'s GPT-4o-mini Model"',
        "semantic_score": 0.7453798131741882,
    },
    {
        "id": 4,
        "text": "librarian = Librarian()\nlibrarian.run()\n```\n\nThis updated Librarian agent demonstrates several important concepts for integrating tools:\n\n- **Tool Definition**: We define tools as functions, which automatically get turned into `BaseTool` types. We can then access the original function through the returned tool's `call` method.\n- **Tool Configuration**: In the `_call` method, we return a dictionary with a `\"tools\"` key, listing the available tools for the LLM to use. This enables us to provide the LLM call with tools that have access to internal attributes through `self`, which makes implementing tools that dynamically update internal state a breeze.\n- **Tool Execution**: The `_step` method checks for tool calls in the response and executes them using the `call` method.\n- **Tool Result Reinsertion**: We use the `response.tool_message_params` classmethod to format the tool results and append them to the conversation history. This method works across different LLM providers, ensuring our agent remains provider-agnostic.\n- **Recursive Handling**: If tools were used, we recursively call `_step` to allow the LLM to process the tool results and potentially use more tools. At each subsequent step we are taking advantage of empty messages to exclude the user message while the LLM is calling tools. When the LLM is done calling tools we return the final response.\n\nThis structure allows our Librarian to use tools to manage a book collection while maintaining a coherent conversation. The LLM can decide when to use tools based on the user's query, and the results of those tool uses are fed back into the conversation for further processing.\n\nBy integrating tools in this way, we've significantly enhanced our agent's capabilities while keeping the implementation flexible and provider-agnostic. In the next section, we'll explore how to add streaming capabilities to our agent, allowing for more responsive interactions.",
        "document_title": '"Empowering Conversational Agents: Integrating Tools for Enhanced Book Collection Management and Flexible Execution"',
        "semantic_score": 0.7450439338939733,
    },
    {
        "id": 5,
        "text": 'Streaming in Agents\n\nStreaming allows agents to provide real-time responses, which can be particularly nice for long-running tasks. By implementing streaming in our Librarian agent, we can create a more responsive and interactive experience. Let\'s update our agent to support streaming responses and handle streamed tool calls.\n\nFirst, we\'ll modify the `_call` method to enable streaming:\n\n```python hl_lines="4"\nclass Librarian(BaseModel):\n    ...\n\n    @openai.call(model="gpt-4o-mini", stream=True)\n    @prompt_template("...")\n    def _call(self, query: str) -> openai.OpenAIDynamicConfig:\n        return {"tools": [self.add_book, self.remove_book]}\n```\n\nNow, let\'s update the `_step` method to handle streaming:\n\n```python hl_lines="4 8"\ndef _step(self, query: str) -> str:\n    response = self._call(query)\n    tools_and_outputs = []\n    for chunk, tool in response:\n        if tool:\n            tools_and_outputs.append((tool, tool.call()))\n        else:\n            print(chunk.content, end="", flush=True)\n\n    if response.user_message_param:\n        self.history.append(response.user_message_param)\n    self.history.append(response.message_param)\n    if tools_and_outputs:\n        self.history += response.tool_message_params(tools_and_outputs)\n        return self._step("")\n    else:\n        return response.content\n```\n\nFinally, let\'s update the `run` method to handle the update to `_step`, which now prints the content of each chunk during the stream internally:\n\n```python hl_lines="7 8 9"\ndef run(self):\n    while True:\n        query = input("User: ")\n        if query.lower() == "exit":\n            break\n\n        print("Librarian: ", end="", flush=True)\n        self._step(query)\n        print("")\n```\n\nThese changes implement streaming in our Librarian agent:\n\n- **Streaming Configuration**: We add `stream=True` to the `@openai.call` decorator in the `_call` method.\n- **Real-time Output**: We print chunk content as it\'s received, providing immediate feedback to the user.\n- **Tool Handling**: Tool calls are processed in real-time as they\'re received in the stream. The results are collected and can be used for further processing.',
        "document_title": "Enhancing Real-Time Responses and Dynamic Tool Configuration in the Librarian Agent through Streaming Technology",
        "semantic_score": 0.744794636469408,
    },
    {
        "id": 6,
        "text": "Best Practices\n\n- **Use Clear Field Names**: Choose descriptive names for your model fields to guide the LLM's output.\n- **Provide Field Descriptions**: Use Pydantic's `Field` with descriptions to give the LLM more context.\n- **Start Simple**: Begin with basic types and gradually increase complexity as needed.\n- **Handle Errors Gracefully**: Implement proper error handling and consider using retry mechanisms.\n- **Leverage JSON Mode**: When possible, use `json_mode=True` for better type support and consistency.\n- **Test Thoroughly**: Validate your Response Models across different inputs and edge cases.\n\nBy leveraging Response Models effectively, you can create more robust, type-safe, and maintainable LLM-powered applications with Mirascope.",
        "document_title": '"Optimizing LLM-Powered Applications: Best Practices for Developing Robust and Maintainable Response Models"',
        "semantic_score": 0.7416758670761349,
    },
    {
        "id": 7,
        "text": "Advanced Techniques\n\n- **Asynchronous Operations**: Leverage Python's asyncio to handle multiple operations concurrently, improving efficiency for I/O-bound tasks.\n- **Multi-Provider Setups**: Use different LLM providers for specialized tasks within your agent system, taking advantage of each provider's strengths.\n- **Dynamic Tool Generation**: Use `BaseToolKit` to generate tools dynamically based on the current state or context of the conversation.\n- **Hierarchical Agents**: Implement a hierarchy of agents, with higher-level agents delegating tasks to more specialized sub-agents. Check out our cookbook recipe on implementing a blog writing agent for an example of how to implement an Agent Executor.\n- **Adaptive Behavior**: Implement mechanisms for your agent to learn from interactions and adjust its behavior over time, such as fine-tuning prompts or adjusting tool selection strategies.\n\nBy following these best practices and leveraging advanced techniques, you can create sophisticated, reliable, and efficient agent systems with Mirascope. Remember to continuously test and refine your agents based on real-world performance and user feedback.\n\nAs you explore more complex agent architectures, consider implementing safeguards, such as content filtering or output validation, to ensure your agents behave ethically and produce appropriate responses. Always monitor your agents' performance and be prepared to make adjustments as needed.",
        "document_title": "Advanced Techniques for Developing Agent Systems",
        "semantic_score": 0.7412537181685909,
    },
    {
        "id": 8,
        "text": 'Custom Messages\n\nYou can completely override the default messages generated from the prompt template by providing custom messages.\n\n```python\nfrom mirascope.core import openai\n\n@openai.call("gpt-4o-mini")\ndef recommend_book(genre: str, style: str) -> openai.OpenAIDynamicConfig:\n    return {\n        "messages": [\n            {"role": "system", "content": "You are a helpful book recommender."},\n            {"role": "user", "content": f"Recommend a {genre} book in the style of {style}."},\n        ]\n    }\n\nresponse = recommend_book("science fiction", "cyberpunk")\nprint(response.content)\n```\n\nWhen using custom messages, the prompt template is ignored and not required.\n\n!!! warning "No Longer Provider-Agnostic"\n\n    When writing your own custom messages, these messages must be written specifically for the provider you are using. This makes switching providers more of a hassle; however, there may be new features that our prompt template parsing does not currently support, which you will always be able to access through custom messages.',
        "document_title": '"Personalized Book Recommendations: Curated Selections for Every Reader"',
        "semantic_score": 0.7406841497239197,
    },
    {
        "id": 9,
        "text": "Best Practices\n\n- Provider Flexibility: Design functions to be provider-agnostic, allowing easy switching between different LLM providers for comparison or fallback strategies.\n- Provider-Specific Prompts: Tailor prompts to leverage unique features of specific providers when needed, using provider-specific `call` decorators. For example, Anthropic is known to handle prompts with XML particularly well.\n- Error Handling: Implement robust error handling to manage API failures, timeouts, or content policy violations, ensuring your application's resilience. Check out our documentation on using Tenacity for how to easily add retries to your error handling logic.\n- Streaming for Long Tasks: Utilize streaming for long-running tasks or when providing real-time updates to users, improving the user experience. Check out the `Streams` documentation for more details.\n- Modular Function Design: Break down complex tasks into smaller, modular functions that can be chained together, enhancing reusability and maintainability. Check out the `Chaining` documentation for more details.\n- Custom Clients: Leverage custom clients when working with self-hosted models or specific API configurations, allowing for greater flexibility in deployment scenarios. For example, you can use open-source models by serving OpenAI compatible endpoints (e.g. with `vLLM`, `Ollama`, etc).\n- Structured Outputs: Use `response_models` to ensure consistency and type safety when you need structured data from your LLM calls. Check out the `Response Models` documentation for more details.\n- Parameterized Calls: Take advantage of `call_params` to customoize model behavior without changing your core function logic.\n\nMastering the `call` decorator is the next step towards building robust LLM applications with Mirascope that are flexible, efficient, and adaptable to various providers and use cases.",
        "document_title": '"Enhancing LLM Applications with Mirascope: Leveraging Provider Flexibility, Error Handling, Streaming, Modular Design, Custom Clients, Structured Outputs, and Parameterized Calls"',
        "semantic_score": 0.7395536852345135,
    },
]
