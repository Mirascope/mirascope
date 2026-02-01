import { Context, Effect } from "effect";
import { describe, it, expect } from "vitest";

import { DrizzleORM, type DrizzleORMClient } from "@/db/client";
import { Payments } from "@/payments";
import { dependencyProvider } from "@/utils";

describe("dependencyProvider", () => {
  const mockClient = {} as DrizzleORMClient;
  const mockPayments = {} as Context.Tag.Service<Payments>;
  const provideDependencies = dependencyProvider([
    { tag: DrizzleORM, instance: mockClient },
    { tag: Payments, instance: mockPayments },
  ]);

  it("should preserve method identity", () => {
    class MockService {
      method() {
        return Effect.succeed("result");
      }
    }

    const ready = provideDependencies(new MockService());

    // Access the same method twice
    const method1 = ready.method;
    const method2 = ready.method;

    // They should be the exact same function (reference equality)
    expect(method1).toBe(method2);
  });

  it("should preserve nested object identity", () => {
    // Create a mock service with nested objects
    class MockService {
      nested = {
        method() {
          return Effect.succeed("nested-result");
        },
      };

      method() {
        return Effect.succeed("result");
      }
    }

    const ready = provideDependencies(new MockService());

    // Access the same nested object twice
    const nested1 = ready.nested;
    const nested2 = ready.nested;

    // They should be the exact same object (reference equality)
    expect(nested1).toBe(nested2);
  });

  it("should preserve deeply nested object identity", () => {
    class MockService {
      level1 = {
        level2: {
          method() {
            return Effect.succeed("deep-result");
          },
        },
      };
    }

    const ready = provideDependencies(new MockService());

    // Access the same deeply nested objects multiple times
    const level1_a = ready.level1;
    const level1_b = ready.level1;
    expect(level1_a).toBe(level1_b);

    const level2_a = ready.level1.level2;
    const level2_b = ready.level1.level2;
    expect(level2_a).toBe(level2_b);
  });

  it("should work with WeakMap keyed by nested objects", () => {
    class MockService {
      nested = {
        method() {
          return Effect.succeed("result");
        },
      };
    }
    const service = new MockService();
    const ready = provideDependencies(service);

    // WeakMaps require reference equality
    const weakMap = new WeakMap<object, string>();
    weakMap.set(ready.nested, "cached-value");

    // Should be able to retrieve the value using the same nested object
    expect(weakMap.get(ready.nested)).toBe("cached-value");
  });

  it("should return cached nested object on subsequent access", () => {
    let wrapCount = 0;

    class NestedClass {
      count = wrapCount++;
      method() {
        return Effect.succeed("nested-result");
      }
    }

    class MockService {
      nested = new NestedClass();
    }

    const service = new MockService();
    const ready = provideDependencies(service);

    // First access wraps the object
    const firstAccess = ready.nested;
    const firstWrapCount = wrapCount;

    // Second access should return cached wrapper (no new wrap)
    const secondAccess = ready.nested;
    const secondWrapCount = wrapCount;

    // Verify caching worked - no additional wrapping occurred
    expect(firstWrapCount).toBe(secondWrapCount);
    expect(firstAccess).toBe(secondAccess);
  });

  it("should handle array values correctly", () => {
    class MockService {
      items = [1, 2, 3];
      method() {
        return Effect.succeed("result");
      }
    }

    const service = new MockService();
    const ready = provideDependencies(service);

    // Arrays should pass through without wrapping
    const items = ready.items;
    expect(Array.isArray(items)).toBe(true);
    expect(items).toEqual([1, 2, 3]);
  });
});
