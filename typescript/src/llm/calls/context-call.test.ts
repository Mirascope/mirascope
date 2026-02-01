import { describe, expect, it } from "vitest";

import { defineCall } from "@/llm/calls/call";
import { createContext, type Context } from "@/llm/context";
import { system, user } from "@/llm/messages";
import { Model } from "@/llm/models";

interface TestDeps {
  userId: string;
  userName: string;
}

describe("defineCall (context-aware)", () => {
  describe("with variables", () => {
    it("creates a call with messages method", () => {
      const greetUser = defineCall<{
        ctx: Context<TestDeps>;
        greeting: string;
      }>({
        model: "anthropic/claude-sonnet-4-20250514",
        template: ({ ctx, greeting }) =>
          `${greeting}, ${ctx.deps.userName}! (ID: ${ctx.deps.userId})`,
      });

      const ctx = createContext<TestDeps>({ userId: "123", userName: "Alice" });
      const messages = greetUser.prompt.messages(ctx, { greeting: "Hello" });

      expect(messages).toHaveLength(1);
      expect(messages[0]).toMatchObject({
        role: "user",
        content: [{ type: "text", text: "Hello, Alice! (ID: 123)" }],
      });
    });

    it("stores the model", () => {
      const call = defineCall<{ ctx: Context<TestDeps>; name: string }>({
        model: "anthropic/claude-sonnet-4-20250514",
        template: ({ ctx, name }) => `Hello, ${name} from ${ctx.deps.userId}!`,
      });

      expect(call.model).toBeInstanceOf(Model);
      expect(call.model.modelId).toBe("anthropic/claude-sonnet-4-20250514");
    });

    it("stores the template function", () => {
      const template = ({
        ctx,
        name,
      }: {
        ctx: Context<TestDeps>;
        name: string;
      }) => `Hello, ${name} from ${ctx.deps.userId}!`;
      const call = defineCall<{ ctx: Context<TestDeps>; name: string }>({
        model: "anthropic/claude-sonnet-4-20250514",
        template,
      });

      expect(call.template).toBe(template);
    });

    it("exposes the underlying prompt", () => {
      const call = defineCall<{ ctx: Context<TestDeps>; name: string }>({
        model: "anthropic/claude-sonnet-4-20250514",
        template: ({ ctx, name }) => `Hello, ${name} from ${ctx.deps.userId}!`,
      });

      const ctx = createContext<TestDeps>({ userId: "123", userName: "Alice" });

      expect(call.prompt).toBeDefined();
      expect(call.prompt.messages(ctx, { name: "World" })).toHaveLength(1);
    });

    it("supports message arrays", () => {
      interface SystemDeps {
        systemPrompt: string;
      }

      const chatBot = defineCall<{
        ctx: Context<SystemDeps>;
        question: string;
      }>({
        model: "anthropic/claude-sonnet-4-20250514",
        template: ({ ctx, question }) => [
          system(ctx.deps.systemPrompt),
          user(question),
        ],
      });

      const ctx = createContext<SystemDeps>({
        systemPrompt: "You are helpful.",
      });
      const messages = chatBot.prompt.messages(ctx, {
        question: "What is TypeScript?",
      });

      expect(messages).toHaveLength(2);
      expect(messages[0]).toMatchObject({ role: "system" });
      expect(messages[1]).toMatchObject({
        role: "user",
        content: [{ type: "text", text: "What is TypeScript?" }],
      });
    });

    it("accepts a Model instance", () => {
      const model = new Model("anthropic/claude-sonnet-4-20250514", {
        temperature: 0.7,
      });
      const call = defineCall<{ ctx: Context<TestDeps>; topic: string }>({
        model,
        template: ({ ctx, topic }) =>
          `Write about ${topic} for ${ctx.deps.userName}`,
      });

      expect(call.model).toBe(model);
      expect(call.model.params).toEqual({ temperature: 0.7 });
    });

    it("accepts params as top-level properties", () => {
      const call = defineCall<{ ctx: Context<TestDeps>; query: string }>({
        model: "anthropic/claude-sonnet-4-20250514",
        temperature: 0,
        maxTokens: 100,
        template: ({ ctx, query }) => `${ctx.deps.userName}: ${query}`,
      });

      expect(call.model.params).toEqual({ temperature: 0, maxTokens: 100 });
    });

    it("throws when passing params with Model instance", () => {
      const model = new Model("anthropic/claude-sonnet-4-20250514");

      expect(() =>
        defineCall<{ ctx: Context<TestDeps>; query: string }>({
          model,
          temperature: 0.5,
          template: ({ ctx, query }) => `${ctx.deps.userName}: ${query}`,
        }),
      ).toThrow(
        "Cannot pass params when model is a Model instance. Use new Model(id, params) instead.",
      );
    });

    it("has a stream method", () => {
      const call = defineCall<{ ctx: Context<TestDeps>; greeting: string }>({
        model: "anthropic/claude-sonnet-4-20250514",
        template: ({ ctx, greeting }) => `${greeting}, ${ctx.deps.userName}!`,
      });

      expect(typeof call.stream).toBe("function");
    });

    it("has a call method", () => {
      const call = defineCall<{ ctx: Context<TestDeps>; greeting: string }>({
        model: "anthropic/claude-sonnet-4-20250514",
        template: ({ ctx, greeting }) => `${greeting}, ${ctx.deps.userName}!`,
      });

      expect(typeof call.call).toBe("function");
    });
  });

  describe("without variables", () => {
    it("creates a call that can be called without vars", () => {
      const sayHello = defineCall<{ ctx: Context<TestDeps> }>({
        model: "anthropic/claude-sonnet-4-20250514",
        template: ({ ctx }) => `Hello, ${ctx.deps.userName}!`,
      });

      const ctx = createContext<TestDeps>({ userId: "123", userName: "Alice" });
      const messages = sayHello.prompt.messages(ctx);

      expect(messages).toHaveLength(1);
      expect(messages[0]).toMatchObject({
        role: "user",
        content: [{ type: "text", text: "Hello, Alice!" }],
      });
    });

    it("supports message arrays without variables", () => {
      interface SystemDeps {
        systemPrompt: string;
        defaultQuestion: string;
      }

      const call = defineCall<{ ctx: Context<SystemDeps> }>({
        model: "anthropic/claude-sonnet-4-20250514",
        template: ({ ctx }) => [
          system(ctx.deps.systemPrompt),
          user(ctx.deps.defaultQuestion),
        ],
      });

      const ctx = createContext<SystemDeps>({
        systemPrompt: "You are helpful.",
        defaultQuestion: "What can you do?",
      });
      const messages = call.prompt.messages(ctx);

      expect(messages).toHaveLength(2);
    });

    it("accepts params without variables", () => {
      const call = defineCall<{ ctx: Context<TestDeps> }>({
        model: "anthropic/claude-sonnet-4-20250514",
        temperature: 0.5,
        template: ({ ctx }) => `Hello, ${ctx.deps.userName}!`,
      });

      expect(call.model.params).toEqual({ temperature: 0.5 });
    });

    it("has a stream method", () => {
      const call = defineCall<{ ctx: Context<TestDeps> }>({
        model: "anthropic/claude-sonnet-4-20250514",
        template: ({ ctx }) => `Hello, ${ctx.deps.userName}!`,
      });

      expect(typeof call.stream).toBe("function");
    });

    it("has a call method", () => {
      const call = defineCall<{ ctx: Context<TestDeps> }>({
        model: "anthropic/claude-sonnet-4-20250514",
        template: ({ ctx }) => `Hello, ${ctx.deps.userName}!`,
      });

      expect(typeof call.call).toBe("function");
    });
  });
});
