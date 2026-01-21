from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "exception": {
            "type": "invalid_request_error",
            "args": "(\"Error code: 400 - {'error': {'message': 'Error while downloading https://en.wikipedia.org/static/images/icons/wikipedia.png.', 'type': 'invalid_request_error', 'param': 'url', 'code': 'invalid_value'}}\",)",
            "body": "{'message': 'Error while downloading https://en.wikipedia.org/static/images/icons/wikipedia.png.', 'type': 'invalid_request_error', 'param': 'url', 'code': 'invalid_value'}",
            "code": "invalid_value",
            "message": "Error code: 400 - {'error': {'message': 'Error while downloading https://en.wikipedia.org/static/images/icons/wikipedia.png.', 'type': 'invalid_request_error', 'param': 'url', 'code': 'invalid_value'}}",
            "param": "url",
            "request": "<Request('POST', 'https://api.openai.com/v1/responses')>",
            "request_id": "req_9a7b50fe4a4d44e98f4fc4477eff2dad",
            "response": "<Response [400 Bad Request]>",
            "status_code": "400",
        }
    }
)
