import { describe, it, expect } from "vitest";

import {
  jsonStringify,
  toJsonable,
  getQualifiedName,
  extractArguments,
} from "./utils";

describe("utils", () => {
  describe("jsonStringify()", () => {
    it("should stringify simple values", () => {
      expect(jsonStringify("hello")).toBe('"hello"');
      expect(jsonStringify(123)).toBe("123");
      expect(jsonStringify(true)).toBe("true");
      expect(jsonStringify(null)).toBe("null");
    });

    it("should stringify objects", () => {
      expect(jsonStringify({ key: "value" })).toBe('{"key":"value"}');
    });

    it("should stringify arrays", () => {
      expect(jsonStringify([1, 2, 3])).toBe("[1,2,3]");
    });

    it("should handle nested structures", () => {
      const nested = {
        a: { b: { c: 1 } },
        arr: [1, [2, 3]],
      };
      expect(jsonStringify(nested)).toBe('{"a":{"b":{"c":1}},"arr":[1,[2,3]]}');
    });

    it("should handle circular references gracefully", () => {
      const circular: Record<string, unknown> = { a: 1 };
      circular.self = circular;

      // Should not throw, returns string representation
      const result = jsonStringify(circular);
      expect(typeof result).toBe("string");
    });

    it("should handle BigInt by returning string representation", () => {
      const obj = { bigint: BigInt(12345678901234567890n) };
      // BigInt causes JSON.stringify to throw, so we fall back to String()
      const result = jsonStringify(obj);
      expect(typeof result).toBe("string");
    });
  });

  describe("toJsonable()", () => {
    it("should pass through null", () => {
      expect(toJsonable(null)).toBe(null);
    });

    it("should pass through primitives", () => {
      expect(toJsonable("hello")).toBe("hello");
      expect(toJsonable(123)).toBe(123);
      expect(toJsonable(true)).toBe(true);
      expect(toJsonable(false)).toBe(false);
    });

    it("should convert arrays recursively", () => {
      expect(toJsonable([1, "two", true])).toEqual([1, "two", true]);
    });

    it("should convert objects recursively", () => {
      const result = toJsonable({ a: 1, b: "two", c: { d: true } });
      expect(result).toEqual({ a: 1, b: "two", c: { d: true } });
    });

    it("should convert undefined to string", () => {
      expect(toJsonable(undefined)).toBe("undefined");
    });

    it("should convert functions to string", () => {
      const fn = () => {};
      expect(typeof toJsonable(fn)).toBe("string");
    });

    it("should convert symbols to string", () => {
      const sym = Symbol("test");
      expect(typeof toJsonable(sym)).toBe("string");
    });
  });

  describe("getQualifiedName()", () => {
    it("should return function name", () => {
      function myFunction() {}
      expect(getQualifiedName(myFunction)).toBe("myFunction");
    });

    it("should return 'anonymous' for anonymous functions", () => {
      expect(getQualifiedName(() => {})).toBe("anonymous");
    });

    it("should return variable name for function expressions assigned to variables", () => {
      // In modern JS, function expressions assigned to variables get the variable name
      const fn = function () {};
      expect(getQualifiedName(fn)).toBe("fn");
    });

    it("should return name for named function expressions", () => {
      const fn = function namedFn() {};
      expect(getQualifiedName(fn)).toBe("namedFn");
    });
  });

  describe("extractArguments()", () => {
    it("should extract argument types and values", () => {
      function testFn(a: string, b: number) {
        return a + b;
      }

      const result = extractArguments(testFn, ["hello", 42]);

      expect(result.argTypes).toEqual(["a: string", "b: number"]);
      expect(result.argValues).toEqual(["hello", 42]);
    });

    it("should handle arrow functions", () => {
      const fn = (x: string) => x;

      const result = extractArguments(fn, ["test"]);

      expect(result.argTypes).toEqual(["x: string"]);
      expect(result.argValues).toEqual(["test"]);
    });

    it("should handle functions with no parameters", () => {
      const fn = () => {};

      const result = extractArguments(fn, []);

      expect(result.argTypes).toEqual([]);
      expect(result.argValues).toEqual([]);
    });

    it("should handle more args than params", () => {
      const fn = (a: string) => a;

      const result = extractArguments(fn, ["one", "two", "three"]);

      expect(result.argTypes.length).toBe(3);
      expect(result.argValues).toEqual(["one", "two", "three"]);
    });

    it("should convert object arguments to Jsonable", () => {
      const fn = (obj: Record<string, unknown>) => obj;

      const result = extractArguments(fn, [{ nested: { key: "value" } }]);

      expect(result.argValues).toEqual([{ nested: { key: "value" } }]);
    });

    it("should handle array arguments", () => {
      const fn = (arr: number[]) => arr;

      const result = extractArguments(fn, [[1, 2, 3]]);

      expect(result.argValues).toEqual([[1, 2, 3]]);
    });

    it("should handle null and boolean arguments", () => {
      const fn = (_a: null, _b: boolean) => {};

      const result = extractArguments(fn, [null, true]);

      expect(result.argValues).toEqual([null, true]);
    });

    it("should handle function with toString that has trailing comma", () => {
      // Create a mock function with a custom toString that produces empty params
      const mockFn = Object.assign((..._args: unknown[]) => null, {
        toString: () => "(a, b, ) => null", // trailing comma produces empty string
      });

      const result = extractArguments(mockFn, ["x", "y", "z"]);

      // Should skip empty param and use fallback for third arg
      expect(result.argValues).toEqual(["x", "y", "z"]);
      expect(result.argTypes[0]).toBe("a: string");
      expect(result.argTypes[1]).toBe("b: string");
      expect(result.argTypes[2]).toBe("arg2: string"); // fallback name
    });
  });
});
