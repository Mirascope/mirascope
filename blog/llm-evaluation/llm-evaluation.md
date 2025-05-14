---
title: Overview of LLM Evaluation Metrics and Approaches 
description: >
  Discover key metrics and methods for comprehensive LLM evaluation. Improve your language model's performance with these proven strategies.
authors:
  - willbakst
categories:
  - Tips & Inspiration
date: 2024-11-16
slug: llm-evaluation
---

# Overview of LLM Evaluation Metrics and Approaches

Methods of evaluating LLMs originated from early techniques used to assess classical NLP models (like Hidden Markov Models and Support Vector Machines). However, the rise of Transformer-based LLMs required more sophisticated evaluations that focused on scalability, generative quality, and ethical considerations.

These evaluations (or “evals” as they’re also called) systematically measure and assess model outputs to ensure they **perform effectively within their intended application or context**.

This is necessary because language models can generate incorrect, biased, or harmful content, which can have implications based on your use case. So you’ll need to verify that the outputs meet your quality standards and adhere to factual correctness.

The whole process of doing evals can be boiled down to two tasks: 

1. Coming up with good criteria against which to evaluate LLM outputs.  
2. Developing systems that reliably and consistently measure those outputs against your criteria.

<!-- more -->

**Ultimately, you’ll want to automate as much as possible** (note we didn’t say completely since you’ll probably want human oversight in critical places) so that your evals scale successfully with your application.

They should also be set up in such a way that they give you confidence that the whole system is functioning as intended.

The above is our destination for evals, but the journey will have bumps:

* There’s no one metric that can perfectly assess a model’s performance, so you’re better off using them in combination.  
* Even LLMs have their own biases (based on their training data of course) so you might consider using a panel of language models to average out individual biases and gain some balance.  
* Subjectivity should be checked at the door when it comes to certain tasks like fact checking, since these require strict, objective evaluations.  
* Evaluating several outputs simultaneously across models is slow if done sequentially.  
* Running evaluations using larger models like GPT-4 is computationally expensive, especially when running many evaluations in parallel through asynchronous execution.  
* As everyone knows by now, the whole space is a moving target, which your evals need to keep up with.

That said, below we give you details on different aspects of setting up and working with LLM evaluations, based on our experiences developing LLM-based applications since the early days of the OpenAI SDK.

Later, we also show some examples of working with evaluations using [Mirascope](https://github.com/mirascope/mirascope), our lightweight toolkit for building applications with generative AI.

## Metrics for Evaluating Language Models

Below we list a few of the more popular (quantitative) metrics for assessing LLMs, many of which can be accessed or implemented via platforms like Hugging Face or more directly with libraries such as NumPy. These metrics are useful for assessing language models both in isolation (during the fine-tuning process, for example), in question-answering tasks, or in the context of an application.

### Accuracy

Accuracy measures the ratio of predictions that are correct out of the total number of predictions, including both positive and negative outcomes. It’s calculated using all four possible outcomes from the [confusion matrix](https://www.ibm.com/topics/confusion-matrix): true positives, true negatives, false positives, and false negatives. Accuracy works well for balanced datasets, but in cases with class imbalance, it can be misleading. 

For example, a model predicting the majority class in a dataset where one outcome is very rare might achieve a high accuracy despite performing poorly on minority cases.

### Precision

[Precision](https://arize.com/blog-course/precision-ml/) measures the accuracy of a model's positive predictions by calculating the proportion of true positive predictions out of all positive predictions made, whether those predictions are correct (true positives) or incorrect (false positives).

A high precision score indicates that when the model predicts a positive outcome, it’s usually correct, minimizing the number of false positives. For example, in a spam detection system, high precision means the model correctly identifies most spam emails, with fewer legitimate emails mistakenly labeled as spam.

### Recall

[Recall](https://www.marqo.ai/blog/what-is-recall-in-machine-learning) measures the percentage of true positives out of all actual positive instances, including both true positives and false negatives. 

It reflects the model’s ability to identify all relevant instances (positives) within the data. A high recall score means the model is minimizing false negatives, which is important in contexts like medical diagnoses, where missing a positive case (e.g., a patient with a disease) can be critical.

For example, in medical diagnosis, high recall means the model successfully identifies most patients with the disease, although it might also return some false positives (healthy patients wrongly identified as sick).​

### F1 Score

[F1 score](https://www.v7labs.com/blog/f1-score-guide) is the harmonic mean of precision and recall. It balances both metrics by considering their relationship, meaning if either precision or recall is low, the F1 score will also be low. 

This makes the F1 score useful in scenarios where a balance between precision and recall is important, such as in classification tasks where both false positives and false negatives need to be minimized

### MRR (Mean Reciprocal Rank)

[MRR](https://www.evidentlyai.com/ranking-metrics/mean-reciprocal-rank-mrr) evaluates the quality of a ranking system, like a search engine or recommendation system, by measuring the average rank position of the correct answer in a list of ranked results.

It basically shows how close to the top of the list the correct answer tends to appear, with a higher MRR indicating the correct answer is consistently appearing closer to the top of the list, suggesting the ranking system is performing well.

### Perplexity

[Perplexity](https://klu.ai/glossary/perplexity) is commonly used to evaluate LLM performance and measures how well a model predicts a sequence of words.

A lower perplexity shows the model is making more accurate predictions, meaning it has a better understanding of the language and can generate more coherent and natural-sounding text. 

But a higher perplexity means it’s struggling to predict the next word, indicating it might have limitations in understanding the language or generating fluent text.

### BLEU (Bilingual Evaluation Understudy)

[BLEU](https://medium.com/nlplanet/two-minutes-nlp-learn-the-bleu-metric-by-examples-df015ca73a86) measures the accuracy of machine-translated text by comparing n-gram overlaps between generated text and reference translations. In other words, it calculates how many n-grams (sequences of words) of a certain length appear in both the generated text and the reference translation (i.e., the overlaps).

A higher BLEU score indicates a better match between the generated and reference texts, indicating the machine translation application produced more accurate results.

### ROUGE (Recall-Oriented Understudy for Gisting Evaluation)

[ROUGE](https://medium.com/nlplanet/two-minutes-nlp-learn-the-rouge-metric-by-examples-f179cc285499) evaluates the quality of text summaries or other generated content by measuring the overlap between generated and referenced text, calculating how much of the reference text is captured in the generated text. 

A higher ROUGE score means the generated text offers better coverage of the original content, indicating it’s a more accurate or comprehensive summary.

## Using Frameworks vs Custom Flows

An LLM evaluation framework is software that automates tasks for assessing the performance of language models and usually comes with a particular methodology or approach.

Frameworks aim to ease the burden of doing evals by allowing you to conveniently test models across different datasets, use cases, or iterations.

Although you’ll find many articles recommending one LLM evaluation framework or another, **we advise ditching any one-size-fits-all approach to evals** that doesn’t align with the specific needs of your application.

Building custom eval flows is a better option because you can define metrics and criteria that directly reflect the qualities you need to optimize for — whether it's precision in medical language, creative output for content generation, or minimizing biases for sensitive topics. 

We agree though it’s fine to use general frameworks for demonstration purposes. Just don’t rely on them to fully evaluate or improve your model.

## Ways of Evaluating Language Models

Below we present several effective ways to evaluate language models, ranging from using relatively simple criteria like recall and precision, to assessing outputs for more subjective qualities like toxicity, and illustrate these using code samples from Mirascope.

### Rule-Based Evaluations

Designing criteria based on strictly defined, objective rules (or hardcoded evaluations using benchmark datasets) is relatively straightforward to accomplish.

#### Exact Match

You use exact match to test outputs for occurrences of specific words, phrases, or patterns. This method is useful for fact-checking or ensuring that certain key information is included:

```py
def exact_match_eval(output: str, expected: list[str]) -> bool:
    return all(phrase in output for phrase in expected)

# Example usage
output = "Mount Everest is the highest mountain in the world, located in the Himalayas."
expected = ["Mount Everest", "highest mountain", "Himalayas"]
result = exact_match_eval(output, expected)
print(result)  # Output: True

```

#### Recall and Precision

You can also evaluate whether a particular text covers expected information without requiring exact matches by calculating **recall** (discussed earlier in this article) as the proportion of expected information that appears in the output, and **precision** as the ratio of the output that is relevant to the target content:

```py
def calculate_recall_precision(output: str, expected: str) -> tuple[float, float]:
    output_words = set(output.lower().split())
    expected_words = set(expected.lower().split())

    common_words = output_words.intersection(expected_words)

    recall = len(common_words) / len(expected_words) if expected_words else 0
    precision = len(common_words) / len(output_words) if output_words else 0

    return recall, precision


# Example usage
output = "Mount Everest is the tallest mountain in the world."
expected = (
"Mount Everest, located in the Himalayas, is the tallest peak on Earth."
)
recall, precision = calculate_recall_precision(output, expected)
print(f"Recall: {recall:.2f}, Precision: {precision:.2f}")
# Output: Recall: 0.43, Precision: 0.50

```

### LLM as Judge

LLMs are natural candidates for the subtle and subjective evaluations required by language tasks like creativity, tone, and content analysis, which are hard to assess with fixed or rules-based criteria. 

When using models to assess the quality of LLM outputs, it’s all in the prompt (so to speak) and so we recommend you follow [best prompt engineering practices](https://mirascope.com/blog/prompt-engineering-best-practices) to ensure consistent, thorough, and interpretable evaluations:

* Write prompts that clearly define evaluation criteria  
* Provide a detailed scale or rubric  
* Use few-shot prompting to illustrate different levels of quality being evaluated  
* Ask for an explanation of the final score  
* Tell the LLM to consider different aspects of the text, rather than just focusing on one aspect

Done right, using models to evaluate other models are very handy for automating and scaling evaluations in your application.

Below, we show two ways of using LLMs as judges.

#### 1. Evaluate an Output Using a Single Model

This example shows how to evaluate a text for answer relevance, using a single LLM via an API (OpenAI’s GPT-4o-mini).

```py
from typing import Literal

from mirascope.core import openai, prompt_template
from pydantic import BaseModel, Field


class Eval(BaseModel):
    score: Literal["poor", "ok", "good", "great", "excellent"] = Field(
        ..., description="A score representing the relevance of the generated answer."
    )
    reasoning: str = Field(
        ..., description="The reasoning for the score in 100 characters or less."
    )


@openai.call(model="gpt-4o-mini", response_model=Eval)
@prompt_template(
    """
    Evaluate the relevance of the generated answer to the given question on a continuous scale from poor to excellent.
    A generation is considered relevant (score > poor ) if it addresses the core of the question, provides accurate information, 
    and stays focused on the topic.

    Consider the following aspects when evaluating the answer:
    - Accuracy: Does the answer provide factually correct information?
    - Completeness: Does the answer sufficiently cover the question?
    - Focus: Does the answer stay on topic without introducing unnecessary or unrelated information?
    - Clarity: Is the answer clear and easy to understand?

    Use the following relevance scale:
    
    poor - No relevance; the answer is completely unrelated or nonsensical
    ok - Low relevance; minor relation to the question but missing key details or accuracy
    good - Moderate relevance; somewhat addresses the question but lacks depth or focus
    great - High relevance; mostly answers the question but may lack completeness or introduce some off-topic information
    excellent - Very high relevance; thoroughly answers the question with minor flaws

    Provide a brief reasoning for your assigned score, considering different aspects such as accuracy, focus, and completeness.

    Question: {question}
    Answer: {answer}
    """
)
def evaluate_answer_relevance(question: str, answer: str): ...


# Example usage
question = "What are the benefits of renewable energy?"
answer = "Renewable energy comes from natural sources like solar and wind, which are infinite and produce less pollution."
response = evaluate_answer_relevance(question=question, answer=answer)
print(response)
# Output: score='good' reasoning="Accurate but lacks depth; doesn't cover all benefits comprehensively."

question = "What are the benefits of renewable energy?"
irrelevant_answer = "I enjoy watching movies on the weekends."
response = evaluate_answer_relevance(question=question, answer=irrelevant_answer)
print(response)
# Output: score='poor' reasoning='The answer is completely unrelated to the question about renewable energy benefits.'

```

Note that we use NLP scores (e.g. "good") instead of numerical scores. In our experience, we've found that LLMs are better at scoring using natural language than numbers.

#### 2. Evaluate an Output Using a Panel of Judges

In cases where a single model’s evaluation might be limited or biased, you may opt for a more comprehensive and balanced evaluation that accounts for different model strengths, weaknesses, and biases.

Here’s another example of evaluating for answer relevance using OpenAI’s GPT-4o-mini and Anthropic’s Claude 3.5 Sonnet:

```py
from typing import Literal

from mirascope.core import BasePrompt, anthropic, openai, prompt_template
from pydantic import BaseModel, Field


class Eval(BaseModel):
    score: Literal["poor", "ok", "good", "great", "excellent"] = Field(
        ..., description="A score representing the relevance of the generated answer."
    )
    reasoning: str = Field(
        ..., description="The reasoning for the score in 100 characters or less."
    )


@prompt_template(
    """
    Evaluate the relevance of the answer to the given question on a scale from poor to excellent:

    poor - No relevance; the answer is completely unrelated or nonsensical
    ok - Low relevance; minor relation to the question but missing key details or accuracy
    good - Moderate relevance; somewhat addresses the question but lacks depth or focus
    great - High relevance; mostly answers the question but may lack completeness or introduce some off-topic information
    excellent - Very high relevance; thoroughly answers the question with minor flaws


    When evaluating relevance, consider the following aspects:
    - Accuracy: Is the information provided correct?
    - Completeness: Does the answer fully address the question?
    - Focus: Does the answer stay on topic without introducing irrelevant information?
    - Clarity: Is the answer easy to understand?

    Provide a brief reasoning for your assigned score, highlighting the aspects that influenced your decision.

    Question: {question}
    Answer: {answer}
    """
)
class AnswerRelevancePrompt(BasePrompt):
    question: str
    answer: str


# Example question and answers
question = "What are the benefits of renewable energy?"
answer = "Renewable energy comes from natural sources like solar and wind, which are infinite and produce less pollution."

prompt = AnswerRelevancePrompt(question=question, answer=answer)

judges = [
    openai.call("gpt-4o", response_model=Eval),
    anthropic.call("claude-3-5-sonnet-20240620", response_model=Eval),
]

evaluations: list[Eval] = [prompt.run(judge) for judge in judges]

for evaluation in evaluations:
    print(evaluation)
# Output:
# (GPT-4o) score='great' reasoning='Accurate, on-topic, but lacks breadth in benefits.'
# (Sonnet) score='good' reasoning='Accurate but lacks depth. Mentions key points (sources, infinity, less pollution) but misses economic benefits.' 

```

### Mirascope Evaluation Guide

See our [documentation](https://mirascope.com/learn/evals/) for rich examples and techniques to help you write evaluations for a range of LLM-driven applications.

## 6 Best Practices for Evaluating Language Models

Below is a list of best practices we’ve found to be useful for creating effective language model evaluations:

### 1. Combine LLM- and Rule-Based Evaluation

Just as no one metric is perfect for evaluating a model, you shouldn’t rely only on either LLM- or rule-based evaluations.

While LLM-based evaluations (like LLM as judge) are great for assessing subjective aspects, such as tone or creativity, they can nevertheless miss the mark when you need to evaluate for factual correctness or exact word matching.

Hardcoded evaluations, on the other hand, are highly reliable for verifying objective details, like specific keywords or format adherence. By combining these approaches, you capture both the nuanced and objective aspects of performance, allowing for a more holistic evaluation of model strengths and weaknesses across various [LLM applications](https://mirascope.com/blog/llm-applications).

### 2. Establish a Baseline Early On

Establish baseline performance for your model early on to act as a point of reference for tracking improvements or detecting degradations over time.

These baselines can be derived from an earlier version of the model, human-generated answers, or industry standards. By creating a set of benchmark tests, you can objectively measure how each iteration of your model compares to the original performance, ensuring consistent improvement.

We've found that LLMs can also generate fairly high-quality synthetic data to get you started. We recommend using LLMs to generate synthetic inputs that you can then run through your actual prompts to get real outputs. You can then hand label these examples (or use an LLM judge) to get your initial baseline.

### 3. Continuously Refine Your Evals

Evaluation isn’t a one-time process; it requires continuous iteration to stay in a useful state given evolving goals and language models.

As new use cases emerge or as the model is fine-tuned, you should regularly revisit your criteria and prompts used for evaluations. Analyze results from past evaluations to identify areas where the evaluation method may be lacking, and adjust the [prompts](https://mirascope.com/blog/llm-prompt) and scoring rubrics accordingly.

### 4. Maintain Context Awareness in Evals

Good evals require a deep understanding of the context in which the LLM output was generated. For instance, a relevant and clear response in one scenario might be irrelevant or inappropriate in another. 

You should design evaluation methods to account for specific circumstances surrounding the input and the intended outcome, rather than using generic templates. By embedding context awareness into the process, you can better judge how well the model adapts to varying situations and ensures relevance across different environments or use cases.

### 5. Use Version Control

We highly recommend versioning your evaluation prompts and criteria to understand how changes affect your eval results over time. 

By tracking different [versions of prompts](https://mirascope.com/blog/prompt-versioning), criteria, and scoring rubrics, you can analyze how modifications to the evaluation setup impact performance metrics. This ensures transparency and helps pinpoint what changes contributed to improvements — or regressions — in the model’s performance.

### 6. Use Diverse Test Sets

Using a set of test inputs covering a wide range of scenarios and edge cases gives you a clearer picture of how the LLM model performs under different contexts and ensures it can handle unexpected situations effectively.

On the other hand, testing with a narrow or overly specific set of inputs can result in a false sense of confidence in the model’s performance. Without diverse evaluations, you’re at risk of deploying a large language model that underperforms in real-world situations, leading to user dissatisfaction or even failure in important tasks.

## Take Control of Your AI’s Evaluations and Performance

Mirascope supports comprehensive, scalable evaluations throughout your [pipeline](https://mirascope.com/blog/llm-pipeline), helping ensure your model performs reliably across diverse scenarios, while reducing bias and delivering consistent, high-quality outputs. Start refining your evaluation process to drive better outcomes for your AI initiatives.

Want to explore more LLM evaluation techniques? You can find Mirascope code samples both on our [documentation site](https://mirascope.com/WELCOME) and our [GitHub repository](https://github.com/mirascope/mirascope).
