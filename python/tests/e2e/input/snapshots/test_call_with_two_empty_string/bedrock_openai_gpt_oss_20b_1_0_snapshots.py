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
                "input_tokens": 69,
                "output_tokens": 310,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "CompletionUsage(completion_tokens=310, prompt_tokens=69, total_tokens=379, completion_tokens_details=None, prompt_tokens_details=None)",
                "total_tokens": 379,
            },
            "messages": [
                UserMessage(content=[Text(text=""), Text(text="")]),
                AssistantMessage(
                    content=[
                        Text(
                            text='<reasoning>We have no conversation. The prompt says "What\'s the best thing about your superhero name?" But wait: The conversation is empty. The last user said nothing? Actually the user hasn\'t said. The conversation logs: There\'s a developer instruction: "You are ChatGPT" etc. Then user says nothing. So we have no direction. Possibly we should ask a question. We need to respond. Maybe the instruction "What\'s the best thing about your superhero name?" is in some context? The original partner question may be something else? The conversation is blank. Probably we should respond politely, asking for more context. Since no content. But we might answer with "I don\'t have a superhero name." The user might be expecting some answer. The best thing about... we don\'t know. We can say "my name is ChatGPT..." But treat as Might be a conversation to test ability. But likely we should respond with: "As a virtual assistant, I don\'t have a superhero name, but if I did..." So produce a creative answer. Ok.</reasoning>I don’t actually have a superhero alias—at least not yet. If I did, the best thing about my name would probably be what it says about who I am: a name that powers curiosity, sparks imagination, and invites people to think bigger than the ordinary. It would be a single word or phrase that instantly hints at both strength and vulnerability, reminds folks that even the biggest “hero” starts with a single choice to help others. 🌟'
                        )
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/openai.gpt-oss-20b-1:0",
                    provider_model_name="openai.gpt-oss-20b-1:0",
                    raw_message={
                        "content": '<reasoning>We have no conversation. The prompt says "What\'s the best thing about your superhero name?" But wait: The conversation is empty. The last user said nothing? Actually the user hasn\'t said. The conversation logs: There\'s a developer instruction: "You are ChatGPT" etc. Then user says nothing. So we have no direction. Possibly we should ask a question. We need to respond. Maybe the instruction "What\'s the best thing about your superhero name?" is in some context? The original partner question may be something else? The conversation is blank. Probably we should respond politely, asking for more context. Since no content. But we might answer with "I don\'t have a superhero name." The user might be expecting some answer. The best thing about... we don\'t know. We can say "my name is ChatGPT..." But treat as Might be a conversation to test ability. But likely we should respond with: "As a virtual assistant, I don\'t have a superhero name, but if I did..." So produce a creative answer. Ok.</reasoning>I don’t actually have a superhero alias—at least not yet. If I did, the best thing about my name would probably be what it says about who I am: a name that powers curiosity, sparks imagination, and invites people to think bigger than the ordinary. It would be a single word or phrase that instantly hints at both strength and vulnerability, reminds folks that even the biggest “hero” starts with a single choice to help others. 🌟',
                        "role": "assistant",
                    },
                ),
            ],
            "format": None,
            "tools": [],
        }
    }
)
