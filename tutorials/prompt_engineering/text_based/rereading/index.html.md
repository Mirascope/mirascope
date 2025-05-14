# Rereading

<div class="admonition note">
<p class="admonition-title">Note</p>
<p>Our experiences indicate that re-reading is not as effective for newer, more powerful models such as Anthropic's 3.5 Sonnet or OpenAI's GPT-4o, although it remains effective in older models.</p>
</div>

[Rereading](https://arxiv.org/pdf/2309.06275) is a prompt engineering technique that simply asks the LLM to reread a question and repeats it. When working with older, less capable LLM models, rereading has shown improvements for all types of reasoning tasks (arithmetic, symbolic, commonsense).

<div class="admonition tip">
<p class="admonition-title">Mirascope Concepts Used</p>
<ul>
<li><a href="../../../../learn/prompts/">Prompts</a></li>
<li><a href="../../../../learn/calls/">Calls</a></li>
</ul>
</div>



```python
from mirascope.core import openai, prompt_template


@openai.call(model="gpt-4o-mini")
@prompt_template("{query} {reread}")
def call(query: str, reread_prompt: bool = False) -> openai.OpenAIDynamicConfig:
    return {
        "computed_fields": {
            "reread": f"Read the question again: {query}" if reread_prompt else "",
        }
    }


prompt = """A coin is heads up. aluino flips the coin. arthor flips the coin.
Is the coin still heads up? Flip means reverse."""

print(call(query=prompt, reread_prompt=True))
```

    To analyze the situation:
    
    1. The coin starts heads up.
    2. Aluino flips the coin, which reverses it to tails up.
    3. Arthor then flips the coin again, which reverses it back to heads up.
    
    So, after both flips, the coin is heads up again. The final answer is yes, the coin is still heads up.


This example demonstrates how to implement the Rereading technique using Mirascope. The `reread` computed field is added to the prompt when `reread_prompt` is set to `True`, instructing the LLM to read the question again.

## Benefits of Rereading

1. **Improved Comprehension**: Rereading can help the LLM better understand complex or nuanced questions.
2. **Enhanced Accuracy**: For older models, rereading has shown to improve accuracy across various reasoning tasks.
3. **Reinforcement**: Repeating the question can reinforce key details that might be overlooked in a single pass.
4. **Reduced Errors**: Rereading can help minimize errors that might occur due to misreading or misinterpreting the initial question.

<div class="admonition tip">
<p class="admonition-title">Effective Rereading</p>
<ul>
<li><strong>Use with Older Models</strong>: Rereading is most effective with older, less capable LLM models.</li>
<li><strong>Apply to Complex Questions</strong>: Consider using rereading for questions that involve multiple steps or complex reasoning.</li>
<li><strong>Combine with Other Techniques</strong>: Rereading can be used in conjunction with other prompt engineering techniques for potentially better results.</li>
<li><strong>Monitor Performance</strong>: Keep track of how rereading affects your model's performance, as its effectiveness may vary depending on the specific task and model used.</li>
<li><strong>Consider Model Capabilities</strong>: For newer, more advanced models, rereading might not provide significant benefits and could potentially be redundant.</li>
</ul>
</div>

By leveraging the Rereading technique, particularly with older LLM models, you may be able to improve the model's understanding and accuracy across various types of reasoning tasks. However, always consider the capabilities of your specific model when deciding whether to apply this technique.
