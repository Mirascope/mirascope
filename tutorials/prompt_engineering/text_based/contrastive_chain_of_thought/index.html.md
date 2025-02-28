# Contrastive Chain of Thought

[Contrastive Chain of Thought](https://arxiv.org/pdf/2311.09277) is an extension of [Chain of Thought](https://arxiv.org/abs/2201.11903) which involves adding both correct and incorrect examples to help the LLM reason. Contrastive Chain of Thought is applicable anywhere CoT is, such as mathematical and reasoning tasks, but is additionally helpful for scenarios where LLM might be prone to common errors or misunderstandings.

<div class="admonition tip">
<p class="admonition-title">Mirascope Concepts Used</p>
<ul>
<li><a href="../../../../learn/prompts/">Prompts</a></li>
<li><a href="../../../../learn/calls/">Calls</a></li>
</ul>
</div>


```python
from mirascope.core import openai, prompt_template

example = """
Example Question: If you roll two 6 sided dice (1~6) and a 12 sided die (1~12),
how many possible outcomes are there?

Correct Reasoning: The smallest possible sum is 3 and the largest possible sum is 24.
We know two six sided die can roll anywhere from 2 to 12 from their standalone sums,
so it stands to reason that by adding a value from (1~12) to one of those possible
sums from 2~12, we can hit any number from 3~24 without any gaps in coverage.
So, there are (24-3)+1 = 22 possible outcomes.

Incorrect Reasoning: 6x6x12 = 2592 outcomes
"""


@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    {example}
    {query}
    """
)
def call(query: str, ccot_prompt: bool = False) -> openai.OpenAIDynamicConfig:
    return {"computed_fields": {"example": example if ccot_prompt else ""}}


prompt = """
If you roll two 8 sided dice (1~8) and a 10 sided die (1~10), how many possible
outcomes are there?
"""

print(call(query=prompt, ccot_prompt=True))
```

    To find the total number of possible outcomes when rolling two 8-sided dice and one 10-sided die, we can use the counting principle. 
    
    1. **Two 8-sided dice:** Each die has 8 possible outcomes. Therefore, the number of outcomes for two dice is:
       \[
       8 \times 8 = 64
       \]
    
    2. **One 10-sided die:** This die has 10 possible outcomes.
    
    3. **Total Outcomes:** Since the rolls are independent, the total number of outcomes when rolling two 8-sided dice and one 10-sided die is the product of the outcomes from each die:
       \[
       64 \times 10 = 640
       \]
    
    Thus, the total number of possible outcomes when rolling two 8-sided dice and one 10-sided die is **640**.


<div class="admonition tip">
<p class="admonition-title">Effective Contrastive Chain of Thought Usage</p>
<ul>
<li><strong>Provide Clear Examples</strong>: Include both correct and incorrect reasoning examples to guide the LLM's thought process.</li>
<li><strong>Highlight Common Mistakes</strong>: Use incorrect examples that demonstrate typical errors or misconceptions related to the problem.</li>
<li><strong>Explain the Contrast</strong>: Clearly explain why the correct reasoning is right and why the incorrect reasoning is wrong.</li>
<li><strong>Apply to Complex Problems</strong>: Use Contrastive Chain of Thought for problems where there are multiple potential approaches, some of which may lead to incorrect conclusions.</li>
<li><strong>Customize Examples</strong>: Tailor the examples to be relevant to the specific type of problem or domain you're working with.</li>
</ul>
</div>

Contrastive Chain of Thought enhances the standard Chain of Thought approach by explicitly showing both correct and incorrect reasoning paths. This technique can be particularly effective in helping the LLM avoid common pitfalls and misconceptions, leading to more accurate and robust problem-solving across a variety of tasks, especially those prone to subtle errors or misunderstandings.
