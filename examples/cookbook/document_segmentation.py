from pydantic import BaseModel, Field

from mirascope.core import openai, prompt_template

SAMPLE_ARTICLE = """
The Rise of Artificial Intelligence in Healthcare: A Comprehensive Overview
Regulatory bodies like the FDA are working to develop frameworks for evaluating and 
approving AI-based medical technologies, balancing the need for innovation with patient 
safety concerns. From diagnosis to treatment planning, AI is making significant strides 
in various areas of healthcare, promising to transform the way we approach medicine and 
patient care in the 21st century. Machine learning models can screen vast libraries of 
compounds much faster than traditional methods, identifying promising drug candidates 
for further investigation. These advancements are particularly crucial in regions with 
a shortage of trained radiologists, as AI can serve as a powerful assistive tool to 
healthcare providers. As AI continues to evolve, it promises to augment human 
capabilities in healthcare, allowing for more precise, efficient, and personalized 
medical care. AI algorithms can identify patterns in patient data that may not be 
apparent to human clinicians, leading to more precise treatment recommendations. 
Beyond diagnosis and treatment planning, AI is proving valuable in providing clinical 
decision support to healthcare providers. Artificial Intelligence (AI) is 
revolutionizing the healthcare industry, offering unprecedented opportunities to 
improve patient care, streamline operations, and advance medical research. 
In patient monitoring, AI algorithms can continuously analyze data from ICU equipment 
or wearable devices, alerting healthcare providers to subtle changes in a patient's 
condition before they become critical. For instance, AI-powered systems have shown 
impressive results in detecting early signs of breast cancer in mammograms, identifying 
lung nodules in chest X-rays, and spotting signs of diabetic retinopathy in eye scans. 
At its core, AI in healthcare relies on machine learning algorithms and neural networks 
that can process vast amounts of medical data. Issues such as data privacy, algorithmic 
bias, and the need for regulatory frameworks are ongoing concerns that need to be 
addressed. Companies like Atomwise and Exscientia are already using AI to discover 
novel drug candidates for various diseases, including COVID-19. This tailored approach 
has the potential to significantly improve treatment efficacy and reduce adverse 
effects. One of the most promising applications of AI in healthcare is in medical 
imaging. Ensuring that AI systems are trained on diverse, representative data and 
regularly audited for bias is crucial for their equitable implementation. Traditional 
drug development is a time-consuming and expensive process, often taking over a decade 
and costing billions of dollars to bring a new drug to market. By analyzing vast 
amounts of patient data, including genetic information, lifestyle factors, and 
treatment outcomes, AI systems can help predict which treatments are likely to be most 
effective for individual patients. These systems are trained on diverse datasets, 
including electronic health records, medical imaging, genetic information, and even 
data from wearable devices. AI can also predict potential side effects and 
drug interactions, helping to prioritize safer compounds earlier in the development 
process. Additionally, there's a need for healthcare professionals to adapt and 
acquire new skills to work effectively alongside AI systems. Machine learning 
algorithms can now analyze X-rays, MRIs, and CT scans with remarkable accuracy, 
often outperforming human radiologists in detecting certain conditions. While AI will 
not replace human healthcare providers, it will undoubtedly become an indispensable
tool in the medical toolkit, helping to address global healthcare challenges and 
improve patient outcomes on a massive scale. The sensitive nature of health data 
requires robust security measures and clear guidelines on data usage and sharing. 
Emerging areas of research include Natural Language Processing (NLP) for analyzing 
clinical notes and medical literature, AI-powered robotic surgery assistants for 
enhanced precision in complex procedures, predictive analytics for population health 
management and disease prevention, and virtual nursing assistants to provide basic 
patient care and monitoring. This proactive approach to patient care has the potential 
to prevent complications and improve outcomes, particularly for chronic disease 
management. However, the integration of AI in healthcare is not without challenges. 
As these AI systems learn from more data, they become increasingly accurate and capable 
of handling complex medical tasks. Algorithmic bias is a particularly pressing issue, 
as AI systems trained on non-diverse datasets may perform poorly for underrepresented 
populations. Despite these challenges, the potential benefits of AI in healthcare are 
immense. For example, in oncology, AI systems are being used to analyze tumor genetics 
and patient characteristics to recommend personalized cancer treatments. AI-powered 
systems can analyze molecular structures, predict drug-target interactions, and 
simulate clinical trials, potentially reducing the time and cost of bringing new drugs 
to market. This includes understanding the capabilities and limitations of AI tools and 
interpreting their outputs in the context of patient care. Similarly, in psychiatry, 
AI is helping to predict patient responses to different antidepressants, potentially 
reducing the trial-and-error approach often used in mental health treatment. As 
technology continues to advance, we can expect to see even more innovative applications 
of AI that will shape the future of medicine and improve patient outcomes worldwide.
"""


class Segment(BaseModel):
    topic: str = Field(..., description="The topic of the section.")
    content: str = Field(..., description="The content that relates to the topic.")


@openai.call("gpt-4o-mini", response_model=list[Segment])
@prompt_template(
    """
    SYSTEM:
    You are an expert in document semantic segmentation.
    Can you segment the following article into coherent secttions based on topic?

    USER:
    {article}
    """
)
def semantic_segmentation(article: str): ...


segments = semantic_segmentation(SAMPLE_ARTICLE)


@openai.call("gpt-4o-mini")
@prompt_template(
    """
    SYSTEM:
    You are an expert Healthcare. Answer the following question based on the segments?

    segments:
    {segments}

    USER:
    {question}
    """
)
def segmented_document(segments: list[Segment], question: str): ...


segmented = segmented_document(
    segments,
    "What are the main applications of AI in healthcare",
)
print(segmented.content)
