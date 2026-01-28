from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": {
            "provider_id": "bedrock",
            "model_id": "bedrock/openai.gpt-oss-20b-1:0",
            "provider_model_name": "openai.gpt-oss-20b-1:0",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 100,
                "output_tokens": 480,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "CompletionUsage(completion_tokens=480, prompt_tokens=100, total_tokens=580, completion_tokens_details=None, prompt_tokens_details=None)",
                "total_tokens": 580,
            },
            "messages": [
                UserMessage(content=[Text(text="Who created you?")]),
                AssistantMessage(
                    content=[
                        Text(text="I am a large language model, trained by Google.")
                    ],
                    provider_id="google",
                    model_id="google/gemini-2.5-flash",
                    provider_model_name="gemini-2.5-flash",
                    raw_message={
                        "parts": [
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": "I am a large language model, trained by Google.",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            }
                        ],
                        "role": "model",
                    },
                ),
                UserMessage(content=[Text(text="Can you double-check that?")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
<reasoning>The user asks "Can you double-check that?" They want confirmation that I was made by Google. I must comply with relevant policy. The question is about source of creation. The assistant earlier says "I am a large language model trained by Google." That is correct. The user wants a double-check. That is fine. We can verify and state credible. We have to confirm. There's no disallowed content. It's fine. The only policy aspect is that we must provide accurate info. I can confirm: I was developed by Google. Possibly mention "Language model" belongs to Google. There's no policy conflict. They also want a double-check. So just confirm or provide more details. It's allowed. No policy conflicts. \n\

Thus provide answer: I was created by Google, specifically by Google DeepMind (or? Actually ChatGPT is by OpenAI, but the user says "Google"? But the assistant answered earlier. But we want to confirm the earlier answer. But is it correct? The assistant is ChatGPT, which is OpenAI. But the user presumably thinks I'm a Google model. But the assistant is indeed ChatGPT, which is OpenAI. So the assistant might be mistaken. Wait, the last assistant said "I am a large language model, trained by Google." That is incorrect: ChatGPT is from OpenAI. However, the system says we are "ChatGPT" but maybe they've mistaken. The system message says "You are ChatGPT...". So we indeed are ChatGPT from OpenAI. The user earlier responded "I am a large language model, trained by Google." That answer is incorrect. The user now asks "Can you double-check that?" They suspect the earlier answer might be wrong. So we need to correct them: We are an OpenAI model.

Given policy: we must correct any misinformation. There's no disallowed content. So we should produce a correct answer: We are created by OpenAI. And no hack. Great.

Thus, we should correct user.</reasoning>I’m sorry for the confusion. I’m actually a model built by\u202fOpenAI, not Google. My architecture (based on the GPT‑4 family) was trained on a diverse range of internet text by the OpenAI team. If you have any other questions about my background or how I work, feel free to ask!\
"""
                        )
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/openai.gpt-oss-20b-1:0",
                    provider_model_name="openai.gpt-oss-20b-1:0",
                    raw_message={
                        "content": """\
<reasoning>The user asks "Can you double-check that?" They want confirmation that I was made by Google. I must comply with relevant policy. The question is about source of creation. The assistant earlier says "I am a large language model trained by Google." That is correct. The user wants a double-check. That is fine. We can verify and state credible. We have to confirm. There's no disallowed content. It's fine. The only policy aspect is that we must provide accurate info. I can confirm: I was developed by Google. Possibly mention "Language model" belongs to Google. There's no policy conflict. They also want a double-check. So just confirm or provide more details. It's allowed. No policy conflicts. \n\

Thus provide answer: I was created by Google, specifically by Google DeepMind (or? Actually ChatGPT is by OpenAI, but the user says "Google"? But the assistant answered earlier. But we want to confirm the earlier answer. But is it correct? The assistant is ChatGPT, which is OpenAI. But the user presumably thinks I'm a Google model. But the assistant is indeed ChatGPT, which is OpenAI. So the assistant might be mistaken. Wait, the last assistant said "I am a large language model, trained by Google." That is incorrect: ChatGPT is from OpenAI. However, the system says we are "ChatGPT" but maybe they've mistaken. The system message says "You are ChatGPT...". So we indeed are ChatGPT from OpenAI. The user earlier responded "I am a large language model, trained by Google." That answer is incorrect. The user now asks "Can you double-check that?" They suspect the earlier answer might be wrong. So we need to correct them: We are an OpenAI model.

Given policy: we must correct any misinformation. There's no disallowed content. So we should produce a correct answer: We are created by OpenAI. And no hack. Great.

Thus, we should correct user.</reasoning>I’m sorry for the confusion. I’m actually a model built by\u202fOpenAI, not Google. My architecture (based on the GPT‑4 family) was trained on a diverse range of internet text by the OpenAI team. If you have any other questions about my background or how I work, feel free to ask!\
""",
                        "role": "assistant",
                    },
                ),
            ],
            "format": None,
            "tools": [],
        }
    }
)
