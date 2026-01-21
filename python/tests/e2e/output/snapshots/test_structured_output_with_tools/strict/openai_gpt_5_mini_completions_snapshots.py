from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    ToolCall,
    ToolOutput,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "response": {
            "provider_id": "openai",
            "model_id": "openai/gpt-5-mini:completions",
            "provider_model_name": "gpt-5-mini:completions",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 286,
                "output_tokens": 1895,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 704,
                "raw": "CompletionUsage(completion_tokens=1895, prompt_tokens=286, total_tokens=2181, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=704, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0))",
                "total_tokens": 2181,
            },
            "messages": [
                UserMessage(
                    content=[
                        Text(
                            text="Please look up the book with ISBN 0-7653-1178-X and provide detailed info and a recommendation score"
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        ToolCall(
                            id="call_wC7OGOI9szqgVMKR3e8BoTEQ",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-5-mini:completions",
                    provider_model_name="gpt-5-mini:completions",
                    raw_message={
                        "role": "assistant",
                        "annotations": [],
                        "tool_calls": [
                            {
                                "id": "call_wC7OGOI9szqgVMKR3e8BoTEQ",
                                "function": {
                                    "arguments": '{"isbn":"0-7653-1178-X"}',
                                    "name": "get_book_info",
                                },
                                "type": "function",
                            }
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_wC7OGOI9szqgVMKR3e8BoTEQ",
                            name="get_book_info",
                            value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006}
 \n\

 \n\
    \n\
 \n\
 \n\
 \n\


 \n\
 \n\


 \n\
 \n\
 \n\
 \n\

 \n\
     \n\
 \n\
    \n\




 \n\
 \n\


 \n\
 \n\




 \n\
 \n\


 \n\
 \n\
 \n\

 \n\
 \n\



 \n\



 \n\
 \n\



 \n\
 \n\

 \n\
 \n\




 \n\
 \n\





 \n\
 \n\






 \n\
 \n\





 \n\
 \n\








 \n\
 \n\





 \n\
 \n\








 \n\
 \n\











 \n\
 \n\








 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\






 \n\
 \n\





 \n\
 \n\








 \n\
 \n\






 \n\
 \n\





 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\





 \n\
 \n\








 \n\
 \n\






 \n\
 \n\





 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\










 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\










 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\







 \n\
 \n\





 \n\
 \n\







 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\






 \n\
 \n\







 \n\
 \n\






 \n\
 \n\







 \n\
 \n\










 \n\
 \n\







 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\







 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\







 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\







 \n\
 \n\










 \n\
 \n\











 \n\
 \n\








 \n\
 \n\








 \n\
 \n\





 \n\
 \n\
 \n\
 \n\

 \n\
 \n\
 \n\
 \n\
 \n\
 \n\















 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\







 \n\
 \n\








 \n\
 \n\








 \n\
 \n\







 \n\
 \n\








 \n\
 \n\












 \n\
 \n\








 \n\
 \n\












 \n\
 \n\












 \n\
 \n\








 \n\
 \n\










 \n\
 \n\







 \n\
 \n\








 \n\
 \n\








 \n\
 \n\


 \n\
 \n\





 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\










 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\












 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\







 \n\
 \n\








 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\



"""
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-5-mini:completions",
                    provider_model_name="gpt-5-mini:completions",
                    raw_message={
                        "content": """\
{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006}
 \n\

 \n\
    \n\
 \n\
 \n\
 \n\


 \n\
 \n\


 \n\
 \n\
 \n\
 \n\

 \n\
     \n\
 \n\
    \n\




 \n\
 \n\


 \n\
 \n\




 \n\
 \n\


 \n\
 \n\
 \n\

 \n\
 \n\



 \n\



 \n\
 \n\



 \n\
 \n\

 \n\
 \n\




 \n\
 \n\





 \n\
 \n\






 \n\
 \n\





 \n\
 \n\








 \n\
 \n\





 \n\
 \n\








 \n\
 \n\











 \n\
 \n\








 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\






 \n\
 \n\





 \n\
 \n\








 \n\
 \n\






 \n\
 \n\





 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\





 \n\
 \n\








 \n\
 \n\






 \n\
 \n\





 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\










 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\










 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\







 \n\
 \n\





 \n\
 \n\







 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\






 \n\
 \n\







 \n\
 \n\






 \n\
 \n\







 \n\
 \n\










 \n\
 \n\







 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\







 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\







 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\







 \n\
 \n\










 \n\
 \n\











 \n\
 \n\








 \n\
 \n\








 \n\
 \n\





 \n\
 \n\
 \n\
 \n\

 \n\
 \n\
 \n\
 \n\
 \n\
 \n\















 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\







 \n\
 \n\








 \n\
 \n\








 \n\
 \n\







 \n\
 \n\








 \n\
 \n\












 \n\
 \n\








 \n\
 \n\












 \n\
 \n\












 \n\
 \n\








 \n\
 \n\










 \n\
 \n\







 \n\
 \n\








 \n\
 \n\








 \n\
 \n\


 \n\
 \n\





 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\










 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\












 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\







 \n\
 \n\








 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\








 \n\
 \n\






 \n\
 \n\












 \n\
 \n\



""",
                        "role": "assistant",
                        "annotations": [],
                    },
                ),
            ],
            "format": {
                "name": "BookSummary",
                "description": None,
                "schema": {
                    "properties": {
                        "title": {"title": "Title", "type": "string"},
                        "author": {"title": "Author", "type": "string"},
                        "pages": {"title": "Pages", "type": "integer"},
                        "publication_year": {
                            "title": "Publication Year",
                            "type": "integer",
                        },
                    },
                    "required": ["title", "author", "pages", "publication_year"],
                    "title": "BookSummary",
                    "type": "object",
                },
                "mode": "strict",
                "formatting_instructions": None,
            },
            "tools": [
                {
                    "name": "get_book_info",
                    "description": "Look up book information by ISBN.",
                    "parameters": """\
{
  "properties": {
    "isbn": {
      "title": "Isbn",
      "type": "string"
    }
  },
  "required": [
    "isbn"
  ],
  "additionalProperties": false,
  "defs": null
}\
""",
                    "strict": False,
                }
            ],
        }
    }
)
async_snapshot = snapshot(
    {
        "response": {
            "provider_id": "openai",
            "model_id": "openai/gpt-5-mini:completions",
            "provider_model_name": "gpt-5-mini:completions",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 286,
                "output_tokens": 4167,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 640,
                "raw": "CompletionUsage(completion_tokens=4167, prompt_tokens=286, total_tokens=4453, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=640, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0))",
                "total_tokens": 4453,
            },
            "messages": [
                UserMessage(
                    content=[
                        Text(
                            text="Please look up the book with ISBN 0-7653-1178-X and provide detailed info and a recommendation score"
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        ToolCall(
                            id="call_1OSveVXHx94x8VCBP8OnNrvW",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-5-mini:completions",
                    provider_model_name="gpt-5-mini:completions",
                    raw_message={
                        "role": "assistant",
                        "annotations": [],
                        "tool_calls": [
                            {
                                "id": "call_1OSveVXHx94x8VCBP8OnNrvW",
                                "function": {
                                    "arguments": '{"isbn":"0-7653-1178-X"}',
                                    "name": "get_book_info",
                                },
                                "type": "function",
                            }
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_1OSveVXHx94x8VCBP8OnNrvW",
                            name="get_book_info",
                            value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006} \n\



  \n\
  \n\
  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\














  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\



  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\



  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\



  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\



  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
 \n\








"""
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-5-mini:completions",
                    provider_model_name="gpt-5-mini:completions",
                    raw_message={
                        "content": """\
{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006} \n\



  \n\
  \n\
  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\














  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\



  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\



  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\



  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\



  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
 \n\








""",
                        "role": "assistant",
                        "annotations": [],
                    },
                ),
            ],
            "format": {
                "name": "BookSummary",
                "description": None,
                "schema": {
                    "properties": {
                        "title": {"title": "Title", "type": "string"},
                        "author": {"title": "Author", "type": "string"},
                        "pages": {"title": "Pages", "type": "integer"},
                        "publication_year": {
                            "title": "Publication Year",
                            "type": "integer",
                        },
                    },
                    "required": ["title", "author", "pages", "publication_year"],
                    "title": "BookSummary",
                    "type": "object",
                },
                "mode": "strict",
                "formatting_instructions": None,
            },
            "tools": [
                {
                    "name": "get_book_info",
                    "description": "Look up book information by ISBN.",
                    "parameters": """\
{
  "properties": {
    "isbn": {
      "title": "Isbn",
      "type": "string"
    }
  },
  "required": [
    "isbn"
  ],
  "additionalProperties": false,
  "defs": null
}\
""",
                    "strict": False,
                }
            ],
        }
    }
)
stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "openai",
            "model_id": "openai/gpt-5-mini:completions",
            "provider_model_name": "gpt-5-mini:completions",
            "finish_reason": None,
            "messages": [
                UserMessage(
                    content=[
                        Text(
                            text="Please look up the book with ISBN 0-7653-1178-X and provide detailed info and a recommendation score"
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        ToolCall(
                            id="call_BdrY6FJD36YmyhGU767Xj3jm",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-5-mini:completions",
                    provider_model_name="gpt-5-mini:completions",
                    raw_message=None,
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_BdrY6FJD36YmyhGU767Xj3jm",
                            name="get_book_info",
                            value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006}
 \n\
























































































































































































































































































































































































































































































































































































































































































































































"""
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-5-mini:completions",
                    provider_model_name="gpt-5-mini:completions",
                    raw_message=None,
                ),
            ],
            "format": {
                "name": "BookSummary",
                "description": None,
                "schema": {
                    "properties": {
                        "title": {"title": "Title", "type": "string"},
                        "author": {"title": "Author", "type": "string"},
                        "pages": {"title": "Pages", "type": "integer"},
                        "publication_year": {
                            "title": "Publication Year",
                            "type": "integer",
                        },
                    },
                    "required": ["title", "author", "pages", "publication_year"],
                    "title": "BookSummary",
                    "type": "object",
                },
                "mode": "strict",
                "formatting_instructions": None,
            },
            "tools": [
                {
                    "name": "get_book_info",
                    "description": "Look up book information by ISBN.",
                    "parameters": """\
{
  "properties": {
    "isbn": {
      "title": "Isbn",
      "type": "string"
    }
  },
  "required": [
    "isbn"
  ],
  "additionalProperties": false,
  "defs": null
}\
""",
                    "strict": False,
                }
            ],
            "usage": {
                "input_tokens": 286,
                "output_tokens": 1252,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 640,
                "raw": "None",
                "total_tokens": 1538,
            },
            "n_chunks": 601,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "openai",
            "model_id": "openai/gpt-5-mini:completions",
            "provider_model_name": "gpt-5-mini:completions",
            "finish_reason": None,
            "messages": [
                UserMessage(
                    content=[
                        Text(
                            text="Please look up the book with ISBN 0-7653-1178-X and provide detailed info and a recommendation score"
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        ToolCall(
                            id="call_aBpvL0Qsb1MYZUjwKJ6MWqXY",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-5-mini:completions",
                    provider_model_name="gpt-5-mini:completions",
                    raw_message=None,
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_aBpvL0Qsb1MYZUjwKJ6MWqXY",
                            name="get_book_info",
                            value="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006}
 \n\




















































































































































































































































































































































































































































































 \n\
































































































 \n\
                                                                       \n\
                                                                                               \n\
                                                                                          \n\
                                                                                \n\
                                                                                    \n\
                                                                                                     \n\
                                                                                                        \n\
                                                                                               \n\
                                                                                                    \n\
                                                                                          \n\
                                                                                                                   \n\
 \n\



























































































































































































































































 \n\































































 \n\











































































"""
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-5-mini:completions",
                    provider_model_name="gpt-5-mini:completions",
                    raw_message=None,
                ),
            ],
            "format": {
                "name": "BookSummary",
                "description": None,
                "schema": {
                    "properties": {
                        "title": {"title": "Title", "type": "string"},
                        "author": {"title": "Author", "type": "string"},
                        "pages": {"title": "Pages", "type": "integer"},
                        "publication_year": {
                            "title": "Publication Year",
                            "type": "integer",
                        },
                    },
                    "required": ["title", "author", "pages", "publication_year"],
                    "title": "BookSummary",
                    "type": "object",
                },
                "mode": "strict",
                "formatting_instructions": None,
            },
            "tools": [
                {
                    "name": "get_book_info",
                    "description": "Look up book information by ISBN.",
                    "parameters": """\
{
  "properties": {
    "isbn": {
      "title": "Isbn",
      "type": "string"
    }
  },
  "required": [
    "isbn"
  ],
  "additionalProperties": false,
  "defs": null
}\
""",
                    "strict": False,
                }
            ],
            "usage": {
                "input_tokens": 286,
                "output_tokens": 1768,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 896,
                "raw": "None",
                "total_tokens": 2054,
            },
            "n_chunks": 861,
        }
    }
)
