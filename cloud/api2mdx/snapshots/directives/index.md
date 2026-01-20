# llm

<Directive path="mirascope.llm.exceptions.APIError" />

<Directive path="mirascope.llm.responses.root_response.AnyResponse" />

<Directive path="mirascope.llm.tools.tool_schema.AnyToolFn" />

<Directive path="mirascope.llm.tools.tool_schema.AnyToolSchema" />

<Directive path="mirascope.llm.messages.message.AssistantContent" />

<Directive path="mirascope.llm.content.AssistantContentChunk" />

<Directive path="mirascope.llm.content.AssistantContentPart" />

<Directive path="mirascope.llm.messages.message.AssistantMessage" />

<Directive path="mirascope.llm.calls.calls.AsyncCall" />

<Directive path="mirascope.llm.responses.base_stream_response.AsyncChunkIterator" />

<Directive path="mirascope.llm.calls.calls.AsyncContextCall" />

<Directive path="mirascope.llm.prompts.prompts.AsyncContextPrompt" />

<Directive path="mirascope.llm.responses.response.AsyncContextResponse" />

<Directive path="mirascope.llm.responses.stream_response.AsyncContextStreamResponse" />

<Directive path="mirascope.llm.tools.tools.AsyncContextTool" />

<Directive path="mirascope.llm.tools.toolkit.AsyncContextToolkit" />

<Directive path="mirascope.llm.prompts.prompts.AsyncPrompt" />

<Directive path="mirascope.llm.responses.response.AsyncResponse" />

<Directive path="mirascope.llm.responses.streams.AsyncStream" />

<Directive path="mirascope.llm.responses.stream_response.AsyncStreamResponse" />

<Directive path="mirascope.llm.responses.streams.AsyncTextStream" />

<Directive path="mirascope.llm.responses.streams.AsyncThoughtStream" />

<Directive path="mirascope.llm.tools.tools.AsyncTool" />

<Directive path="mirascope.llm.responses.streams.AsyncToolCallStream" />

<Directive path="mirascope.llm.tools.toolkit.AsyncToolkit" />

<Directive path="mirascope.llm.content.audio.Audio" />

<Directive path="mirascope.llm.exceptions.AuthenticationError" />

<Directive path="mirascope.llm.exceptions.BadRequestError" />

<Directive path="mirascope.llm.content.audio.Base64AudioSource" />

<Directive path="mirascope.llm.content.image.Base64ImageSource" />

<Directive path="mirascope.llm.tools.toolkit.BaseToolkit" />

<Directive path="mirascope.llm.calls.calls.Call" />

<Directive path="mirascope.llm.calls.decorator.CallDecorator" />

<Directive path="mirascope.llm.responses.base_stream_response.ChunkIterator" />

<Directive path="mirascope.llm.exceptions.ConnectionError" />

<ApiObject
  path="mirascope.llm.context.context.Context"
  symbolName="Context"
  slug="context"
  canonicalPath="index"
/>

<Directive path="mirascope.llm.calls.calls.ContextCall" />

<Directive path="mirascope.llm.prompts.prompts.ContextPrompt" />

<Directive path="mirascope.llm.responses.response.ContextResponse" />

<Directive path="mirascope.llm.responses.stream_response.ContextStreamResponse" />

<Directive path="mirascope.llm.tools.tools.ContextTool" />

<Directive path="mirascope.llm.tools.toolkit.ContextToolkit" />

<ApiObject
  path="mirascope.llm.context.context.DepsT"
  symbolName="DepsT"
  slug="deps-t"
  canonicalPath="index"
/>

<Directive path="mirascope.llm.content.document.Document" />

<Directive path="mirascope.llm.exceptions.FeatureNotSupportedError" />

<Directive path="mirascope.llm.responses.finish_reason.FinishReason" />

<Directive path="mirascope.llm.formatting.format.Format" />

<Directive path="mirascope.llm.formatting.types.FormattableT" />

<Directive path="mirascope.llm.formatting.types.FormattingMode" />

<Directive path="mirascope.llm.exceptions.FormattingModeNotSupportedError" />

<Directive path="mirascope.llm.content.image.Image" />

<Directive path="mirascope.llm.types.jsonable.Jsonable" />

<Directive path="mirascope.llm.messages.message.Message" />

<Directive path="mirascope.llm.exceptions.MirascopeLLMError" />

<Directive path="mirascope.llm.models.models.Model" />

<Directive path="mirascope.llm.providers.model_id.ModelId" />

<Directive path="mirascope.llm.exceptions.NoRegisteredProviderError" />

<Directive path="mirascope.llm.exceptions.NotFoundError" />

<Directive path="mirascope.llm.formatting.output_parser.OutputParser" />

<Directive path="mirascope.llm.models.params.Params" />

<Directive path="mirascope.llm.formatting.partial.Partial" />

<Directive path="mirascope.llm.exceptions.PermissionError" />

<Directive path="mirascope.llm.prompts.prompts.Prompt" />

<Directive path="mirascope.llm.prompts.decorator.PromptDecorator" />

<Directive path="mirascope.llm.providers.base.base_provider.Provider" />

<Directive path="mirascope.llm.providers.provider_id.ProviderId" />

<Directive path="mirascope.llm.exceptions.RateLimitError" />

<Directive path="mirascope.llm.responses.base_stream_response.RawMessageChunk" />

<Directive path="mirascope.llm.responses.response.Response" />

<Directive path="mirascope.llm.responses.root_response.RootResponse" />

<Directive path="mirascope.llm.exceptions.ServerError" />

<Directive path="mirascope.llm.responses.streams.Stream" />

<Directive path="mirascope.llm.responses.stream_response.StreamResponse" />

<Directive path="mirascope.llm.responses.base_stream_response.StreamResponseChunk" />

<Directive path="mirascope.llm.messages.message.SystemContent" />

<Directive path="mirascope.llm.messages.message.SystemMessage" />

<Directive path="mirascope.llm.content.text.Text" />

<Directive path="mirascope.llm.content.text.TextChunk" />

<Directive path="mirascope.llm.content.text.TextEndChunk" />

<Directive path="mirascope.llm.content.text.TextStartChunk" />

<Directive path="mirascope.llm.responses.streams.TextStream" />

<Directive path="mirascope.llm.models.thinking_config.ThinkingConfig" />

<Directive path="mirascope.llm.models.thinking_config.ThinkingLevel" />

<Directive path="mirascope.llm.content.thought.Thought" />

<Directive path="mirascope.llm.content.thought.ThoughtChunk" />

<Directive path="mirascope.llm.content.thought.ThoughtEndChunk" />

<Directive path="mirascope.llm.content.thought.ThoughtStartChunk" />

<Directive path="mirascope.llm.responses.streams.ThoughtStream" />

<Directive path="mirascope.llm.exceptions.TimeoutError" />

<Directive path="mirascope.llm.tools.tools.Tool" />

<Directive path="mirascope.llm.content.tool_call.ToolCall" />

<Directive path="mirascope.llm.content.tool_call.ToolCallChunk" />

<Directive path="mirascope.llm.content.tool_call.ToolCallEndChunk" />

<Directive path="mirascope.llm.content.tool_call.ToolCallStartChunk" />

<Directive path="mirascope.llm.responses.streams.ToolCallStream" />

<Directive path="mirascope.llm.exceptions.ToolNotFoundError" />

<Directive path="mirascope.llm.content.tool_output.ToolOutput" />

<Directive path="mirascope.llm.tools.tool_schema.ToolSchema" />

<Directive path="mirascope.llm.tools.toolkit.Toolkit" />

<Directive path="mirascope.llm.tools.toolkit.ToolkitT" />

<Directive path="mirascope.llm.content.image.URLImageSource" />

<Directive path="mirascope.llm.responses.usage.Usage" />

<Directive path="mirascope.llm.responses.usage.UsageDeltaChunk" />

<Directive path="mirascope.llm.messages.message.UserContent" />

<Directive path="mirascope.llm.content.UserContentPart" />

<Directive path="mirascope.llm.messages.message.UserMessage" />

<Directive path="mirascope.llm.calls.decorator.call" />

<ApiObject
  path="mirascope.llm.calls"
  symbolName="calls"
  slug="calls"
  canonicalPath="index"
/>

<ApiObject
  path="mirascope.llm.content"
  symbolName="content"
  slug="content"
  canonicalPath="index"
/>

<ApiObject
  path="mirascope.llm.exceptions"
  symbolName="exceptions"
  slug="exceptions"
  canonicalPath="index"
/>

<Directive path="mirascope.llm.formatting.format.format" />

<ApiObject
  path="mirascope.llm.formatting"
  symbolName="formatting"
  slug="formatting"
  canonicalPath="index"
/>

<ApiObject
  path="mirascope.llm.mcp"
  symbolName="mcp"
  slug="mcp"
  canonicalPath="index"
/>

<ApiObject
  path="mirascope.llm.messages"
  symbolName="messages"
  slug="messages"
  canonicalPath="index"
/>

<Directive path="mirascope.llm.models.models.model" />

<Directive path="mirascope.llm.models.models.model_from_context" />

<ApiObject
  path="mirascope.llm.models"
  symbolName="models"
  slug="models"
  canonicalPath="index"
/>

<Directive path="mirascope.llm.formatting.output_parser.output_parser" />

<Directive path="mirascope.llm.prompts.decorator.prompt" />

<ApiObject
  path="mirascope.llm.prompts"
  symbolName="prompts"
  slug="prompts"
  canonicalPath="index"
/>

<ApiObject
  path="mirascope.llm.providers"
  symbolName="providers"
  slug="providers"
  canonicalPath="index"
/>

<Directive path="mirascope.llm.providers.provider_registry.register_provider" />

<Directive path="mirascope.llm.providers.provider_registry.reset_provider_registry" />

<ApiObject
  path="mirascope.llm.responses"
  symbolName="responses"
  slug="responses"
  canonicalPath="index"
/>

<Directive path="mirascope.llm.tools.decorator.tool" />

<ApiObject
  path="mirascope.llm.tools"
  symbolName="tools"
  slug="tools"
  canonicalPath="index"
/>

<ApiObject
  path="mirascope.llm.types"
  symbolName="types"
  slug="types"
  canonicalPath="index"
/>

<Directive path="mirascope.llm.models.models.use_model" />