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
            "provider_id": "azure",
            "model_id": "azure/openai/gpt-5-mini",
            "provider_model_name": "gpt-5-mini",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 286,
                "output_tokens": 2606,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 960,
                "raw": "CompletionUsage(completion_tokens=2606, prompt_tokens=286, total_tokens=2892, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=960, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0))",
                "total_tokens": 2892,
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
                            id="call_hzxSgcRFKwD5KnbYTz0IhweD",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider_id="azure",
                    model_id="azure/openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini",
                    raw_message={
                        "role": "assistant",
                        "annotations": [],
                        "tool_calls": [
                            {
                                "id": "call_hzxSgcRFKwD5KnbYTz0IhweD",
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
                            id="call_hzxSgcRFKwD5KnbYTz0IhweD",
                            name="get_book_info",
                            result="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
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


  \r\r
  \n\
 \r\r
  \n\
 \r\r
\r\r
\r\r
  \n\
 \n\
 \n\



\r\r
\r\r



\r\r
\r\r



\r\r
\r\r




\r\r
\r\r
\r\r
\r\r
\r\r



\r\r
\r\r





\r\r
 \n\








\r


 \n\








\r



\r





\r







\r





\r





\r





\r





\r





\r





\r
\r
\r
                                                                 \n\

                                                                                        \n\

                                                                                                             \n\


                                                                                                            \n\


                                                                                                             \n\
                                                                                                         \n\
                                                                                                             \n\


                                                                                                             \n\


                                                                                                             \n\


                                                                                                             \n\


                                                                                                             \n\




                                                                                                                             \n\




                                                                                                                              \n\


                                                                                                                              \n\


                                                                                                                              \n\


                                                                                                                              \n\


                                                                                                                              \n\


                                                                                                                              \n\


                                                                                                                             \n\


                                                                                                                             \n\


                                                                                                                              \n\


                                                                                                                              \n\


                                                                                                                              \n\


                                                                                                                              \n\


                                                                                                                              \n\


                                                                                                                               \n\

                                                                                                                              \n\


                                                                                                                              \n\


                                                                                                                              \n\


                                                                                                                              \n\


                                                                                                                              \n\



                                                                                                                             \n\


                                                                                                                             \n\


                                                                                                                              \n\


                                                                                                                              \n\


                                                                                                                              \n\


                                                                                                                              \n\


                                                                                                                              \n\


                                                                                                                              \n\


                                                                                                                              \n\


                                                                                                                               \n\


                                                                                                                              \n\


                                                                                                                              \n\


                                                                                                                              \n\
                                                                                                                              \n\


                                                                                                                              \n\


                                                                                                                              \n\


                                                                                                                              \n\


                                                                                                                              \n\


                                                                                                                               \n\

\r


\r\r
\r\r



\r


\r


\r


\r


\r


\r


\r\r


\r
\r
\r













\r
\r
\r
\r\r
\r\r
\r
\r
\r
\r
\r
\r
\r

\r
\r
\r


\r
\r
\r


\r
\r
\r


\r
\r
\r


\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
                                                                   \n\

                                                                                     \n\


                                                                                         \n\




                                                                                        \n\


                                                                                              \n\
                                                                                        \n\


                                                                                       \n\
                                                                                        \n\


                                                                                        \n\


                                                                                        \n\


                                                                                        \n\


                                                                                        \n\


                                                                                         \n\




                                                                                         \n\


                                                                                        \n\


                                                                                         \n\


                                                                                         \n\


                                                                                         \n\


                                                                                         \n\


                                                                                         \n\


                                                                                         \n\


                                                                                         \n\


                                                                                          \n\

                                                                                                \n\

                                                                                                 \n\


                                                                \n\



                                                                                           \n\


                                                                                                \n\

                                                                                                 \n\


                                                                                              \n\


                                                                                                 \n\


                                                                                                 \n\

                                                                                                 \n\


                                                                                                 \n\



                                                                                                 \n\


                                                                                                 \n\


                                                                                                 \n\





\r\r
\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r
\r\r



\r
\r
\r


\r
\r
\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r

\r
\r
\r
\r




\r
\r
\r

\r
\r
\r
\r


\r
\r
\r


\r
\r
\r
\r

\r
\r
\r
\r


\r
\r
\r
\r

\r
\r
\r


\r
\r
\r


\r
\r
\r
\r


\r
\r
\r


\r
\r
\r


\r
\r
\r


\r
\r
\r




\r
\r
\r


\r
\r
\r


\r
\r
\r


\r
\r
\r
\r\r


\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r


\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r


\r
\r
\r


\r
\r
\r


\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r


\r
\r
\r


\r
\r
\r


\r
\r
\r
\r
\r
\r

\r
\r
\r
\r
\r
\r
\r


\r
\r
\r
\r

\r
\r
\r
\r
\r
\r
\r
\r
\r
\r


\r
\r
\r


\r
\r
\r


\r
\r
\r


\r
\r
\r
\r
\r


\r
\r
\r
\r


\r
\r
\r


\r
\r
\r
\r


\r
\r
\r
\r
\r
\r

\r
\r
\r




\r
\r
\r


\r
\r
\r
\r

\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r

\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r


\r
\r
\r


\r
\r
\r


\r
\r
\r
\r
\r
\r

\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r

\r
\r
\r


\r
\r
\r
\r


\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r


\r
\r
\r


\r
\r
\r


\r
\r
\r
\r


\r
\r
\r
\r
\r
\r

\r
\r
\r


\r
\r
\r


\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r


\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r


\r
\r
\r
\r
\r
\r

\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r


\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r

\r
\r
\r


\r
\r
\r
\r\r


\r
\r
\r


\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r

\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r

\r
\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r


\r
\r
\r


\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r


\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r

\r
\r
\r


\r
\r
\r
\r


\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r

\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r


\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
 \n\




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r


\r
\r
\r


\r
\r
\r
\r
\r
\r
\r


\r
\r
\r
\r


\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r


\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
 \r
\r



\r

\r
\r
\r


\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r


\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r


\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r


\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r


\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r
\r




\r




\r
\r
\r


\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r


\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r


\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r\r
 \n\

\r
\r
\r
\r
\r\r
\r\r



\r
\r
\r


\r
\r
\r
\r
\r\r
 \n\

\r
\r
\r


\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r


\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r


\r
\r
\r
\r
\r
\r
 \n\





"""
                        )
                    ],
                    provider_id="azure",
                    model_id="azure/openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini",
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


  \r\r
  \n\
 \r\r
  \n\
 \r\r
\r\r
\r\r
  \n\
 \n\
 \n\



\r\r
\r\r



\r\r
\r\r



\r\r
\r\r




\r\r
\r\r
\r\r
\r\r
\r\r



\r\r
\r\r





\r\r
 \n\








\r


 \n\








\r



\r





\r







\r





\r





\r





\r





\r





\r





\r
\r
\r
                                                                 \n\

                                                                                        \n\

                                                                                                             \n\


                                                                                                            \n\


                                                                                                             \n\
                                                                                                         \n\
                                                                                                             \n\


                                                                                                             \n\


                                                                                                             \n\


                                                                                                             \n\


                                                                                                             \n\




                                                                                                                             \n\




                                                                                                                              \n\


                                                                                                                              \n\


                                                                                                                              \n\


                                                                                                                              \n\


                                                                                                                              \n\


                                                                                                                              \n\


                                                                                                                             \n\


                                                                                                                             \n\


                                                                                                                              \n\


                                                                                                                              \n\


                                                                                                                              \n\


                                                                                                                              \n\


                                                                                                                              \n\


                                                                                                                               \n\

                                                                                                                              \n\


                                                                                                                              \n\


                                                                                                                              \n\


                                                                                                                              \n\


                                                                                                                              \n\



                                                                                                                             \n\


                                                                                                                             \n\


                                                                                                                              \n\


                                                                                                                              \n\


                                                                                                                              \n\


                                                                                                                              \n\


                                                                                                                              \n\


                                                                                                                              \n\


                                                                                                                              \n\


                                                                                                                               \n\


                                                                                                                              \n\


                                                                                                                              \n\


                                                                                                                              \n\
                                                                                                                              \n\


                                                                                                                              \n\


                                                                                                                              \n\


                                                                                                                              \n\


                                                                                                                              \n\


                                                                                                                               \n\

\r


\r\r
\r\r



\r


\r


\r


\r


\r


\r


\r\r


\r
\r
\r













\r
\r
\r
\r\r
\r\r
\r
\r
\r
\r
\r
\r
\r

\r
\r
\r


\r
\r
\r


\r
\r
\r


\r
\r
\r


\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
                                                                   \n\

                                                                                     \n\


                                                                                         \n\




                                                                                        \n\


                                                                                              \n\
                                                                                        \n\


                                                                                       \n\
                                                                                        \n\


                                                                                        \n\


                                                                                        \n\


                                                                                        \n\


                                                                                        \n\


                                                                                         \n\




                                                                                         \n\


                                                                                        \n\


                                                                                         \n\


                                                                                         \n\


                                                                                         \n\


                                                                                         \n\


                                                                                         \n\


                                                                                         \n\


                                                                                         \n\


                                                                                          \n\

                                                                                                \n\

                                                                                                 \n\


                                                                \n\



                                                                                           \n\


                                                                                                \n\

                                                                                                 \n\


                                                                                              \n\


                                                                                                 \n\


                                                                                                 \n\

                                                                                                 \n\


                                                                                                 \n\



                                                                                                 \n\


                                                                                                 \n\


                                                                                                 \n\





\r\r
\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r


\r\r
\r\r



\r
\r
\r


\r
\r
\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r

\r
\r
\r
\r




\r
\r
\r

\r
\r
\r
\r


\r
\r
\r


\r
\r
\r
\r

\r
\r
\r
\r


\r
\r
\r
\r

\r
\r
\r


\r
\r
\r


\r
\r
\r
\r


\r
\r
\r


\r
\r
\r


\r
\r
\r


\r
\r
\r




\r
\r
\r


\r
\r
\r


\r
\r
\r


\r
\r
\r
\r\r


\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r


\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r


\r
\r
\r


\r
\r
\r


\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r


\r
\r
\r


\r
\r
\r


\r
\r
\r
\r
\r
\r

\r
\r
\r
\r
\r
\r
\r


\r
\r
\r
\r

\r
\r
\r
\r
\r
\r
\r
\r
\r
\r


\r
\r
\r


\r
\r
\r


\r
\r
\r


\r
\r
\r
\r
\r


\r
\r
\r
\r


\r
\r
\r


\r
\r
\r
\r


\r
\r
\r
\r
\r
\r

\r
\r
\r




\r
\r
\r


\r
\r
\r
\r

\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r

\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r


\r
\r
\r


\r
\r
\r


\r
\r
\r
\r
\r
\r

\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r

\r
\r
\r


\r
\r
\r
\r


\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r


\r
\r
\r


\r
\r
\r


\r
\r
\r
\r


\r
\r
\r
\r
\r
\r

\r
\r
\r


\r
\r
\r


\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r


\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r


\r
\r
\r
\r
\r
\r

\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r


\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r

\r
\r
\r


\r
\r
\r
\r\r


\r
\r
\r


\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r

\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r

\r
\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r


\r
\r
\r


\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r


\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r

\r
\r
\r


\r
\r
\r
\r


\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r

\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r


\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
 \n\




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r


\r
\r
\r


\r
\r
\r
\r
\r
\r
\r


\r
\r
\r
\r


\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r


\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
 \r
\r



\r

\r
\r
\r


\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r


\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r


\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r


\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r


\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r
\r




\r




\r
\r
\r


\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r


\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r


\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r\r
 \n\

\r
\r
\r
\r
\r\r
\r\r



\r
\r
\r


\r
\r
\r
\r
\r\r
 \n\

\r
\r
\r


\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r


\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r
\r
\r
\r
\r
\r
\r
\r




\r
\r
\r


\r
\r
\r


\r
\r
\r
\r
\r
\r
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
                    "strict": None,
                }
            ],
        }
    }
)
async_snapshot = snapshot(
    {
        "response": {
            "provider_id": "azure",
            "model_id": "azure/openai/gpt-5-mini",
            "provider_model_name": "gpt-5-mini",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 286,
                "output_tokens": 3925,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 640,
                "raw": "CompletionUsage(completion_tokens=3925, prompt_tokens=286, total_tokens=4211, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=640, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0))",
                "total_tokens": 4211,
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
                            id="call_ZN7xRUl4wZLyraUplpRyUvxJ",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider_id="azure",
                    model_id="azure/openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini",
                    raw_message={
                        "role": "assistant",
                        "annotations": [],
                        "tool_calls": [
                            {
                                "id": "call_ZN7xRUl4wZLyraUplpRyUvxJ",
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
                            id="call_ZN7xRUl4wZLyraUplpRyUvxJ",
                            name="get_book_info",
                            result="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text='{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006}'
                        )
                    ],
                    provider_id="azure",
                    model_id="azure/openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini",
                    raw_message={
                        "content": '{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006}',
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
                    "strict": None,
                }
            ],
        }
    }
)
stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "azure",
            "model_id": "azure/openai/gpt-5-mini",
            "provider_model_name": "gpt-5-mini",
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
                            id="call_7YPd5mDdKnB7LsEwwgtq6L1C",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider_id="azure",
                    model_id="azure/openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini",
                    raw_message=None,
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_7YPd5mDdKnB7LsEwwgtq6L1C",
                            name="get_book_info",
                            result="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
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
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\












  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\






  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\






  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\






  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\




  \n\




  \n\




  \n\




  \n\




  \n\




  \n\
  \n\




  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\




  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\

  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\
  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\




  \n\




  \n\
  \n\




  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
    \n\
  \n\
  \n\
  \n\
    \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\






  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\
  \n\




  \n\




  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\

  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\

  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\




  \n\
  \n\




  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\




  \n\
  \n\




  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\






  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\






  \n\
  \n\





  \n\
  \n\




  \n\
  \n\






  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\






  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\






  \n\
  \n\




  \n\
  \n\



  \n\
  \n\




  \n\
  \n\




  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\






  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\






  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\






  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\






  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\






  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\










  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\

  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\

  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\

  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\






  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\






  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
 \n\





 \n\
 \n\





 \n\
 \n\





 \n\
 \n\





 \n\
 \n\





 \n\
 \n\





 \n\
 \n\





 \n\
 \n\





 \n\
 \n\





 \n\
 \n\





 \n\
 \n\





 \n\
 \n\





 \n\
 \n\





 \n\
 \n\





 \n\
 \n\





 \n\
 \n\





 \n\
 \n\





 \n\
 \n\





 \n\
 \n\
 \n\
 \n\






 \n\
 \n\






 \n\
 \n\








 \n\
 \n\








 \n\
 \n\








 \n\
 \n\








 \n\
 \n\








 \n\
 \n\








 \n\





 \n\
 \n\
 \n\








 \n\
 \n\











 \n\
 \n\






 \n\
 \n\






 \n\
 \n\







 \n\
 \n\
 \n\







 \n\
 \n\








 \n\
 \n\







 \n\
 \n\







 \n\
 \n\






 \n\
 \n\









 \n\
 \n\









 \n\
 \n\








 \n\












 \n\













 \n\
 \n\












 \n\
 \n\








 \n\
 \n\











 \n\
 \n\








 \n\
 \n\









 \n\
 \n\







 \n\
 \n\








 \n\
 \n\








 \n\
 \n\












 \n\












 \n\











 \n\
 \n\




















 \n\
 \n\
 \n\














 \n\
 \n\















 \n\
 \n\

 \n\








 \n\
 \n\


  \n\
   \n\
   \n\
   \n\
   \n\
   \n\
   \n\
   \n\
   \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\




  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





 \n\
 \n\












 \n\
 \n\















 \n\
 \n\












 \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\

  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\






  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\

  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\

  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\




   \n\
  \n\
   \n\

   \n\
   \n\
   \n\
   \n\
   \n\
   \n\
   \n\
   \n\
   \n\
   \n\
   \n\
   \n\
   \n\
   \n\
   \n\
   \n\
   \n\
   \n\
   \n\
   \n\
   \n\
   \n\

    \n\




  \n\
  \n\




  \n\
  \n\




  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\




  \n\
  \n\





  \n\
  \n\




  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\






  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\






  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\






  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\
  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\

  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\














  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\









  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\

  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\






  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\






  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





 \n\
 \n\







  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\

  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\

  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\














  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\
  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\






  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\

  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\






  \n\
 \n\







  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\


  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\










  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\

  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\






  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\






  \n\
   \n\

  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\

  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\

  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\











  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\


  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\




  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\

  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\






  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\

  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\

  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\













  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





 \n\
 \n\














 \n\
 \n\

  \n\
  \n\




  \n\
  \n\




 \n\
 \n\










 \n\
 \n\
















 \n\
 \n\















 \n\
 \n\












 \n\
 \n\








 \n\
 \n\












 \n\
 \n\










 \n\
 \n\












 \n\










 \n\
 \n\





 \n\
 \n\





 \n\
 \n\

  \n\
  \n\




  \n\
  \n\










 \n\
 \n\








 \n\







 \n\












 \n\












 \n\




























 \n\







 \n\






 \n\












 \n\












 \n\












 \n\












  \n\
  \n\




  \n\
  \n\




  \n\




  \n\
  \n\




  \n\




  \n\




  \n\




  \n\




  \n\




  \n\




  \n\




  \n\




  \n\




  \n\




  \n\




  \n\




  \n\




  \n\




  \n\




  \n\




  \n\




  \n\




  \n\




  \n\




  \n\




  \n\




  \n\




  \n\




  \n\




  \n\




  \n\




  \n\




  \n\





  \n\




  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\
  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
 \n\





 \n\





 \n\


  \n\
 \n\








 \n\
 \n\












  \n\




 \n\
 \n\















 \n\
 \n\

  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\










 \n\
 \n\






 \n\
 \n\












 \n\
 \n\








 \n\
 \n\







 \n\
 \n\








 \n\
 \n\






 \n\
 \n\






 \n\
  \n\




  \n\
  \n\




  \n\




  \n\




  \n\
  \n\




  \n\




  \n\
  \n\




  \n\
 \n\






 \n\






 \n\













 \n\








 \n\
 \n\
















 \n\
 \n\







 \n\






  \n\
  \n\




  \n\




  \n\
  \n\




 \n\












 \n\












  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
 \n\







 \n\
 \n\















 \n\
 \n\












 \n\












 \n\












 \n\












 \n\


















 \n\
 \n\






 \n\


















 \n\
 \n\














 \n\
 \n\
 \n\



 \n\



 \n\
 \n\












 \n\
 \n\












 \n\
 \n\










 \n\
 \n\
 \n\
















  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\


 \n\
 \n\







 \n\
 \n\












 \n\












 \n\








 \n\












 \n\


  \n\
  \n\




  \n\




  \n\
  \n\

  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\












  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\

  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\

  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\

  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\

  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\

  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\
  \n\





  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
 \n\
















 \n\
 \n\









  \n\
  \n\




 \n\












  \n\
  \n\




  \n\
  \n\




  \n\
  \n\

  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
 \n\
 \n\











  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\

  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\











  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\




  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\






  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\





  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
  \n\




  \n\
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
                    provider_id="azure",
                    model_id="azure/openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini",
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
                    "strict": None,
                }
            ],
            "usage": {
                "input_tokens": 286,
                "output_tokens": 18549,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 704,
                "raw": "None",
                "total_tokens": 18835,
            },
            "n_chunks": 17833,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "azure",
            "model_id": "azure/openai/gpt-5-mini",
            "provider_model_name": "gpt-5-mini",
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
                            id="call_DEqEv4RZYRowKdxkG9ZIhaNj",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider_id="azure",
                    model_id="azure/openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini",
                    raw_message=None,
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_DEqEv4RZYRowKdxkG9ZIhaNj",
                            name="get_book_info",
                            result="Title: Mistborn: The Final Empire, Author: Brandon Sanderson, Pages: 544, Published: 2006-07-25",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text='{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson — Highly recommended (9/10). Dark, inventive epic fantasy with a unique magic system (Allomancy), memorable characters (Vin, Kelsier), and a gripping heist/insurgency plot; first published 2006-07-25.","pages":544,"publication_year":2006}'
                        )
                    ],
                    provider_id="azure",
                    model_id="azure/openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini",
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
                    "strict": None,
                }
            ],
            "usage": {
                "input_tokens": 286,
                "output_tokens": 1565,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 1472,
                "raw": "None",
                "total_tokens": 1851,
            },
            "n_chunks": 81,
        }
    }
)
