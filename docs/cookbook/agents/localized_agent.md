# Localized Agent

This recipe will show you how to use Nimble to make a simple Q&A ChatBot based on Google Maps data.

## Setup

We will need an API key for :

- [Nimble API Key](https://nimbleway.com/) or alternatively directly from [Google Maps API](https://developers.google.com/maps/documentation/places/web-service/search)

And of course, Mirascope.

??? tip "Mirascope Concepts Used"

    - [Prompts](../../learn/prompts.md)
    - [Calls](../../learn/calls.md)
    - [Tools](../../learn/tools.md)
    - [Dynamic Configuration](../../learn/dynamic_configuration.md)
    - [Agents](../../learn/agents.md)

!!! note "Background"

    In the past, users had to rely on search engines and manually browse through multiple web pages to research or answer questions. Large Language Models (LLMs) have revolutionized this process. They can efficiently utilize map data and extract relevant content. By leveraging this information, LLMs can quickly provide accurate answers to user queries, eliminating the need for active searching. Users can simply pose their questions and let the LLM work in the background, significantly streamlining the information retrieval process.

## Creating a Localized Recommender ChatBot

### Setup Tools

Let's start off with defining our tools `get_current_date`, `get_coordinates_from_location` , and `nimble_google_maps`  for our agent:

```python
--8<-- "examples/cookbook/agents/localized_agent.py:1:5"
--8<-- "examples/cookbook/agents/localized_agent.py:9:102"
```

A quick summary of each of the tools:

- `_get_current_date` - Gets the current date, this is relevant if the user wants to ask if a place is open or closed.
- `_get_coordinates_from_location` - Gets the latitude and longitude based on the user’s query using OSM’s Geolocation.
- `_nimble_google_maps` - Gets google maps information using the Nimble API.

### Creating the Agent

We then create our Agent, giving it the tools we defined and history for memory. As this agent functions as a ChatBot, we implement streaming to enhance the user experience:

```python
--8<-- "examples/cookbook/agents/localized_agent.py:6:9"
--8<-- "examples/cookbook/agents/localized_agent.py:13:15"
    ...
--8<-- "examples/cookbook/agents/localized_agent.py:103:124"
```

Since our tools are defined inside our agent, we need to use Mirascope `DynamicConfig` to give our LLM call access to tools.

### Creating our run function

Now it is time to create our `run` function. We will first prompt the user to ask a question. The LLM will continue to call tools until it has all the information needed to answer the user’s question:

```python
--8<-- "examples/cookbook/agents/localized_agent.py:13:15"
    ...
--8<-- "examples/cookbook/agents/localized_agent.py:126:151"
```

We use Mirascope utility functions `user_message_param`, `message_param`, and `tool_message_params` to easily update our history so the LLM is aware of which tools its called and what the next steps are.

### Results

```python
--8<-- "examples/cookbook/agents/localized_agent.py:154:175"
```

The more information we give the LLM from the Nimble API, the more specific of a recommendation the LLM can give, such as information about outside seating, dietary restrictions, cuisine, and more.

!!! tip "Additional Real-World Applications"

    - **Mobile Travel Companion**: Transform this example into a portable app for on-the-go recommendations during your travels."
    - **Smart Day Planner**: Discover nearby events and efficiently map out your itinerary, optimizing routes based on timing and proximity.
    - **Immersive Explorer**: Blend location awareness with visual recognition using a multimodal model to enhance your on-site experience."

When adapting this recipe, consider:

- Tailor the Nimble tool by pulling different information for your requirements.
- Give the LLM access to the web to access more detailed information.
- Connect the agent to a database for quicker data fetching.
