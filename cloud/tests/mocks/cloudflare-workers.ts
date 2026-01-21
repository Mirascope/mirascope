/**
 * Mock for cloudflare:workers module used in tests.
 *
 * Provides a minimal DurableObject base class that mirrors the Cloudflare
 * runtime behavior for testing purposes.
 */

/**
 * Mock DurableObject base class.
 *
 * In the actual Cloudflare runtime, this class provides `ctx` and `env`
 * properties. Our mock stores them for test access.
 */
export abstract class DurableObject<Env = unknown> {
  protected ctx: DurableObjectState;
  protected env: Env;

  constructor(ctx: DurableObjectState, env: Env) {
    this.ctx = ctx;
    this.env = env;
  }
}
