from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    FinishReason,
    Text,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "response": (
            {
                "provider": "anthropic",
                "model_id": "claude-sonnet-4-0",
                "params": {"temperature": 0.7, "max_tokens": 120, "top_p": 0.3},
                "finish_reason": FinishReason.MAX_TOKENS,
                "messages": [
                    UserMessage(content=[Text(text="List all U.S. states")]),
                    AssistantMessage(
                        content=[
                            Text(
                                text="""\
Here are all 50 U.S. states in alphabetical order:

1. Alabama
2. Alaska
3. Arizona
4. Arkansas
5. California
6. Colorado
7. Connecticut
8. Delaware
9. Florida
10. Georgia
11. Hawaii
12. Idaho
13. Illinois
14. Indiana
15. Iowa
16. Kansas
17. Kentucky
18. Louisiana
19. Maine
20. Maryland
21. Massachusetts
22. Michigan
23. Minnesota
24. Mississippi
25. Missouri
26. Montana\
"""
                            )
                        ]
                    ),
                ],
                "format": None,
                "tools": [],
            },
        ),
        "logging": [],
    }
)
async_snapshot = snapshot(
    {
        "response": (
            {
                "provider": "anthropic",
                "model_id": "claude-sonnet-4-0",
                "params": {"temperature": 0.7, "max_tokens": 120, "top_p": 0.3},
                "finish_reason": FinishReason.MAX_TOKENS,
                "messages": [
                    UserMessage(content=[Text(text="List all U.S. states")]),
                    AssistantMessage(
                        content=[
                            Text(
                                text="""\
Here are all 50 U.S. states in alphabetical order:

1. Alabama
2. Alaska
3. Arizona
4. Arkansas
5. California
6. Colorado
7. Connecticut
8. Delaware
9. Florida
10. Georgia
11. Hawaii
12. Idaho
13. Illinois
14. Indiana
15. Iowa
16. Kansas
17. Kentucky
18. Louisiana
19. Maine
20. Maryland
21. Massachusetts
22. Michigan
23. Minnesota
24. Mississippi
25. Missouri
26. Montana\
"""
                            )
                        ]
                    ),
                ],
                "format": None,
                "tools": [],
            },
        ),
        "logging": [],
    }
)
stream_snapshot = snapshot(
    {
        "response": (
            {
                "provider": "anthropic",
                "model_id": "claude-sonnet-4-0",
                "finish_reason": FinishReason.MAX_TOKENS,
                "messages": [
                    UserMessage(content=[Text(text="List all U.S. states")]),
                    AssistantMessage(
                        content=[
                            Text(
                                text="""\
Here are all 50 U.S. states in alphabetical order:

1. Alabama
2. Alaska
3. Arizona
4. Arkansas
5. California
6. Colorado
7. Connecticut
8. Delaware
9. Florida
10. Georgia
11. Hawaii
12. Idaho
13. Illinois
14. Indiana
15. Iowa
16. Kansas
17. Kentucky
18. Louisiana
19. Maine
20. Maryland
21. Massachusetts
22. Michigan
23. Minnesota
24. Mississippi
25. Missouri
26. Montana\
"""
                            )
                        ]
                    ),
                ],
                "format": None,
                "tools": [],
                "n_chunks": 11,
            },
        ),
        "logging": [],
    }
)
async_stream_snapshot = snapshot(
    {
        "response": (
            {
                "provider": "anthropic",
                "model_id": "claude-sonnet-4-0",
                "finish_reason": FinishReason.MAX_TOKENS,
                "messages": [
                    UserMessage(content=[Text(text="List all U.S. states")]),
                    AssistantMessage(
                        content=[
                            Text(
                                text="""\
Here are all 50 U.S. states in alphabetical order:

1. Alabama
2. Alaska
3. Arizona
4. Arkansas
5. California
6. Colorado
7. Connecticut
8. Delaware
9. Florida
10. Georgia
11. Hawaii
12. Idaho
13. Illinois
14. Indiana
15. Iowa
16. Kansas
17. Kentucky
18. Louisiana
19. Maine
20. Maryland
21. Massachusetts
22. Michigan
23. Minnesota
24. Mississippi
25. Missouri
26. Montana\
"""
                            )
                        ]
                    ),
                ],
                "format": None,
                "tools": [],
                "n_chunks": 11,
            },
        ),
        "logging": [],
    }
)
