/**
 * Calculator tools for basic arithmetic operations.
 */

import { llm } from "mirascope";

/**
 * Add two numbers together.
 */
export const add = llm.tool({
  name: "add",
  description: "Add two numbers together.",
  parameters: {
    type: "object",
    properties: {
      a: { type: "number", description: "The first number." },
      b: { type: "number", description: "The second number." },
    },
    required: ["a", "b"],
  },
  execute: ({ a, b }: { a: number; b: number }) => a + b,
});

/**
 * Subtract b from a.
 */
export const subtract = llm.tool({
  name: "subtract",
  description: "Subtract b from a.",
  parameters: {
    type: "object",
    properties: {
      a: { type: "number", description: "The number to subtract from." },
      b: { type: "number", description: "The number to subtract." },
    },
    required: ["a", "b"],
  },
  execute: ({ a, b }: { a: number; b: number }) => a - b,
});

/**
 * Multiply two numbers.
 */
export const multiply = llm.tool({
  name: "multiply",
  description: "Multiply two numbers.",
  parameters: {
    type: "object",
    properties: {
      a: { type: "number", description: "The first number." },
      b: { type: "number", description: "The second number." },
    },
    required: ["a", "b"],
  },
  execute: ({ a, b }: { a: number; b: number }) => a * b,
});

/**
 * Divide a by b.
 */
export const divide = llm.tool({
  name: "divide",
  description: "Divide a by b.",
  parameters: {
    type: "object",
    properties: {
      a: { type: "number", description: "The dividend." },
      b: { type: "number", description: "The divisor." },
    },
    required: ["a", "b"],
  },
  execute: ({ a, b }: { a: number; b: number }) => {
    if (b === 0) {
      throw new Error("Cannot divide by zero");
    }
    return a / b;
  },
});
