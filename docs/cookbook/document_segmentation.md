# Document Segmentation

In this recipe, we go over how to do semantic document segmentation. Topics and themes of articles can frequently be dispersed across multiple sections or even separate files. We will be using OpenAI GPT-4o-mini to break down an article into topics and themes.

??? tip "Mirascope Concepts Used"

    - [Prompts](../learn/prompts.md)
    - [Calls](../learn/calls.md)
    - [Response Models](../learn/response_models.md)

!!! note "Background"

    Traditional machine learning techniques often relied on handcrafted features, such as detecting paragraph breaks, identifying section headers, or using statistical measures of text coherence. While effective for well-structured documents, these approaches often struggled with more complex or inconsistently formatted texts. LLMs have revolutionized document segmentation by enabling more flexible and context-aware parsing of text, regardless of formatting or structure.
    
## Create your prompt

We will create a simple prompt that instructs the LLM to semantically segment an article:

```python
from pydantic import BaseModel, Field

from mirascope.core import openai

SAMPLE_ARTICLE = """
The Rise of Artificial Intelligence in Healthcare: A Comprehensive Overview
Regulatory bodies like the FDA are working to develop frameworks for evaluating and approving AI-based medical technologies, balancing the need for innovation with patient safety concerns. From diagnosis to treatment planning, AI is making significant strides in various areas of healthcare, promising to transform the way we approach medicine and patient care in the 21st century. Machine learning models can screen vast libraries of compounds much faster than traditional methods, identifying promising drug candidates for further investigation. These advancements are particularly crucial in regions with a shortage of trained radiologists, as AI can serve as a powerful assistive tool to healthcare providers. As AI continues to evolve, it promises to augment human capabilities in healthcare, allowing for more precise, efficient, and personalized medical care. AI algorithms can identify patterns in patient data that may not be apparent to human clinicians, leading to more precise treatment recommendations. Beyond diagnosis and treatment planning, AI is proving valuable in providing clinical decision support to healthcare providers. Artificial Intelligence (AI) is revolutionizing the healthcare industry, offering unprecedented opportunities to improve patient care, streamline operations, and advance medical research. In patient monitoring, AI algorithms can continuously analyze data from ICU equipment or wearable devices, alerting healthcare providers to subtle changes in a patient's condition before they become critical. For instance, AI-powered systems have shown impressive results in detecting early signs of breast cancer in mammograms, identifying lung nodules in chest X-rays, and spotting signs of diabetic retinopathy in eye scans. At its core, AI in healthcare relies on machine learning algorithms and neural networks that can process vast amounts of medical data. Issues such as data privacy, algorithmic bias, and the need for regulatory frameworks are ongoing concerns that need to be addressed. Companies like Atomwise and Exscientia are already using AI to discover novel drug candidates for various diseases, including COVID-19. This tailored approach has the potential to significantly improve treatment efficacy and reduce adverse effects. One of the most promising applications of AI in healthcare is in medical imaging. Ensuring that AI systems are trained on diverse, representative data and regularly audited for bias is crucial for their equitable implementation. Traditional drug development is a time-consuming and expensive process, often taking over a decade and costing billions of dollars to bring a new drug to market. By analyzing vast amounts of patient data, including genetic information, lifestyle factors, and treatment outcomes, AI systems can help predict which treatments are likely to be most effective for individual patients. These systems are trained on diverse datasets, including electronic health records, medical imaging, genetic information, and even data from wearable devices. AI can also predict potential side effects and drug interactions, helping to prioritize safer compounds earlier in the development process. Additionally, there's a need for healthcare professionals to adapt and acquire new skills to work effectively alongside AI systems. Machine learning algorithms can now analyze X-rays, MRIs, and CT scans with remarkable accuracy, often outperforming human radiologists in detecting certain conditions. While AI will not replace human healthcare providers, it will undoubtedly become an indispensable tool in the medical toolkit, helping to address global healthcare challenges and improve patient outcomes on a massive scale. The sensitive nature of health data requires robust security measures and clear guidelines on data usage and sharing. Emerging areas of research include Natural Language Processing (NLP) for analyzing clinical notes and medical literature, AI-powered robotic surgery assistants for enhanced precision in complex procedures, predictive analytics for population health management and disease prevention, and virtual nursing assistants to provide basic patient care and monitoring. This proactive approach to patient care has the potential to prevent complications and improve outcomes, particularly for chronic disease management. However, the integration of AI in healthcare is not without challenges. As these AI systems learn from more data, they become increasingly accurate and capable of handling complex medical tasks. Algorithmic bias is a particularly pressing issue, as AI systems trained on non-diverse datasets may perform poorly for underrepresented populations. Despite these challenges, the potential benefits of AI in healthcare are immense. For example, in oncology, AI systems are being used to analyze tumor genetics and patient characteristics to recommend personalized cancer treatments. AI-powered systems can analyze molecular structures, predict drug-target interactions, and simulate clinical trials, potentially reducing the time and cost of bringing new drugs to market. This includes understanding the capabilities and limitations of AI tools and interpreting their outputs in the context of patient care. Similarly, in psychiatry, AI is helping to predict patient responses to different antidepressants, potentially reducing the trial-and-error approach often used in mental health treatment. As technology continues to advance, we can expect to see even more innovative applications of AI that will shape the future of medicine and improve patient outcomes worldwide.
"""

class Segment(BaseModel):
    topic: str = Field(..., description="The topic of the section.")
    content: str = Field(..., description="The content that relates to the topic.")

@openai.call("gpt-4o-mini", response_model=list[Segment])
def semantic_segmentation(article: str):
    """
    SYSTEM:
    You are an expert in document semantic segmentation.
    Can you segment the following article into coherent secttions based on topic?

    USER:
    {article}
    """
```

We use Mirascope `response_model` to tell the LLM to output a list of `Segment` that will break the article into multiple different topics.

## Make a call

We can see that there are sub-sections that the LLM created for us and also the content related to those sub-sections:

```python
print(semantic_segmentation(SAMPLE_ARTICLE))
# > [
#        Segment(
#            topic="Introduction to AI in Healthcare",
#            content="Artificial Intelligence (AI) is revolutionizing the healthcare industry, offering unprecedented opportunities to improve patient care, streamline operations, and advance medical research.",
#        ),
#        Segment(
#            topic="Regulatory Frameworks",
#            content="Regulatory bodies like the FDA are working to develop frameworks for evaluating and approving AI-based medical technologies, balancing the need for innovation with patient safety concerns.",
#        ),
#        Segment(
#            topic="AI in Diagnosis and Treatment",
#            content="From diagnosis to treatment planning, AI is making significant strides in various areas of healthcare, promising to transform the way we approach medicine and patient care in the 21st century.",
#        ),
#        Segment(
#            topic="Applications of AI in Medical Imaging",
#            content="One of the most promising applications of AI in healthcare is in medical imaging. For instance, AI-powered systems have shown impressive results in detecting early signs of breast cancer in mammograms, identifying lung nodules in chest X-rays, and spotting signs of diabetic retinopathy in eye scans.",
#        ),
#        Segment(
#            topic="AI in Drug Discovery",
#            content="Companies like Atomwise and Exscientia are already using AI to discover novel drug candidates for various diseases, including COVID-19. Traditional drug development is a time-consuming and expensive process, often taking over a decade and costing billions of dollars to bring a new drug to market.",
#        ),
#        Segment(
#            topic="Patient Monitoring and Clinical Decision Support",
#            content="In patient monitoring, AI algorithms can continuously analyze data from ICU equipment or wearable devices, alerting healthcare providers to subtle changes in a patient's condition before they become critical.",
#        ),
#        Segment(
#            topic="Machine Learning and Data Privacy Concerns",
#            content="AI in healthcare relies on machine learning algorithms and neural networks that can process vast amounts of medical data. Issues such as data privacy, algorithmic bias, and the need for regulatory frameworks are ongoing concerns.",
#        ),
#        Segment(
#            topic="Challenges in AI Integration",
#            content="However, the integration of AI in healthcare is not without challenges. Algorithmic bias is a particularly pressing issue, as AI systems trained on non-diverse datasets may perform poorly for underrepresented populations.",
#        ),
#        Segment(
#            topic="Future of AI in Healthcare",
#            content="As technology continues to advance, we can expect to see even more innovative applications of AI that will shape the future of medicine and improve patient outcomes worldwide.",
#        ),
#        Segment(
#            topic="Conclusion",
#            content="While AI will not replace human healthcare providers, it will undoubtedly become an indispensable tool in the medical toolkit, helping to address global healthcare challenges and improve patient outcomes on a massive scale.",
#        ),
#   ]
```

The impact of segmenting a single article is not as obvious compared to segmenting multiple articles or pages. However, by compiling multiple articles, you can gain a deeper understanding of a particular topic or theme without reading each article in full.

!!! tip "Additional Real-World Applications"
    - **General Information Retrieval**: Segmentation helps in organizing large documents into smaller, searchable units, improving the efficiency of information retrieval systems.
    - **Education**: Create study guides or slides from textbook material using summaries.
    - **Productivity**: Summarize email chains, slack threads, word documents for your day-to-day.
    - **Summarization**: Segmentation is a crucial step in creating summaries of long documents or articles.

When adapting this recipe to your specific use-case, consider the following:
    - Refine your prompts to provide clear instructions and relevant context for text summarization.
    - Experiment with different model providers and version to balance quality and speed.
    - Provide a feedback loop, use an LLM to evaluate the quality of the summary based on a criteria and feed that back into the prompt for refinement.
