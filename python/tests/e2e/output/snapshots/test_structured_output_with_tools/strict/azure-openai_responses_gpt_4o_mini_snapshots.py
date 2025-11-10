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
            "provider": "azure-openai:responses",
            "model_id": "gpt-4o-mini",
            "params": {},
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
                            id="call_uz2in4OrM8UzltFrUiUWnwcF",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "arguments": '{"isbn":"0-7653-1178-X"}',
                            "call_id": "call_uz2in4OrM8UzltFrUiUWnwcF",
                            "name": "get_book_info",
                            "type": "function_call",
                            "id": "fc_0bacd9931601515b00690c220b73988197a009bc5a4c030800",
                            "status": "completed",
                        }
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_uz2in4OrM8UzltFrUiUWnwcF",
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
"""
                        )
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "id": "msg_03758189f31b832200690c220da4908190af5e51ec22297e08",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
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
""",
                                    "type": "output_text",
                                    "logprobs": [],
                                }
                            ],
                            "role": "assistant",
                            "status": "completed",
                            "type": "message",
                        }
                    ],
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
            "provider": "azure-openai:responses",
            "model_id": "gpt-4o-mini",
            "params": {},
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
                            id="call_ATSbUOtS8C0sTsazw1w9FMbX",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "arguments": '{"isbn":"0-7653-1178-X"}',
                            "call_id": "call_ATSbUOtS8C0sTsazw1w9FMbX",
                            "name": "get_book_info",
                            "type": "function_call",
                            "id": "fc_074bf5ac734f89c100690c222680dc81958c3fee87c771becf",
                            "status": "completed",
                        }
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_ATSbUOtS8C0sTsazw1w9FMbX",
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

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

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
                        ),
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

 \n\

   \n\
   \n\
  \n\

   \n\
 \n\

 \n\

   \n\

 \n\
 \n\

   \n\

 \n\

   \n\

   \n\

 \n\

 \n\

 \n\
 \n\
 \n\

 \n\
 \n\

 \
"""
                        ),
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "id": "msg_09e43354b00e32c700690c2227c59c8194babf1a5d43470109",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
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

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

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
                                    "type": "output_text",
                                    "logprobs": [],
                                }
                            ],
                            "role": "assistant",
                            "status": "completed",
                            "type": "message",
                        },
                        {
                            "id": "msg_09e43354b00e32c700690c223d61c08194a07329891818afcc",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
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

 \n\

   \n\
   \n\
  \n\

   \n\
 \n\

 \n\

   \n\

 \n\
 \n\

   \n\

 \n\

   \n\

   \n\

 \n\

 \n\

 \n\
 \n\
 \n\

 \n\
 \n\

 \
""",
                                    "type": "output_text",
                                    "logprobs": [],
                                }
                            ],
                            "role": "assistant",
                            "status": "completed",
                            "type": "message",
                        },
                    ],
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
            "provider": "azure-openai:responses",
            "model_id": "gpt-4o-mini",
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
                            id="call_tUuxEavuwrX7n3y9MNtav0T1",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "arguments": '{"isbn":"0-7653-1178-X"}',
                            "call_id": "call_tUuxEavuwrX7n3y9MNtav0T1",
                            "name": "get_book_info",
                            "type": "function_call",
                            "id": "fc_04290325b31add8800690c225bb1248193a298046b28c1cd54",
                            "status": "completed",
                        }
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_tUuxEavuwrX7n3y9MNtav0T1",
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

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\


 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

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
                        ),
                        Text(
                            text='{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006}'
                        ),
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "id": "msg_0d6d686eb6310d5800690c225ced14819090023c6bf3c238ef",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
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

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\


 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

 \n\

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
                                    "type": "output_text",
                                    "logprobs": [],
                                }
                            ],
                            "role": "assistant",
                            "status": "completed",
                            "type": "message",
                        },
                        {
                            "id": "msg_0d6d686eb6310d5800690c22bba62c8190ac69017620dc0858",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": '{"title":"Mistborn: The Final Empire","author":"Brandon Sanderson","pages":544,"publication_year":2006}',
                                    "type": "output_text",
                                    "logprobs": [],
                                }
                            ],
                            "role": "assistant",
                            "status": "completed",
                            "type": "message",
                        },
                    ],
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
            "n_chunks": 660,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider": "azure-openai:responses",
            "model_id": "gpt-4o-mini",
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
                            id="call_jVDZQAbwOD3YWo6VVlLCDUk4",
                            name="get_book_info",
                            args='{"isbn":"0-7653-1178-X"}',
                        )
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "arguments": '{"isbn":"0-7653-1178-X"}',
                            "call_id": "call_jVDZQAbwOD3YWo6VVlLCDUk4",
                            "name": "get_book_info",
                            "type": "function_call",
                            "id": "fc_01b2a302c4f3f36500690c22d03388819595a43007be9b3e26",
                            "status": "completed",
                        }
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_jVDZQAbwOD3YWo6VVlLCDUk4",
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
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\


  \n\
  \n\

  \n\
  \n\

  \n\
  \n\


  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\


  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\


  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\


  \n\
  \n\

  \n\
  \n\


  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\


  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\



  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\



  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\


  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\


  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\



  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\


  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\



  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
    \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\



  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\



  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\


  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\



  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\



  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\



  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\



  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
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
                        ),
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

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\



  \n\
  \n\

  \n\
  \n\



  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
    \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
   \n\

 \n\
                            \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\





  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\


   \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\



  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

   \n\
  \n\
  \n\
    \n\

  \n\

 \n\
   \n\

  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

   \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\



  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

   \n\
  \n\

   \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\



  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

   \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

    \n\
  \n\


   \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

   \n\
  \n\

    \n\

  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\
  \n\

  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\



  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

   \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\



  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

   \n\
  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\



  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

   \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

     \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

    \n\
  \n\
    \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\


   \n\
  \n\

    \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

  \n\
  \n\

   \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\



  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

    \n\
    \n\

  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

   \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

 \n\
   \n\

  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\
  \n\

  \n\
  \n\

   \n\
  \n\

  \n\
  \n\



  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\
 \n\

  \n\
   \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

     \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

      \n\
  \n\

  \n\
  \n\

  \n\
  \n\

   \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\



  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

    \n\
  \n\

   \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

   \
"""
                        ),
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "id": "msg_0ba977faf234a04e00690c22d11a408190ad03e886ee4fa6dd",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
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
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\


  \n\
  \n\

  \n\
  \n\

  \n\
  \n\


  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\


  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\


  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\


  \n\
  \n\

  \n\
  \n\


  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\


  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\



  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\



  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\


  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\


  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\



  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\


  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\



  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
    \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\



  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\



  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\


  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\



  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\



  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\



  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\



  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
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
                                    "type": "output_text",
                                    "logprobs": [],
                                }
                            ],
                            "role": "assistant",
                            "status": "completed",
                            "type": "message",
                        },
                        {
                            "id": "msg_0ba977faf234a04e00690c236391ec819084661898a191fc11",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
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

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\



  \n\
  \n\

  \n\
  \n\



  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
    \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
   \n\

 \n\
                            \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\





  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\


   \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\



  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

   \n\
  \n\
  \n\
    \n\

  \n\

 \n\
   \n\

  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

   \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\



  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

   \n\
  \n\

   \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\



  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

   \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

    \n\
  \n\


   \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

   \n\
  \n\

    \n\

  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\
  \n\

  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\



  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

   \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\



  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

   \n\
  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\



  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

   \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

     \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

    \n\
  \n\
    \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\


   \n\
  \n\

    \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

  \n\
  \n\

   \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\



  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

    \n\
    \n\

  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

   \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

 \n\
   \n\

  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\
  \n\

  \n\
  \n\

   \n\
  \n\

  \n\
  \n\



  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\
 \n\

  \n\
   \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

     \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

      \n\
  \n\

  \n\
  \n\

  \n\
  \n\

   \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\



  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
   \n\

    \n\
  \n\

   \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

    \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

  \n\
  \n\

   \
""",
                                    "type": "output_text",
                                    "logprobs": [],
                                }
                            ],
                            "role": "assistant",
                            "status": "completed",
                            "type": "message",
                        },
                    ],
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
            "n_chunks": 2918,
        }
    }
)
