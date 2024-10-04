# OpenTelemetry

Mirascope provides out-of-the-box integration with [OpenTelemetry](https://opentelemetry.io/docs/what-is-opentelemetry/).

You can install the necessary packages directly or using the `opentelemetry` extras flag:

```python
pip install "mirascope[opentelemetry]"
```

You can then use the `with_otel` decorator to automatically log calls:

!!! mira ""

    {% for method, method_title in zip(prompt_writing_methods, prompt_writing_method_titles) %}
    === "{{ method_title }}"

        {% for provider in supported_llm_providers %}
        === "{{ provider }}"

            ```python hl_lines="2 4 7"
            --8<-- "examples/integrations/otel/{{ provider | provider_dir }}/{{ method }}.py"
            ```
        {% endfor %}

    {% endfor %}

??? info "Example output span"

    This will give you:

    * A span called `recommend_book` that captures items like the prompt template, templating properties and fields, and input/output attributes
    * Details of the response, including the number of tokens used

    ```python
    {
        "name": "recommend_book",
        "context": {
            "trace_id": "0x9397ede2f689a5b7767f0063d7b81959",
            "span_id": "0xa22a446b2076ffe4",
            "trace_state": "[]"
        },
        "kind": "SpanKind.INTERNAL",
        "parent_id": null,
        "start_time": "2024-10-04T05:16:47.340006Z",
        "end_time": "2024-10-04T05:16:47.341937Z",
        "status": {
            "status_code": "UNSET"
        },
        "attributes": {
            "gen_ai.system": "",
            "gen_ai.request.model": "claude-3-5-sonnet-20240620",
            "gen_ai.request.max_tokens": 0,
            "gen_ai.request.temperature": 0,
            "gen_ai.request.top_p": 0,
            "gen_ai.response.model": "claude-3-5-sonnet-20240620",
            "gen_ai.response.id": "msg_01X8sppiaZeErMjh8oCNz4ZA",
            "gen_ai.response.finish_reasons": [
                "end_turn"
            ],
            "gen_ai.usage.completion_tokens": 268,
            "gen_ai.usage.prompt_tokens": 12,
            "async": false
        },
        "events": [
            {
                "name": "gen_ai.content.prompt",
                "timestamp": "2024-10-04T05:16:47.341924Z",
                "attributes": {
                    "gen_ai.prompt": "{\"content\": \"Recommend a fantasy book\", \"role\": \"user\"}"
                }
            },
            {
                "name": "gen_ai.content.completion",
                "timestamp": "2024-10-04T05:16:47.341931Z",
                "attributes": {
                    "gen_ai.completion": "{\"content\": [{\"text\": \"There are many great fantasy books to choose from, but here's a popular recommendation:\\n\\n\\\"The Name of the Wind\\\" by Patrick Rothfuss\\n\\nThis is the first book in \\\"The Kingkiller Chronicle\\\" series. It's a beautifully written, engaging story that follows the life of Kvothe, a legendary wizard, warrior, and musician. The book is known for its rich world-building, complex magic system, and compelling characters.\\n\\nOther excellent fantasy recommendations include:\\n\\n1. \\\"The Lord of the Rings\\\" by J.R.R. Tolkien\\n2. \\\"A Game of Thrones\\\" by George R.R. Martin\\n3. \\\"The Way of Kings\\\" by Brandon Sanderson\\n4. \\\"The Lies of Locke Lamora\\\" by Scott Lynch\\n5. \\\"The Night Circus\\\" by Erin Morgenstern\\n6. \\\"Mistborn: The Final Empire\\\" by Brandon Sanderson\\n7. \\\"The Wizard of Earthsea\\\" by Ursula K. Le Guin\\n\\nThese books cater to different tastes within the fantasy genre, so you might want to read a brief synopsis of each to see which one appeals to you most.\", \"type\": \"text\"}], \"role\": \"assistant\"}"
                }
            }
        ],
        "links": [],
        "resource": {
            "attributes": {
                "telemetry.sdk.language": "python",
                "telemetry.sdk.name": "opentelemetry",
                "telemetry.sdk.version": "1.22.0",
                "service.name": "unknown_service"
            },
            "schema_url": ""
        }
    }
    ```

??? note "Handling streams"

    When logging streams, the span will not be logged until the stream has been exhausted. This is a function of how streaming works.

    You will also need to set certain `call_params` for usage to be tracked for certain providers (such as OpenAI).

## Sending to an observability tool

You'll likely want to send the spans to an actual observability tool so that you can monitor your traces. There are many observability tools out there, but the majority of them can collect OpenTelemetry data. You can pass in processors as an argument of configure() so that you can send the spans to your choice of observability tool:

!!! mira ""

    ```python
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.trace.export import (
        BatchSpanProcessor,
    )
    from mirascope.integrations.otel import configure

    OBSERVABILITY_TOOL_ENDPOINT = "..."
    configure(
        processors=[
            BatchSpanProcessor(
                OTLPSpanExporter(
                    endpoint=f"https://{OBSERVABILITY_TOOL_ENDPOINT}/v1/traces",
                )
            )
        ]
    )
    ```

You should refer to your observability tool's documentation to find the endpoint. If there is an observability backend that you would like for us to integrate out-of-the-box, create a [GitHub Issue](https://github.com/Mirascope/mirascope/issues) or let us know in our [Slack community](https://join.slack.com/t/mirascope-community/shared_invite/zt-2ilqhvmki-FB6LWluInUCkkjYD3oSjNA).
