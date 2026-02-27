import { describe, it, expect } from "vitest";

import type {
  Jsonable,
  BaseOpsOptions,
  TraceOptions,
  VersionOptions,
  PropagatorFormat,
} from "./types";

describe("types", () => {
  describe("Jsonable", () => {
    it("should accept string primitives", () => {
      const value: Jsonable = "hello";
      expect(value).toBe("hello");
    });

    it("should accept number primitives", () => {
      const value: Jsonable = 42;
      expect(value).toBe(42);
    });

    it("should accept boolean primitives", () => {
      const value: Jsonable = true;
      expect(value).toBe(true);
    });

    it("should accept null", () => {
      const value: Jsonable = null;
      expect(value).toBeNull();
    });

    it("should accept arrays of primitives", () => {
      const arr: Jsonable = [1, "two", true, null];
      expect(arr).toEqual([1, "two", true, null]);
    });

    it("should accept nested objects", () => {
      const obj: Jsonable = {
        name: "test",
        count: 42,
        active: true,
        nested: { deep: [1, 2, 3] },
      };
      expect(obj).toEqual({
        name: "test",
        count: 42,
        active: true,
        nested: { deep: [1, 2, 3] },
      });
    });

    it("should accept deeply nested structures", () => {
      const value: Jsonable = {
        level1: {
          level2: {
            level3: [{ key: "value" }],
          },
        },
      };
      expect(value).toBeDefined();
    });
  });

  describe("TraceOptions", () => {
    it("should require name", () => {
      const opts: TraceOptions = { name: "myFn" };
      expect(opts.name).toBe("myFn");
    });

    it("should accept tags with name", () => {
      const opts: TraceOptions = {
        name: "myFn",
        tags: ["production", "v1"],
      };
      expect(opts.tags).toHaveLength(2);
    });

    it("should accept metadata with name", () => {
      const opts: TraceOptions = {
        name: "myFn",
        metadata: { version: "1.0.0", environment: "prod" },
      };
      expect(opts.metadata?.version).toBe("1.0.0");
    });

    it("should accept name, tags, and metadata together", () => {
      const opts: TraceOptions = {
        name: "myFn",
        tags: ["v1"],
        metadata: { key: "value" },
      };
      expect(opts.name).toBe("myFn");
      expect(opts.tags).toBeDefined();
      expect(opts.metadata).toBeDefined();
    });
  });

  describe("BaseOpsOptions", () => {
    it("should accept empty options", () => {
      const opts: BaseOpsOptions = {};
      expect(opts).toEqual({});
    });

    it("should accept tags and metadata", () => {
      const opts: BaseOpsOptions = {
        tags: ["v1"],
        metadata: { key: "value" },
      };
      expect(opts.tags).toBeDefined();
      expect(opts.metadata).toBeDefined();
    });
  });

  describe("VersionOptions", () => {
    it("should extend BaseOpsOptions with optional name", () => {
      const opts: VersionOptions = {
        tags: ["v1"],
        metadata: { key: "value" },
      };
      expect(opts.tags).toBeDefined();
      expect(opts.metadata).toBeDefined();
      expect(opts.name).toBeUndefined();
    });

    it("should accept optional name property", () => {
      const opts: VersionOptions = {
        name: "my-function",
      };
      expect(opts.name).toBe("my-function");
    });

    it("should accept all properties together", () => {
      const opts: VersionOptions = {
        name: "embedding-v1",
        tags: ["production", "embeddings"],
        metadata: { algorithm: "ada-002" },
      };
      expect(opts.name).toBe("embedding-v1");
      expect(opts.tags).toHaveLength(2);
      expect(opts.metadata?.algorithm).toBe("ada-002");
    });
  });

  describe("PropagatorFormat", () => {
    it("should accept tracecontext", () => {
      const format: PropagatorFormat = "tracecontext";
      expect(format).toBe("tracecontext");
    });

    it("should accept b3", () => {
      const format: PropagatorFormat = "b3";
      expect(format).toBe("b3");
    });

    it("should accept b3multi", () => {
      const format: PropagatorFormat = "b3multi";
      expect(format).toBe("b3multi");
    });

    it("should accept jaeger", () => {
      const format: PropagatorFormat = "jaeger";
      expect(format).toBe("jaeger");
    });

    it("should accept composite", () => {
      const format: PropagatorFormat = "composite";
      expect(format).toBe("composite");
    });

    it("should accept all valid formats in array", () => {
      const formats: PropagatorFormat[] = [
        "tracecontext",
        "b3",
        "b3multi",
        "jaeger",
        "composite",
      ];
      expect(formats).toHaveLength(5);
    });
  });
});
