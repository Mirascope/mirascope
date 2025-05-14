# Rephrase and Respond

[Rephrase and respond](https://arxiv.org/pdf/2311.04205) (RaR) is a prompt engineering technique which involves asking the LLM to rephrase and expand upon the question before responding. RaR has shown improvements across all types of prompts, but we have personally found that RaR is most effective for shorter and vaguer prompts.

<div class="admonition tip">
<p class="admonition-title">Mirascope Concepts Used</p>
<ul>
<li><a href="../../../../learn/prompts/">Prompts</a></li>
<li><a href="../../../../learn/calls/">Calls</a></li>
</ul>
</div>



```python
from mirascope.core import openai, prompt_template

rar_augment = "\nRephrase and expand the question, and respond."


@openai.call(model="gpt-4o-mini")
@prompt_template("{query} {rar_augment}")
def call(query: str, rar_prompt: bool = False) -> openai.OpenAIDynamicConfig:
    return {
        "computed_fields": {
            "rar_augment": rar_augment if rar_prompt else "",
        }
    }


prompt = """A coin is heads up. aluino flips the coin. arthor flips the coin.
Is the coin still heads up? Flip means reverse."""

print(call(query=prompt, rar_prompt=True))
```

    ### Rephrased and Expanded Question:
    
    A coin starts with the heads side facing up. If Aluino flips the coin, it will land with the tails side facing up. Then Arthur flips the coin again. After these two sequences of flips, can we say that the coin is still heads up? 
    
    ### Response:
    
    To analyze the scenario, let's break down the actions step by step:
    
    1. **Initial State**: The coin starts with the heads side facing up.
       
    2. **Aluino Flips the Coin**: When Aluino flips the coin, it reverses its position. Since the coin initially was heads up, after Aluino's flip, the coin will now be tails up.
    
    3. **Arthur Flips the Coin**: Next, Arthur takes his turn to flip the coin. Given that the current state of the coin is tails up, flipping it will reverse it again, resulting in the coin now being heads up.
    
    At the end of these actions, after both Aluino and Arthur have flipped the coin, the final state of the coin is heads up once more. Thus, the answer to the question is: 
    
    **No, after Aluino flips it, the coin is tails up; however, after Arthur flips it again, the coin is heads up once more.**


This example demonstrates how to implement the Rephrase and Respond technique using Mirascope. The `rar_augment` variable contains the instruction for the LLM to rephrase and expand the question before responding. This instruction is added to the end of the prompt when `rar_prompt` is set to `True`.

## Benefits of Rephrase and Respond

1. **Improved Understanding**: By rephrasing the question, the LLM demonstrates and often improves its understanding of the query.
2. **Clarity**: The rephrasing can help clarify ambiguous or vague queries.
3. **Context Expansion**: The expansion part of RaR allows the LLM to consider additional relevant context.
4. **Better Responses**: The combination of rephrasing and expanding often leads to more comprehensive and accurate responses.

<div class="admonition tip">
<p class="admonition-title">Effective Rephrase and Respond</p>
<ul>
<li><strong>Use with Shorter Prompts</strong>: RaR is particularly effective with shorter or vaguer prompts that benefit from expansion.</li>
<li><strong>Allow for Flexibility</strong>: The rephrasing may interpret the question slightly differently, which can lead to new insights.</li>
<li><strong>Review the Rephrasing</strong>: Pay attention to how the LLM rephrases the question, as it can provide insights into the model's understanding.</li>
<li><strong>Iterative Refinement</strong>: If the rephrasing misses key points, consider refining your original prompt.</li>
<li><strong>Combine with Other Techniques</strong>: RaR can be used in conjunction with other prompt engineering techniques for even better results.</li>
</ul>
</div>

By leveraging the Rephrase and Respond technique, you can often obtain more thorough and accurate responses from the LLM, especially for queries that benefit from additional context or clarification.

