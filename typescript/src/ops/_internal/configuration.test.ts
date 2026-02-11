import type { Tracer } from "@opentelemetry/api";

import { NodeTracerProvider } from "@opentelemetry/sdk-trace-node";
import { describe, it, expect, beforeEach, afterEach } from "vitest";

import {
  configure,
  forceFlush,
  getTracer,
  setTracer,
  shutdown,
  tracerContext,
  resetConfiguration,
} from "./configuration";

describe("configuration", () => {
  beforeEach(() => {
    resetConfiguration();
  });

  afterEach(() => {
    resetConfiguration();
  });

  describe("configure", () => {
    it("should create tracer when called with defaults", () => {
      configure();
      expect(getTracer()).not.toBeNull();
    });

    it("should use custom tracer provider when provided", () => {
      const customProvider = new NodeTracerProvider();
      configure({ tracerProvider: customProvider });
      expect(getTracer()).not.toBeNull();
    });

    it("should use custom tracer name", () => {
      configure({ tracerName: "custom.tracer" });
      const tracer = getTracer();
      expect(tracer).not.toBeNull();
    });

    it("should use custom tracer version", () => {
      configure({ tracerName: "test", tracerVersion: "1.0.0" });
      expect(getTracer()).not.toBeNull();
    });

    it("should accept apiKey option", () => {
      configure({ apiKey: "test-key" });
      expect(getTracer()).not.toBeNull();
    });

    it("should accept baseURL option", () => {
      configure({ baseURL: "https://custom.example.com" });
      expect(getTracer()).not.toBeNull();
    });

    it("should accept multiple options", () => {
      configure({
        apiKey: "test-key",
        baseURL: "https://custom.example.com",
        tracerName: "my.tracer",
        tracerVersion: "2.0.0",
      });
      expect(getTracer()).not.toBeNull();
    });
  });

  describe("getTracer", () => {
    it("should return null before configure", () => {
      expect(getTracer()).toBeNull();
    });

    it("should return tracer after configure", () => {
      configure();
      expect(getTracer()).not.toBeNull();
    });
  });

  describe("setTracer", () => {
    it("should allow setting tracer directly", () => {
      const mockTracer = { startSpan: () => {} } as unknown as Tracer;
      setTracer(mockTracer);
      expect(getTracer()).toBe(mockTracer);
    });

    it("should allow clearing tracer with null", () => {
      configure();
      expect(getTracer()).not.toBeNull();

      setTracer(null);
      expect(getTracer()).toBeNull();
    });
  });

  describe("tracerContext", () => {
    it("should temporarily set tracer", () => {
      const original = { name: "original" } as unknown as Tracer;
      const temporary = { name: "temporary" } as unknown as Tracer;
      setTracer(original);

      tracerContext(temporary, () => {
        expect(getTracer()).toBe(temporary);
      });

      expect(getTracer()).toBe(original);
    });

    it("should restore tracer even on error", () => {
      const original = { name: "original" } as unknown as Tracer;
      const temporary = { name: "temporary" } as unknown as Tracer;
      setTracer(original);

      expect(() =>
        tracerContext(temporary, () => {
          throw new Error("test error");
        }),
      ).toThrow("test error");

      expect(getTracer()).toBe(original);
    });

    it("should return the function result", () => {
      const result = tracerContext(null, () => {
        return "test result";
      });

      expect(result).toBe("test result");
    });

    it("should work with async-like patterns", () => {
      const asyncLikeResult = tracerContext(null, () => {
        return Promise.resolve(42);
      });

      expect(asyncLikeResult).toBeInstanceOf(Promise);
    });

    it("should work with null tracer", () => {
      configure();
      const originalTracer = getTracer();

      tracerContext(null, () => {
        expect(getTracer()).toBeNull();
      });

      expect(getTracer()).toBe(originalTracer);
    });

    it("should support nested contexts", () => {
      const tracer1 = { name: "tracer1" } as unknown as Tracer;
      const tracer2 = { name: "tracer2" } as unknown as Tracer;
      const tracer3 = { name: "tracer3" } as unknown as Tracer;
      setTracer(tracer1);

      tracerContext(tracer2, () => {
        expect(getTracer()).toBe(tracer2);

        tracerContext(tracer3, () => {
          expect(getTracer()).toBe(tracer3);
        });

        expect(getTracer()).toBe(tracer2);
      });

      expect(getTracer()).toBe(tracer1);
    });
  });

  describe("forceFlush", () => {
    it("should no-op when not configured", async () => {
      await expect(forceFlush()).resolves.toBeUndefined();
    });

    it("should delegate to provider forceFlush", async () => {
      configure();
      await expect(forceFlush()).resolves.toBeUndefined();
    });
  });

  describe("shutdown", () => {
    it("should no-op when not configured", async () => {
      await expect(shutdown()).resolves.toBeUndefined();
    });

    it("should delegate to provider shutdown", async () => {
      configure();
      await expect(shutdown()).resolves.toBeUndefined();
    });
  });

  describe("resetConfiguration", () => {
    it("should reset tracer to null", () => {
      configure();
      expect(getTracer()).not.toBeNull();

      resetConfiguration();
      expect(getTracer()).toBeNull();
    });

    it("should allow reconfiguring after reset", () => {
      configure({ tracerName: "first" });
      resetConfiguration();
      configure({ tracerName: "second" });

      expect(getTracer()).not.toBeNull();
    });
  });
});
