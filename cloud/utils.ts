/**
 * @fileoverview Shared utility functions for Effect-based services.
 */

import { Context, Effect } from "effect";

/**
 * Type representing a service tag and its instance for dependency provision.
 */
export type ServiceProvider = {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  tag: Context.Tag<any, any>;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  instance: any;
};

/**
 * Type that transforms a service by removing all dependencies from methods.
 *
 * This represents a "ready" service where dependencies have been provided.
 * Methods return `Effect<A, E>` instead of `Effect<A, E, R>`.
 */
export type Ready<T> = {
  [K in keyof T]: T[K] extends (
    ...args: infer A
  ) => Effect.Effect<infer R, infer E, unknown>
    ? (...args: A) => Effect.Effect<R, E>
    : T[K] extends object
      ? Ready<T[K]>
      : T[K];
};

/**
 * Creates a dependency provider that wraps services to automatically provide dependencies.
 *
 * Returns a function that takes a service and returns a "ready" version where all methods
 * have the specified dependencies pre-provided via Effect.provideService.
 *
 * This eliminates duplication of the complex proxy logic needed to wrap service methods
 * and handle nested objects, caching, and enumerable properties for spread operators.
 *
 * @param providers - Array of service tags and instances to provide
 * @returns A function that wraps services to provide all specified dependencies
 *
 * @example
 * ```ts
 * // Create a provider for database services
 * const provideDependencies = dependencyProvider([
 *   { tag: DrizzleORM, instance: client },
 *   { tag: Payments, instance: payments },
 * ]);
 *
 * // Use it to make services ready
 * const readyUsers = provideDependencies(new Users());
 * const readyOrgs = provideDependencies(new Organizations());
 * ```
 *
 * @example
 * ```ts
 * // Create a provider for payment services
 * const provideDependencies = dependencyProvider([
 *   { tag: Stripe, instance: stripe },
 * ]);
 *
 * const readyCustomers = provideDependencies(new Customers());
 * ```
 */
export const dependencyProvider = (providers: ServiceProvider[]) => {
  return <T extends object>(service: T): Ready<T> => {
    const proto = Object.getPrototypeOf(service) as object;

    // Collect all method names from prototype
    const methodNames = Object.getOwnPropertyNames(proto).filter(
      (key) =>
        key !== "constructor" &&
        typeof (service as Record<string, unknown>)[key] === "function",
    );

    type WrappedMethod = (
      ...args: unknown[]
    ) => Effect.Effect<unknown, unknown, never>;

    // Helper to wrap a method with all dependency provisions
    const wrapMethod =
      (method: (...args: unknown[]) => unknown): WrappedMethod =>
      (...args: unknown[]) => {
        let effect = method.apply(service, args) as Effect.Effect<
          unknown,
          unknown,
          unknown
        >;

        // Apply all providers
        for (const provider of providers) {
          effect = effect.pipe(
            Effect.provideService(provider.tag, provider.instance),
          );
        }

        return effect as Effect.Effect<unknown, unknown, never>;
      };

    // Cache wrapped methods to ensure consistent identity
    const wrappedMethods = new Map<string | symbol, WrappedMethod>();
    // Cache wrapped nested objects to preserve identity
    const wrappedObjects = new Map<string | symbol, object>();

    const getWrappedMethod = (prop: string | symbol): WrappedMethod => {
      let wrapped = wrappedMethods.get(prop);
      if (!wrapped) {
        const method = (service as Record<string | symbol, unknown>)[prop];
        if (typeof method === "function") {
          wrapped = wrapMethod(method as (...args: unknown[]) => unknown);
          wrappedMethods.set(prop, wrapped);
        }
      }
      return wrapped!;
    };

    return new Proxy(service, {
      get(target, prop, receiver) {
        const value = Reflect.get(target, prop, receiver);

        // Wrap functions to provide dependencies
        if (typeof value === "function") {
          return getWrappedMethod(prop);
        }

        // Recursively wrap nested objects (with caching to preserve identity)
        if (value && typeof value === "object" && !Array.isArray(value)) {
          let wrapped = wrappedObjects.get(prop);
          if (!wrapped) {
            // Recursively apply the same providers to nested objects
            wrapped = dependencyProvider(providers)(value as object);
            wrappedObjects.set(prop, wrapped);
          }
          return wrapped;
        }

        return value;
      },

      // Make prototype methods appear as own properties for spread operator
      ownKeys() {
        return [...methodNames, ...Object.keys(service)];
      },

      getOwnPropertyDescriptor(target, prop) {
        // For prototype methods, make them enumerable
        if (typeof prop === "string" && methodNames.includes(prop)) {
          return {
            configurable: true,
            enumerable: true,
            writable: true,
            value: getWrappedMethod(prop),
          };
        }
        return Object.getOwnPropertyDescriptor(target, prop);
      },
    }) as Ready<T>;
  };
};
