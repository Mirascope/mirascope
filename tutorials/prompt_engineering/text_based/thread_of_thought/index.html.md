# Thread of Thought

[Thread of Thought](https://arxiv.org/pdf/2311.08734) (THoT) is an extension of zero-shot [Chain of Thought](../chain_of_thought) where the request to walk through the reasoning steps is improved. The paper tests the results of various phrases, but finds the best to be "Walk me through this context in manageable parts step by step, summarizing and analyzing as we go." It is applicable to reasoning and mathematical tasks just like CoT, but is most useful for tasks with retrieval / large amounts of context and Q and A on this context.

<div class="admonition tip">
<p class="admonition-title">Mirascope Concepts Used</p>
<ul>
<li><a href="../../../../learn/prompts/">Prompts</a></li>
<li><a href="../../../../learn/calls/">Calls</a></li>
</ul>
</div>



```python
from mirascope.core import openai, prompt_template

rag_output = [
    """Apple Inc. was founded on April 1, 1976, by Steve Jobs, Steve Wozniak, and
Ronald Wayne. The company started in the garage of Jobs' childhood home in 
Los Altos, California.""",
    """Steve Jobs was a visionary entrepreneur and the co-founder of Apple Inc.
He played a key role in the development of the Macintosh, iPod, iPhone, and iPad.""",
    """Apple's headquarters, known as Apple Park, is located in Cupertino, California.
The campus, designed by Norman Foster, opened to employees in April 2017.""",
    """In 1977, Apple Computer, Inc. was incorporated. The Apple II, one of the first
highly successful mass-produced microcomputer products, was introduced that year.""",
    """Apple's first product, the Apple I, was sold as a fully assembled circuit board.
The idea for the company came from Steve Wozniak's interest in building a computer
kit.""",
    """Steve Wozniak and Steve Jobs were high school friends before they founded Apple
together. They were both members of the Homebrew Computer Club, where they exchanged
ideas with other computer enthusiasts.""",
    """The first Apple Store opened in Tysons Corner, Virginia, in May 2001.
Apple Stores have since become iconic retail spaces around the world.""",
    """Apple has a strong commitment to environmental sustainability. The company
aims to have its entire supply chain carbon neutral by 2030.""",
    """Ronald Wayne, the lesser-known third co-founder of Apple, sold his shares
in the company just 12 days after it was founded. He believed the venture was too
risky and wanted to avoid potential financial loss.""",
    """In 1984, Apple launched the Macintosh, the first personal computer to feature
a graphical user interface and a mouse. This product revolutionized the computer
industry and set new standards for user-friendly design.""",
]


def retrieve_passages(query: str):
    """Simulates RAG retrieval."""
    return rag_output


thot_augment = """Walk me through this context in manageable parts step by step,
summarizing and analyzing as we go"""


@openai.call(model="gpt-4o-mini")
@prompt_template(
    """
    As a content reviewer, I provide multiple retrieved passages about
    this question; you need to answer the question.

    {context}

    {query} {thot_augment}
    """
)
def call(query: str, thot_prompt: bool = False) -> openai.OpenAIDynamicConfig:
    passages = retrieve_passages(query)
    context = [
        f"retrieved passage {i+1} is: {passage}" for i, passage in enumerate(passages)
    ]
    return {
        "computed_fields": {
            "context": context,
            "thot_augment": thot_augment if thot_prompt else "",
        }
    }


prompt = "Where was Apple founded?"

print(call(query=prompt, thot_prompt=True))
```

    To answer the question "Where was Apple founded?" let's break down the information available in the retrieved passages step by step.
    
    ### Step 1: Identify Founding Information
    
    From **retrieved passage 1**, we learn the following:
    - Apple Inc. was founded on April 1, 1976.
    - The founders are Steve Jobs, Steve Wozniak, and Ronald Wayne.
    - The company started in the garage of Jobs' childhood home.
    
    ### Step 2: Analyze the Location
    
    The precise location mentioned in **retrieved passage 1** is:
    - **Los Altos, California.**
    This indicates that Apple was founded in a residential setting, specifically in a garage, which is a common story for many tech startups, illustrating humble beginnings.
    
    ### Step 3: Confirming with Additional Context
    
    While the remaining passages provide various pieces of information about Apple, such as the development of its products and its incorporation, they do not provide an alternative founding location. Therefore, the core location remains unchanged by the additional context.
    
    ### Step 4: Summarizing
    
    In summary, Apple Inc. was founded in **Los Altos, California**, in the garage of Steve Jobs' childhood home. This information highlights the origins of a now-massive corporation, emphasizing that great companies can start in modest environments.
    
    Thus, the answer to the question "Where was Apple founded?" is **Los Altos, California**.



<div class="admonition tip">
<p class="admonition-title">Effective Thread of Thought Usage</p>
<ul>
<li><strong>Use with Large Context</strong>: THoT is particularly effective when dealing with large amounts of retrieved information or context.</li>
<li><strong>Encourage Step-by-Step Analysis</strong>: The key phrase "Walk me through this context in manageable parts step by step, summarizing and analyzing as we go" prompts the LLM to break down and analyze information incrementally.</li>
<li><strong>Apply to Q&A Tasks</strong>: THoT is especially useful for question-answering tasks that require processing and synthesizing information from multiple sources.</li>
<li><strong>Combine with Retrieval</strong>: THoT works well in combination with retrieval augmented generation (RAG) techniques.</li>
<li><strong>Review Intermediate Steps</strong>: Examine the LLM's step-by-step analysis to ensure it's properly interpreting and synthesizing the context.</li>
</ul>
</div>

Thread of Thought enhances the zero-shot Chain of Thought approach by providing a more structured way for the LLM to process and analyze large amounts of context. This technique is particularly valuable for tasks that involve information retrieval and synthesis, allowing for more thorough and transparent reasoning in complex question-answering scenarios.
