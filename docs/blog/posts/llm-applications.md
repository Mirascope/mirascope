---
title: LLM Applications - What They Are and 6 Examples
description: >
  Curious about LLM applications? Discover what they are and see 6 practical examples of how large language models are being applied across sectors.
authors:
  - willbakst
categories:
  - Tips & Inspiration
date: 2024-08-30
slug: llm-applications
---

# LLM Applications: What They Are and 6 Examples

Large language models (LLMs) have exploded in popularity since the release of ChatGPT in late 2022, which brought a surge of interest in the development community for building LLM applications across various domains like healthcare, finance, entertainment, and beyond.

Developers are integrating models into tools for content generation, customer service automation, personalized learning, and data analysis, among many others, driving innovation in areas where natural language understanding and generation excel.

As the range of applications continues to grow, we decided to explore six of the most popular and impactful use cases that are driving adoption of LLM applications today.

We also explain our top considerations for designing such apps, and show you how to implement an example question-answering chatbot using both Llama Index, a framework commonly used for ingesting and managing data, and [Mirascope](https://github.com/mirascope/mirascope), our lightweight tool for building LLM applications.

<!-- more -->

## 6 Real-World LLM Applications

As we suggested above, the number of potential applications using large language models, even at the current technological level, is virtually limitless. Here, we present several popular (and interesting) use cases for LLMs.

### 1. Text Classification

You can leverage an LLM’s deep understanding of language to [accurately categorize text](https://mirascope.com/tutorials/more_advanced/text_classification/) based on its content, intent, or sentiment.

This can be done in a wide variety of contexts like customer support, content moderation, sentiment analysis, and even more specialized domains like legal document classification or medical record categorization.

Depending on the specificity of a domain's language, you might need a specialized model fine-tuned for that particular field. Or you can leverage [prompt engineering](https://mirascope.com/blog/prompt-engineering-examples) to guide a pretrained model in reaching the necessary accuracy and relevance for classification tasks.

#### Types of Text Classification

There are different ways to classify text, including:

| Type                  | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Binary**            | Text is categorized as one of two possible classes and labeled accordingly. <br><br>Example application: an email filter that classifies messages as “spam” or “not spam.”                                                                                                                                                                                                                                                                                                                                                                   |
| **Multi-Class**       | A single piece of text can be assigned multiple labels simultaneously. <br><br>Example application: a news recommendation platform that uses a multi-label classifier to tag a news article as both "Politics" and "Economics."                                                                                                                                                                                                                                                                                                              |
| **Hierarchical**      | Text can be categorized into a structured taxonomy, where broader categories are subdivided into more specific ones. <br><br>Example application: a clinical decision support system that uses a hierarchical classifier to first classify a text as related to "Disease," then narrow it down to "Infectious Disease," and finally to "Viral Infection."                                                                                                                                                                                    |
| **Sequence Labeling** | Each word or token in a text sequence can be classified individually, rather than the entire text as a single unit. <br><br>Example classification: a financial news application platform that uses named entity recognition (NER) to scan incoming financial news and automatically identify and categorize proper nouns and other specific entities. For example, in a news article mentioning "Apple," "Tim Cook," and "Cupertino," the NER system would tag "Apple" as a company, "Tim Cook" as a person, and "Cupertino" as a location. |

#### Text Classification Example

Below, we show a brief example of using binary classification.

Prompt:

```plaintext
Classify the following text as spam or not spam: {text}
```

Output:

```plaintext
"I'm the Deputy Governor of the Central Bank and need your help to transfer $25 million out of the country, and will offer you a 30% share."

# This text is classified as spam


"Hi! It was great meeting you today. Let's stay in touch!"

# This text is classified as not spam
```

### 2. Text Summarization

[Text summarization](https://mirascope.com/tutorials/more_advanced/text_summarization/) basically takes a longer text and distills it into a more manageable format. Unlike earlier models that merely extracted and rearranged sentences, modern LLMs “digest” and generate more useful, abstractive summaries.

This means they synthesize new sentences that encapsulate the core ideas, offering a more fluid and nuanced representation of the original content.

#### Applications of Text Summarization

A few of the possible uses of text summarization include:

- Meeting minutes
- Patient medical records
- Summarizing product reviews
- Academic research papers
- Financial reports
- Government reports

#### Text Summarization Example

Prompt:

```plaintext
Summarize the following text by first creating an outline with a nested structure, listing all major topics in the text with subpoints for each of the major points. The number of subpoints for each topic should correspond to the length and importance of the major point within the text. Then create the actual summary using the outline.
{text}
```

Output:

```plaintext
1. Introduction to Generative Pre-trained Transformers (GPTs)
- Definition and purpose
- Transformer architecture foundation
- Pre-training on large datasets
- Capability to generate human-like content

2. Development and Evolution of GPT Models
- Introduction of the first GPT by OpenAI in 2018
- Subsequent releases, including GPT-4 in March 2023
- GPT models as a foundation for various task-specific systems, e.g., ChatGPT

3. GPT Models by Other Companies
- Development of GPT models by EleutherAI and Cerebras
- Mention of competition and diversification in the field

4. Customization and Adaptation of GPT Models
- Fine-tuning and prompt engineering for specific tasks and domains
- Multi-modal capabilities, including processing text, images, and audio
- Custom versions of ChatGPT for specific domains (ChatGPT Plus subscribers)

5. Trademark and Legal Aspects
- OpenAI's pursuit of trademark registration for the term "GPT" in AI

Summary

Generative pre-trained transformers (GPTs) are large language models based on the transformer architecture, designed to generate human-like content by being pre-trained on vast datasets of unlabelled text. First introduced by OpenAI in 2018, GPT models for generative AI have evolved significantly, with major releases like GPT-4 in 2023, forming the basis for applications such as the ChatGPT chatbot. Other companies, such as EleutherAI and Cerebras, have also developed their own GPT models, contributing to the growth and diversity of the field. Though not open source, these AI models can be fine-tuned and adapted for specific tasks and domains, including processing multiple modalities like images and audio. OpenAI has recently introduced custom versions of ChatGPT for specialized use by subscribers and is seeking trademark registration for the term "GPT" within the artificial intelligence sector.
```

### 3. Search with Sources

In [Search with Sources](https://mirascope.com/tutorials/more_advanced/search_with_sources/), the model retrieves information from verified sources through a search tool, and then supports its answers with citations from these sources. It lists these alongside its responses, ensuring the information is grounded in verifiable data.

Retrieving and citing information from verified sources offers better accuracy and improves the credibility of LLM answers by allowing users to easily fact check these.

#### Search with Sources Example

Prompt:

```plaintext
What is the average price of a house in the United States?
```

Output:

```plaintext
{
    "result": [
        {
            "source": "https://www.fool.com/the-ascent/research/average-house-price-state/",
            "answer": "The average house price in the United States was approximately $495,100 in the second quarter of 2023."
        },
        {
            "source": "https://www.instarem.com/blog/average-house-price-usa/",
            "answer": "The average house price in the USA is near record highs and was reported to be around $406,700 as of July 2023."
        },
        {
            "source": "https://www.bankrate.com/real-estate/median-home-price/",
            "answer": "The National Association of Realtors reported the median price for an existing home was $387,600 as of November 2023."
        }
    ]
}
```

### 4. PDF Extraction

[This application](https://mirascope.com/tutorials/more_advanced/extract_from_pdf/) lets you extract specific content from PDF files — whether that’s text, images, or structured data — without the need for the labor-intensive and error-prone manual methods of the past.

Before language models, extracting data required manual effort or, at best, the use of natural language processing (NLP) tools that required configuration to correctly identify and categorize information within a document. Such tools lacked the flexibility to adapt to new or unexpected categories without manual effort.

#### Applications of PDF Extraction

You can extract data from PDFs for different purposes:

| Type                      | Description                                                                                                                                                                                                                                                                                               |
| ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Text**                  | The entire text content from a PDF is extracted and returned in plain text format. <br><br>Example application: automating the extraction of text from contracts, allowing legal teams to quickly review content without manually opening and scanning each document.                                     |
| **Structured Data**       | Specific fields or sections from a PDF are extracted and returned as structured data. <br><br>Example application: parsing invoices to automatically extract details like invoice number, date, and total amount, which can then be imported directly into an accounting system.                          |
| **Field Specific**        | Targeted extraction of predefined fields, such as names, dates, or addresses, from structured or semi-structured PDF documents. <br><br>Example application: scanning employment applications to extract applicant names and contact information, which can then be entered into an HR management system. |
| **Vision-Based Analysis** | Images within a PDF are analyzed to extract text or other meaningful information using vision models. <br><br>Example application: analyzing scanned handwritten notes within a PDF and converting them into editable text or searchable metadata.                                                        |

#### Extract from PDFs Example

Prompt:

```plaintext
Extract personal details from the pdf file.
{pdf_text}
```

Output:

```plaintext
{
    "name": "Jane Doe",
    "email": "jane.doe@example.com",
    "phone": "+1-555-123-4567",
    "skills": [
        "Python",
        "Data Analysis",
        "Machine Learning",
        "SQL",
        "Project Management"
    ],
    "experience": [
        "Data Scientist at Tech Solutions Inc. (2018 - Present): Led data analysis projects and developed machine learning models to improve business processes.",
        "Junior Data Analyst at Analytics Corp. (2015 - 2018): Assisted in data collection, cleaning, and analysis for various client projects."
    ],
    "education": [
        "M.S. in Data Science, University of California, Berkeley (2015)",
        "B.S. in Computer Science, Stanford University (2013)"
    ]
}
```

### 5. Knowledge Graph Extraction

You can [extract a (highly structured) knowledge graph](https://mirascope.com/tutorials/more_advanced/knowledge_graph/) from messy, unstructured data by mapping out the relationships between different entities. This kind of application is well-suited to domains where understanding complex connections is critical, like legal analysis, academic research, and fraud detection.

NLP already makes use of knowledge graphs to identify and link entities within unstructured text. However, LLMs improve the process by more accurately recognizing entities and linking all those entities to the appropriate entries in the knowledge graph.

#### Knowledge Graph Extraction Applications

Applications of knowledge graphs include: ‍

| Type                              | Description                                                                                                                                                                                                                                                                                                                             |
| --------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Entity Relationships**          | Entities and their relationships within a text corpus are identified and structured into a knowledge graph. <br><br>Example application: automatically mapping out the relationships between characters, locations, and events in a historical text, enabling historians to visualize and analyze complex networks over time.           |
| **Contextual Search Enhancement** | Enhancing search functionality by using a knowledge graph to understand the context and relationships between search terms. <br><br>Example application: improving search results in a research database by linking related terms, authors, and topics, allowing users to find relevant studies even if they use different terminology. |
| **Supply Chain Management**       | Extracting and structuring data from supply chain documents into a knowledge graph to track dependencies and risks. <br><br>Example application: visualizing the entire supply chain network, including suppliers, logistics, and inventory levels, to identify potential bottlenecks and optimize operations.                          |
| **Fraud Detection**               | Modeling complex financial data into a knowledge graph to detect patterns of fraudulent activity. <br><br>Example application: mapping transactions between accounts and identifying suspicious links that deviate from normal behavior, helping to flag potential fraud in real-time. #### Knowledge Graph Extraction Example          |

Below, we prompt the LLM to answer a user’s query based on an existing knowledge graph and a Wikipedia article.

For the prompt, we created three roles — SYSTEM, knowledge graph, and USER — to clearly define the context and expectations for each part of the interaction.

The SYSTEM role sets the stage and provides instructions, the knowledge graph role passes the knowledge graph to the LLM, and the USER role represents the actual query.

Prompt:

```plaintext
SYSTEM:
Answer the following question based on the knowledge graph.

Knowledge graph:
{knowledge_graph}

USER:
What are the challenges of renewable energy adoption?
```

Output:

```plaintext
The knowledge graph contains information about the challenges of renewable energy adoption. Based on the existing entries, the challenges include:

1. Intermittency - Renewable energy sources like solar and wind are intermittent, meaning they don't produce energy consistently.
2. High Initial Costs - The initial investment required for renewable energy infrastructure can be prohibitive.
3. Energy Storage - Effective energy storage solutions are still a significant challenge, as renewable energy generation does not always align with demand.
4. Grid Integration - Integrating renewable energy into existing power grids can be complex and costly.
5. Land Use - Renewable energy projects, particularly wind and solar farms, require large amounts of land.
6. Resource Availability - The availability of renewable resources can vary greatly by location, limiting widespread adoption.
7. Public Opposition - There can be public opposition to renewable energy projects, especially due to visual or environmental impacts.
8. Policy and Regulation - Inconsistent or insufficient policies and regulations can hinder the adoption of renewable energy technologies.
```

### 6. Generate Image Captions

[Generating image captions](https://mirascope.com/tutorials/more_advanced/generating_captions/) involves creating descriptive text that accurately reflects the content of an image.

This task, once done only by humans, has seen considerable automation in recent years through the use of machine learning algorithms like conditional random fields (CRFs) and support vector machines (SVMs). While these methods are effective, they often require considerable time and computational resources.

LLMs are a game changer in generating image captions since they can process multiple data types. However, not all model providers offer support for multimodal inputs. OpenAI, however, does and allows developers to use images as context when asking questions or making requests.

#### Image Caption Generation Example

Below, we ask the LLM to caption an image.

Prompt:

```plaintext
Generate a short, descriptive caption for this image: {url:image}
```

Output:

```plaintext
A majestic wolf howls in the night, silhouetted against the luminous full moon, creating a hauntingly beautiful scene that captures the spirit of the wild.
```

## How to Build an LLM Application

Developing an application with a language model at its core comes with special considerations around integration with surrounding components, performance optimization, and more.

### 7 Considerations for Building an LLM App

Here are seven basic, but key elements to consider to ensure the application’s effectiveness, scalability, and overall user experience.

#### 1. Understand Your Target Audience’s Needs

Considering the types of queries users will likely input and how they expect the application to respond will guide you in refining the application's responses to be not only accurate but also delivered in a tone and style that resonates with your users.

#### 2. Clearly Define the Application’s Purpose and Use Case

Specifying the application’s core function, whether that’s a use case like question answering, text summarization, or source-based searches as completely as possible, helps you tailor its features, user interface, and overall design to address the specific problems or requirements of the user.

#### 3. Choose the Right LLM

The choice of LLM should be based on the complexity of the tasks it needs to perform, its required language understanding, the resources at your disposal, and the output types (e.g., text, multimodal, JSON, etc.) that your application requires.

Larger models may deliver better performance but come with higher costs and resource demands, while smaller, private models offer better privacy and security by significantly limiting third-party access.

#### 4. Customize and Fine-Tune the Model

Tailoring the model to handle domain-specific language ensures it can accurately interpret and respond to industry-specific queries. One way to do this is by [fine-tuning the model](https://mirascope.com/blog/prompt-engineering-vs-fine-tuning), which involves training it on a specialized dataset that reflects the specific terminology, nuances, and context of the domain.

[Prompt engineering](https://mirascope.com/blog/prompt-engineering-tools) offers a cost-effective alternative to fine-tuning since it lets you carefully iterate on prompts to better guide the model. In fact, we recommend you start with prompt engineering to first get a strong baseline for model performance.

Then, if you’ve hit a plateau in improvements, fine-tuning on a custom dataset might be a viable option to get further accuracy or relevance out of the model for your use case.

#### 5. Ensure Integration with Backend Systems

Your LLM application will likely need a [data pipeline](https://mirascope.com/blog/llm-pipeline) with access to, for instance, backend systems, databases, and APIs, in order to retrieve and process information as smoothly as possible to give users timely and accurate responses

A well-designed pipeline that’s modular and adaptable allows the application to handle more traffic and complex queries without compromising performance, making it easier to grow and adapt to changing user needs.

#### 6. Optimize for Performance and Scalability

A production-grade application should be capable of handling multiple simultaneous conversations without lag, especially during periods of high traffic. Using performance monitoring tools can help you track metrics such as latency and error rates, ensuring the application remains responsive and reliable.

To further speed things up, you can run parallel execution and asynchronous processing to handle multiple tasks concurrently, reducing bottlenecks and improving response times. These are especially useful for scaling applications to meet the demands of a growing user base.

#### 7. Test and Iterate for Reliability

Doing evaluations across a wide range of scenarios and edge cases to identify potential weaknesses or unexpected behaviors ensures the application will perform consistently under different and perhaps stressful conditions.

We also recommend testing for accuracy and validation by creating a set of benchmark questions with known correct answers, and comparing these responses to the benchmarks to gauge the correctness and relevance of those answers.

### Building an LLM Application that Uses Retrieval Augmented Generation (RAG)

Below, we walk you through the broad steps for developing an application to “chat with your documents.” RAG improves the accuracy and relevance of generated text by passing not only the user’s question to the LLM, but context as well — as relevant document excerpts.

In RAG, documents are often stored in a database called a vector store, where they’re converted into vector representations for efficient search and retrieval.

**A RAG system has two main processes:**

1. It retrieves relevant excerpts from the vector store based on the user’s query.
   ‍
2. The retrieved information, together with the user’s query, are fed into a large language model for generation of a contextually rich response.

This combination allows for more informed and precise answers, especially where an LLM model alone (answering queries without added context) might struggle with factual accuracy.

**RAG can be implemented in many applications, such as:**

- **Customer service:** To retrieve specific information from a company’s knowledge base
- **Product recommendations:** To retrieve e-commerce product information based on user preferences and queries.
- **Legal document analysis:** To retrieve relevant case law or legal documents, and to generate summaries or insights.

#### RAG Pipeline Example

In the code below, we combine [Llama Index’s data ingestion and processing features](https://mirascope.com/blog/llamaindex-vs-langchain) with the prompt engineering capabilities of Mirascope, our own LLM development toolkit.

This application sets up a chatbot that mimics Steve Jobs by referencing his speeches. It passes user queries to a `retriever` object that finds (via vector similarity search) excerpts that are most relevant to the user’s query:

```python
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.base.base_retriever import BaseRetriever

from mirascope.core import openai, prompt_template

# Load documents and build index
documents = SimpleDirectoryReader("./steve_jobs_speeches").load_data()
retriever = VectorStoreIndex.from_documents(documents).as_retriever()


# Define the function to ask "Steve Jobs" a question
@openai.call("gpt-4o-mini")
@prompt_template("""
    SYSTEM:
    Your task is to respond to the user as though you are Steve Jobs.

    Here are some excerpts from Steve Jobs' speeches relevant to the user query.
    Use them as a reference for how to respond.

    <excerpts>
    {excerpts}
    </excerpts>
    """)
def ask_steve_jobs(query: str, retriever: BaseRetriever) -> openai.OpenAIDynamicConfig:
    """Retrieves excerpts from Steve Jobs' speeches relevant to `query` and generates a response."""
    excerpts = [node.get_content() for node in retriever.retrieve(query)]
    return {"computed_fields": {"excerpts": excerpts}}

# Get the user's query and ask "Steve Jobs"
query = input("(User): ")
response = ask_steve_jobs(query, retriever)
print(response.content)
```

Note that:

- Llama Index’s `SimpleDirectoryReader` loads the documents (in this case, speeches by Steve Jobs) from the specified directory. Its `VectorStoreIndex` creates an index from these documents, which allows the bot to retrieve relevant excerpts based on the user's query.
- We call an `as_retriever` method on the index from the loaded documents, turning it into a `retriever` object that retrieves relevant excerpts from Steve Jobs’ speeches.
- We define our `ask_steve_jobs` function and add two decorators: Mirascope’s `openai.call()` decorator turns a Python function into an OpenAI call (with little boilerplate) and `prompt_template` provides the instruction for the LLM; this saves developers from having to use Python docstrings for prompt templates, as these are traditionally intended for documenting code rather than defining operational logic.‍
- `ask_steve_jobs` retrieves excerpts relevant to the query using `retriever.retrieve(query)`. It returns a dictionary containing the `excerpts` as a computed field, which will be used by the OpenAI API to generate a response.

## Start Building Your Next App with Mirascope

Ready to turn your ideas into reality? Design your next LLM application with Mirascope’s Python toolkit for building LLM agents your way. Join our community of forward-thinking developers who are leveraging advanced [AI tools](https://mirascope.com/blog/llm-tools) and workflows to create innovative and scalable applications.

Want to learn more? You can find more Mirascope code samples both on our [documentation site](https://mirascope.com) and on our [GitHub page](https://github.com/mirascope/mirascope).
