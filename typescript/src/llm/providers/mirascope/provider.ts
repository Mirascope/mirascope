import type { Context } from "@/llm/context";
import type { Format } from "@/llm/formatting";
import type { Message } from "@/llm/messages";
import type { Params } from "@/llm/models";
import type { ProviderId } from "@/llm/providers/provider-id";
import type { Tools, ContextTools } from "@/llm/tools";

import { BaseProvider, type ProviderErrorMap } from "@/llm/providers/base";
import {
  extractModelScope,
  getDefaultRouterBaseUrl,
  createUnderlyingProvider,
} from "@/llm/providers/mirascope/_utils";
import { ContextResponse } from "@/llm/responses/context-response";
import { ContextStreamResponse } from "@/llm/responses/context-stream-response";
import { Response } from "@/llm/responses/response";
import { StreamResponse } from "@/llm/responses/stream-response";

export interface MirascopeProviderInit {
  apiKey?: string;
  baseURL?: string;
}

export class MirascopeProvider extends BaseProvider {
  readonly id: ProviderId = "mirascope";
  protected readonly errorMap: ProviderErrorMap = [];

  private readonly apiKey: string;
  private readonly routerBaseUrl: string;

  constructor(init?: MirascopeProviderInit) {
    super();
    const apiKey = init?.apiKey ?? process.env.MIRASCOPE_API_KEY;
    if (!apiKey) {
      throw new Error(
        "Mirascope API key not found. " +
          "Set MIRASCOPE_API_KEY environment variable or pass apiKey parameter.",
      );
    }
    this.apiKey = apiKey;
    this.routerBaseUrl = init?.baseURL ?? getDefaultRouterBaseUrl();
  }

  private getUnderlyingProvider(modelId: string): BaseProvider {
    const modelScope = extractModelScope(modelId);
    if (!modelScope) {
      throw new Error(
        `Invalid model ID format: ${modelId}. ` +
          `Expected format 'scope/model-name' (e.g., 'openai/gpt-4')`,
      );
    }
    return createUnderlyingProvider(
      modelScope,
      this.apiKey,
      this.routerBaseUrl,
    );
  }

  protected async _call(args: {
    modelId: string;
    messages: readonly Message[];
    tools?: Tools;
    format?: Format | null;
    params?: Params;
  }): Promise<Response> {
    const provider = this.getUnderlyingProvider(args.modelId);
    return provider.call(args);
  }

  protected async _stream(args: {
    modelId: string;
    messages: readonly Message[];
    tools?: Tools;
    format?: Format | null;
    params?: Params;
  }): Promise<StreamResponse> {
    const provider = this.getUnderlyingProvider(args.modelId);
    return provider.stream(args);
  }

  protected async _contextCall<DepsT>(args: {
    ctx: Context<DepsT>;
    modelId: string;
    messages: readonly Message[];
    tools?: ContextTools<DepsT>;
    format?: Format | null;
    params?: Params;
  }): Promise<ContextResponse<DepsT>> {
    const provider = this.getUnderlyingProvider(args.modelId);
    return provider.contextCall(args);
  }

  protected async _contextStream<DepsT>(args: {
    ctx: Context<DepsT>;
    modelId: string;
    messages: readonly Message[];
    tools?: ContextTools<DepsT>;
    format?: Format | null;
    params?: Params;
  }): Promise<ContextStreamResponse<DepsT>> {
    const provider = this.getUnderlyingProvider(args.modelId);
    return provider.contextStream(args);
  }

  /* v8 ignore next 3 - unreachable: errors handled by underlying providers */
  protected getErrorStatus(_e: Error): number | undefined {
    return undefined;
  }
}
