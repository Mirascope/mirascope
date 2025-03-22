# Copyright The OpenTelemetry Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Modifications copyright (C) 2024 Mirascope

from collections.abc import Collection
from typing import Any

from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.instrumentation.utils import unwrap
from opentelemetry.semconv.schemas import Schemas
from opentelemetry.trace import get_tracer
from wrapt import wrap_function_wrapper

from .patch import (
    chat_completions_create,
    chat_completions_create_async,
    chat_completions_parse,
    chat_completions_parse_async,
)


class OpenAIInstrumentor(BaseInstrumentor):
    def instrumentation_dependencies(self) -> Collection[str]:
        return ("openai>=1.6.0,<2",)

    def _instrument(self, **kwargs: Any) -> None:
        """Enable OpenAI instrumentation."""
        tracer_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(
            __name__,
            "0.1.0",  # Lilypad version
            tracer_provider,
            schema_url=Schemas.V1_28_0.value,
        )
        wrap_function_wrapper(
            module="openai.resources.chat.completions",
            name="Completions.create",
            wrapper=chat_completions_create(tracer),
        )
        wrap_function_wrapper(
            module="openai.resources.chat.completions",
            name="AsyncCompletions.create",
            wrapper=chat_completions_create_async(tracer),
        )

        wrap_function_wrapper(
            module="openai.resources.beta.chat.completions",
            name="Completions.parse",
            wrapper=chat_completions_parse(tracer),
        )
        wrap_function_wrapper(
            module="openai.resources.beta.chat.completions",
            name="AsyncCompletions.parse",
            wrapper=chat_completions_parse_async(tracer),
        )

    def _uninstrument(self, **kwargs: Any) -> None:
        import openai

        unwrap(openai.resources.chat.completions.Completions, "create")  # pyright: ignore[reportAttributeAccessIssue]
        unwrap(openai.resources.chat.completions.AsyncCompletions, "create")  # pyright: ignore[reportAttributeAccessIssue]
        unwrap(openai.resources.beta.chat.completions.Completions, "parse")  # pyright: ignore[reportAttributeAccessIssue]
        unwrap(openai.resources.beta.chat.completions.AsyncCompletions, "parse")  # pyright: ignore[reportAttributeAccessIssue]
