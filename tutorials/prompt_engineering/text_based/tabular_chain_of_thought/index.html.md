# Tabular Chain of Thought

[Tabular Chain of Thought](https://arxiv.org/pdf/2305.17812) (Tab-CoT) is an extension of zero-shot [Chain of Thought](https://arxiv.org/abs/2201.1190), with the caveat that the LLM is given a Markdown heading to structure each step of its response in an individual row of a Markdown table. The added structure can help the LLM's reasoning process and improves accuracy in arithmetic and reasoning tasks.

<div class="admonition tip">
<p class="admonition-title">Mirascope Concepts Used</p>
<ul>
<li><a href="../../../../learn/prompts/">Prompts</a></li>
<li><a href="../../../../learn/calls/">Calls</a></li>
</ul>
</div>



```python
from mirascope.core import openai, prompt_template

tab_cot_augment = "|step|subquestion|process|result|"


@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    {query}
    {tab_cot_augment}
    """
)
def call(query: str, tab_cot_prompt: bool = False) -> openai.OpenAIDynamicConfig:
    return {
        "computed_fields": {
            "tab_cot_augment": tab_cot_augment if tab_cot_prompt else "",
        }
    }


prompt = """A pet store had 102 puppies. In one day they sold 21 of them and put
the rest into cages with 9 in each cage. How many cages did they use?"""

print(call(query=prompt, tab_cot_prompt=True))
```

    | Step | Subquestion                     | Process                                                                                            | Result     |
    |------|---------------------------------|-----------------------------------------------------------------------------------------------------|------------|
    | 1    | How many puppies are left?     | Start with 102 puppies and subtract the 21 sold: 102 - 21 = 81                                   | 81 puppies |
    | 2    | How many cages are needed?     | Divide the remaining puppies by the number in each cage: 81 ÷ 9 = 9                             | 9 cages    |
    | 3    | Check for remainder?           | Calculate the remainder when dividing 81 by 9: 81 mod 9 = 0 (no remainder, so no extra cage needed)| N/A        |
    
    Final Result: The pet store used **9 cages**.


Tabular Chain of Thought is an extension of [Chain of Thought](https://arxiv.org/abs/2201.1190), with the caveat that the LLM is asked to put each step of its reasoning process in a row of a Markdown table. The added structure can structure the LLM's reasoning and make it likelier to give a correct answer.



```python
from mirascope.core import openai


@openai.call(model="gpt-3.5-turbo")
def call(query: str) -> str:
    return query


prompt = """
A circle with radius 1 circumscribes (perfectly surrounds) an equilateral triangle.
What's the area of the triangle?
"""
generic_response = call(prompt)
engineered_response = call(f"""{prompt}. Explain your reasoning step by step,
with each step in a row in a markdown table.""")

print(generic_response)
print("\n\n\n")
print(engineered_response)
```

    To find the area of the equilateral triangle that is circumscribed by the circle with radius 1, first we need to find the side length of the triangle.
    
    In an equilateral triangle, all sides are equal. Let's label the side length as "s". 
    
    The radius of the circle will be the distance from the center of the circle to the midpoint of a side of the equilateral triangle. This forms a right triangle with the side of the equilateral triangle and half of the side of the equilateral triangle. Using the Pythagorean theorem, we have:
    
    s^2 = (s/2)^2 + 1^2
    s^2 = s^2/4 + 1
    3s^2/4 = 1
    s^2 = 4/3
    s = sqrt(4/3)
    s = 2/sqrt(3)
    
    Now that we have the side length of the equilateral triangle, we can find the area of the triangle using the formula:
    
    Area = (sqrt(3)/4)(s^2)
    Area = (sqrt(3)/4)(4/3)
    Area = sqrt(3)/3
    
    Therefore, the area of the equilateral triangle is sqrt(3)/3 units squared.
    
    
    
    
    | Step | Calculation                                      | Reasoning                                                                                  |
    |------|--------------------------------------------------|--------------------------------------------------------------------------------------------|
    | 1    | Equilateral triangle has all equal sides        | By definition, all sides of an equilateral triangle are equal                               |
    | 2    | The radius of the circle is 1                   | Given in the problem statement                                                            |
    | 3    | The radius of the circle is the distance         | From the center of the circle to any vertex of the triangle, which is also the altitude    |
    | 4    | The altitude of an equilateral triangle         | Is also the perpendicular bisector of any side of the triangle                            |
    | 5    | Dividing the angle at a vertex of the triangle  | into two equal parts gives two 30-60-90 right triangles                                  |
    | 6    | The side opposite the 60 degree angle in         | a 30-60-90 triangle is $\sqrt{3}$ times the side opposite the 30 degree angle             |
    | 7    | The side opposite the 30 degree angle in a       | 30-60-90 triangle is 1 times the radius of the circle                                      |
    | 8    | Therefore, the side opposite the 60 degree       | angle in our equilateral triangle is $\sqrt{3}$ times the radius of the circle, which is 1 |
    | 9    | Using the formula for the area of an equilateral | triangle with side length "s": $Area = \frac{\sqrt{3}}{4} * s^2$                           |
    | 10   | Substituting $s = \sqrt{3}$                      | into the formula gives $Area = \frac{\sqrt{3}}{4} * (\sqrt{3})^2 = \frac{3\sqrt{3}}{4}$     |
    | 11   | Thus, the area of the equilateral triangle       | circumscribed by a circle with radius 1 is $\frac{3\sqrt{3}}{4}$ units squared              |


For reference, `engineered_response` answer is correct.

<div class="admonition tip">
<p class="admonition-title">Effective Tabular Chain of Thought Usage</p>
<ul>
<li><strong>Structured Reasoning</strong>: Use Tab-CoT to encourage the LLM to break down complex problems into clear, discrete steps.</li>
<li><strong>Improved Accuracy</strong>: The tabular format can lead to improved accuracy, especially in arithmetic and multi-step reasoning tasks.</li>
<li><strong>Easy Verification</strong>: The step-by-step tabular format makes it easier to verify the LLM's reasoning process.</li>
<li><strong>Consistency</strong>: Tab-CoT can help maintain consistency in the problem-solving approach across different queries.</li>
<li><strong>Visual Clarity</strong>: The table format provides a clear visual representation of the problem-solving process, which can be beneficial for understanding and presentation.</li>
</ul>
</div>

Tabular Chain of Thought provides a structured approach to problem-solving that can enhance the LLM's reasoning capabilities. By organizing thoughts into a table format, it allows for clearer step-by-step analysis, which can lead to more accurate results, especially in complex arithmetic or logical reasoning tasks.
