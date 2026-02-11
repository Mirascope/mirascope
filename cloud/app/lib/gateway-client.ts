/**
 * Browser-side WebSocket client for the OpenClaw gateway JSON-RPC protocol.
 *
 * Communicates with the server-side WS proxy at `/api/ws/claws/:orgSlug/:clawSlug`.
 * The proxy handles authentication and the OpenClaw connect handshake; the browser
 * only sees JSON-RPC request/response frames and streaming events.
 *
 * ## Protocol
 *
 * **Request:**  `{ type: "req", id: string, method: string, params?: unknown }`
 * **Response:** `{ type: "res", id: string, ok: boolean, payload: unknown }`
 * **Event:**    `{ type: "event", event: string, payload: unknown }`
 */

type ConnectionState = "disconnected" | "connecting" | "connected" | "error";

type EventHandler = (payload: unknown) => void;

type PendingRequest = {
  resolve: (payload: unknown) => void;
  reject: (error: Error) => void;
};

let nextRequestId = 1;

export class GatewayClient {
  private ws: WebSocket | null = null;
  private _state: ConnectionState = "disconnected";
  private pendingRequests = new Map<string, PendingRequest>();
  private eventHandlers = new Map<string, Set<EventHandler>>();
  private stateChangeHandlers = new Set<(state: ConnectionState) => void>();
  private connectResolve: (() => void) | null = null;

  get state(): ConnectionState {
    return this._state;
  }

  private setState(state: ConnectionState) {
    this._state = state;
    for (const handler of this.stateChangeHandlers) {
      handler(state);
    }
  }

  onStateChange(handler: (state: ConnectionState) => void): () => void {
    this.stateChangeHandlers.add(handler);
    return () => {
      this.stateChangeHandlers.delete(handler);
    };
  }

  connect(orgSlug: string, clawSlug: string): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.ws) {
        this.disconnect();
      }

      this.setState("connecting");

      const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
      const url = `${protocol}//${window.location.host}/api/ws/claws/${orgSlug}/${clawSlug}`;

      this.ws = new WebSocket(url);

      this.connectResolve = resolve;

      this.ws.onopen = () => {
        // Don't resolve yet — wait for the proxy to complete the upstream
        // handshake and send a "proxy.ready" message.
        this.setState("connecting");
      };

      this.ws.onerror = () => {
        if (this._state === "connecting") {
          this.setState("error");
          reject(new Error("WebSocket connection failed"));
        } else {
          this.setState("error");
        }
      };

      this.ws.onclose = (event) => {
        // Reject all pending requests
        for (const [, pending] of this.pendingRequests) {
          pending.reject(
            new Error(`WebSocket closed: ${event.code} ${event.reason}`),
          );
        }
        this.pendingRequests.clear();

        if (this._state === "connecting") {
          this.setState("error");
          reject(new Error(`WebSocket closed during connect: ${event.code}`));
        } else {
          this.setState("disconnected");
        }
      };

      this.ws.onmessage = (event) => {
        this.handleMessage(event.data as string);
      };
    });
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close(1000, "Client disconnect");
      this.ws = null;
    }
    this.pendingRequests.clear();
    this.setState("disconnected");
  }

  /**
   * Send a JSON-RPC request and wait for its response.
   */
  rpc(method: string, params?: unknown): Promise<unknown> {
    return new Promise((resolve, reject) => {
      if (!this.ws || this._state !== "connected") {
        reject(new Error("Not connected"));
        return;
      }

      const id = String(nextRequestId++);
      this.pendingRequests.set(id, { resolve, reject });

      this.ws.send(
        JSON.stringify({ type: "req", id, method, params: params ?? {} }),
      );
    });
  }

  // ---------------------------------------------------------------------------
  // Typed convenience methods
  // ---------------------------------------------------------------------------

  chatSend(params: {
    sessionKey: string;
    message: string;
    idempotencyKey: string;
  }): Promise<{ runId: string }> {
    return this.rpc("chat.send", params) as Promise<{ runId: string }>;
  }

  chatHistory(params: { sessionKey: string }): Promise<unknown[]> {
    return this.rpc("chat.history", params) as Promise<unknown[]>;
  }

  chatAbort(params?: { runId?: string; sessionKey?: string }): Promise<void> {
    return this.rpc("chat.abort", params ?? {}) as Promise<void>;
  }

  sessionsList(): Promise<unknown[]> {
    return this.rpc("sessions.list") as Promise<unknown[]>;
  }

  // ---------------------------------------------------------------------------
  // Event subscription
  // ---------------------------------------------------------------------------

  /**
   * Subscribe to gateway events. Returns an unsubscribe function.
   *
   * @param event - Event name (e.g., "chat.text.delta", "chat.done")
   *                Use "*" to subscribe to all events.
   */
  on(event: string, handler: EventHandler): () => void {
    let handlers = this.eventHandlers.get(event);
    if (!handlers) {
      handlers = new Set();
      this.eventHandlers.set(event, handlers);
    }
    handlers.add(handler);

    return () => {
      handlers!.delete(handler);
      if (handlers!.size === 0) {
        this.eventHandlers.delete(event);
      }
    };
  }

  // ---------------------------------------------------------------------------
  // Internal
  // ---------------------------------------------------------------------------

  private handleMessage(data: string) {
    let msg: {
      type: string;
      id?: string;
      ok?: boolean;
      payload?: unknown;
      event?: string;
      error?: unknown;
    };
    try {
      msg = JSON.parse(data);
    } catch {
      console.warn("[GatewayClient] Invalid JSON from server:", data);
      return;
    }

    // The server-side proxy sends this after completing the gateway handshake
    if (msg.type === "proxy.ready") {
      this.setState("connected");
      if (this.connectResolve) {
        this.connectResolve();
        this.connectResolve = null;
      }
      return;
    }

    if (msg.type === "res" && msg.id) {
      const pending = this.pendingRequests.get(msg.id);
      if (pending) {
        this.pendingRequests.delete(msg.id);
        if (msg.ok) {
          pending.resolve(msg.payload);
        } else {
          pending.reject(
            new Error(
              typeof msg.error === "string"
                ? msg.error
                : JSON.stringify(msg.error ?? msg.payload ?? "RPC error"),
            ),
          );
        }
      }
    } else if (msg.type === "event" && msg.event) {
      // Dispatch to specific event handlers
      const handlers = this.eventHandlers.get(msg.event);
      if (handlers) {
        for (const handler of handlers) {
          handler(msg.payload);
        }
      }

      // Dispatch to wildcard handlers
      const wildcardHandlers = this.eventHandlers.get("*");
      if (wildcardHandlers) {
        for (const handler of wildcardHandlers) {
          handler({ event: msg.event, payload: msg.payload });
        }
      }
    }
  }
}
