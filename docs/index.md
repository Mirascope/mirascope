# Getting Started with Mirascope

Welcome to Mirascope! This guide will help you dive into building powerful LLM-powered applications with ease. We'll start with an interactive tutorial and then guide you through next steps to deepen your knowledge and understanding of Mirascope and all of its features.

## Interactive Web Search Agent Tutorial

Jump right in with our hands-on tutorial where you'll interact with a web search agent built using Mirascope. This will give you a practical taste of Mirascope's key features.

### Replit Environment

We've set up a Replit environment for you to start immediately without any local setup:

[Mirascope Getting Started Tutorial](https://replit.com/@willbakst/Mirascope-Getting-Started-Tutorial?v=1)

### How to Use the Replit

1. Open the Replit link above.
2. Click the "Fork" button to create your own copy of the Replit.
3. In the Secrets tab (lock icon on the left sidebar), add your OpenAI API key:
   - Key: `OPENAI_API_KEY`
   - Value: Your actual OpenAI API key
4. Click the "Run" button at the top of the Replit interface.
5. Interact with the agent in the console on the right side of the screen.

### Understanding the Code

The Replit contains a Python script that runs a Web Search Agent implemented using Mirascope, DuckDuckGo Search, BeautifulSoup, and Requests. Here's a breakdown of the key components:

- `constants.py`: Constant values used across the various other files.
- `tools.py`: The `web_search` and `parse_content` tools. These enable the agent to retrieve search results and parse them.
- `agent.py`: The main `WebSearchAgent` implementation of a streaming agent with access to the web.
- `main.py`: A simple script that runs the agent.

### Experimenting with the Agent

Try asking the agent various questions. It can:

- Answer general knowledge questions
- Provide summaries of current events
- Explain complex topics
- And much more!

The agent will use its web search capability when it needs additional information.

### Key Mirascope Features Demonstrated

This tutorial showcases several key Mirascope features:

1. **LLM Calls**: The `call` decorator simplifies interactions with LLM APIs.
2. **Prompt Templates**: Dynamic prompt creation using the `@prompt_template` decorator.
3. **Custom Tools**: Implementation of web search and content parsing tools.
4. **Streaming**: Real-time responses using Mirascope's streaming capabilities.
5. **Agent State Management**: Maintaining conversation history and context, including iteratively calling and inserting tools.

## Next Steps

Once you're comfortable with the tutorial, here are some next steps to deepen your Mirascope knowledge:

### Explore the Documentation

Dive into our comprehensive documentation to learn more about Mirascope's features:

- [Learn Mirascope](./learn/index.md): In-depth guides on all Mirascope features.
- [API Reference](./api/index.md): Detailed information on Mirascope's classes and functions.

### Try More Examples

Check out our Cookbook for more advanced examples and real-world applications:

- [Mirascope Cookbook](./cookbook/index.md): A collection of recipes for common LLM application patterns.

### Set Up Your Local Environment

To start building your own projects, set up Mirascope in your local environment:

```bash
pip install mirascope
pip install "mirascope[openai]"     # when using e.g. mirascope.core.openai
pip install "mirascope[anthropic]"  # when using e.g. mirascope.core.anthropic
```

We provide tags for extras for your convenience when using additional modules. These tags will ensure that you install all of the packages necessary for using the modules matching said tags.

### Join the Community

Connect with other Mirascope developers:

- [Slack Community](https://join.slack.com/t/mirascope-community/shared_invite/zt-2ilqhvmki-FB6LWluInUCkkjYD3oSjNA): Get support and share your projects.
- [GitHub](https://github.com/Mirascope/mirascope): Star us on GitHub, request features, report bugs, and contribute to the project!

We're excited to see what you'll build with Mirascope. Happy coding!
