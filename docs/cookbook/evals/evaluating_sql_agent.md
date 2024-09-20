# Evaluating Generating SQL with LLM

In this recipe, we will be using taking our [SQL Agent](../agents/sql_agent.md) example and running evaluations on LLM call. We will be exploring various different evaluations we can run to ensure quality and expected behavior.

??? tip "Mirascope Concepts Used"

    - [Prompts](../../learn/prompts.md)
    - [Calls](../../learn/calls.md)
    - [Tools](../../learn/tools.md)
    - [Async](../../learn/async.md)
    - [Evals](../../learn/evals.md)

??? note "Check out the SQL Agent Cookbook"

    We will be using our `LibrarianAgent` for our evaluations. For a detailed explanation regarding this code snippet, refer to the [SQL Agent Cookbook](../agents/sql_agent.md).

## Evaluating the prompt using a golden dataset

One effective approach is to establish a golden dataset that the prompt must successfully pass. We'll leverage `pytest` for this purpose, as it offers numerous testing conveniences.

```python
--8<-- "examples/cookbook/agents/sql_agent/test_agent.py:4:6"
--8<-- "examples/cookbook/agents/sql_agent/test_agent.py:21:97"
```

The golden dataset serves as our test fixtures, allowing us to verify basic text-to-SQL conversions and ensure our Agent maintains this functionality.

As we expand our tools or enhance our prompt, we should consistently implement additional prompt regression tests to maintain quality and functionality.

!!! note "Tip"

    SQL queries can get complex so be sure to add very specific tests, especially for mutable operations like INSERTS, UPDATES, and DELETES.

## Evaluating conversations

With the above techniques, we've shown how to evaluate simple input and output pairs, but we also want to test conversations with history. We can define some messages we want the LLM to have and get some expected output, like so:

```python
--8<-- "examples/cookbook/agents/sql_agent/test_agent.py:7:11"
--8<-- "examples/cookbook/agents/sql_agent/test_agent.py:98:117"


@pytest.mark.asyncio
async def test_conversation(mock_librarian: Librarian):
    mock_librarian.messages = [
        ChatCompletionUserMessageParam(
            role="user", content="Can you recommend me a fantasy book?"
        ),
        ChatCompletionAssistantMessageParam(
            role="assistant",
            content="I would recommend 'The Name of the Wind' by Patrick Rothfuss. It’s the first book in 'The Kingkiller Chronicle' series and features a beautifully written story about a gifted young man who grows up to be a legendary figure. It's filled with magic, adventure, and rich character development. I believe you'll enjoy it! Would you like to add it to your reading list?",
        ),
    ]
    response = await mock_librarian._step("Can you add it to my reading list?")
    async for _, tool in response:
        query = tool.args.get("query", "") if tool else ""
        assert (
            query
            == "INSERT INTO ReadingList (title, status) VALUES ('The Name of the Wind', 'Not Started');"
        )
```

We expect that the LLM understands what "it" means in this case. If history was not working, then the LLM would not know what "it" refers to and would not be able to use the tool properly. This is particular useful because we can now test user flows easily to make sure certain flows behave properly.

Next, we'll be taking a look at using LLMs as judges for testing the tone we expect the LLM to take.

## LLMs as judges

With tools, it's easy to do an equality comparison to check that the LLM outputs proper SQL, but tone is a bit more complex. Thankfully, using LLMs makes this much simpler. We can use the LLM to evaluate the `friendliness` of the LLM and adjust the prompt as necessary.

```python
--8<-- "examples/cookbook/agents/sql_agent/test_agent.py:1:1"

--8<-- "examples/cookbook/agents/sql_agent/test_agent.py:12:12"
--8<-- "examples/cookbook/agents/sql_agent/test_agent.py:15:22"
--8<-- "examples/cookbook/agents/sql_agent/test_agent.py:119:205"
```

 Similar to the conversations test, we simulate a user interaction by passing a messages array to a mock librarian. To assess the friendliness of this response, we utilize a custom `FriendlinessEvaluator`, which is a Mirascope `BasePrompt` that scores friendliness on a scale from 1 to 5 based on specific criteria. Leveraging Mirascope's model-agnostic capabilities, we send this evaluation prompt to both GPT-4 and Claude 3.5 Sonnet and average out these results.


 When adapting this recipe to your specific use-case, consider the following:

- Experiment with the prompt, add specific examples to the `FriendlinessEvaluator` for more accurate evaluations
- Experiment with the call prompt, add more examples of friendly conversation or persona.
- Add evaluations for retrieval if you're using RAG, or evaluations for business metrics.
e
