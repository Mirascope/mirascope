/**
 * Tests for Model instrumentation wrappers.
 */

import { describe, it, expect, beforeEach, afterEach } from "vitest";

import { Model } from "@/llm/models";

import {
  wrapModelCall,
  unwrapModelCall,
  wrapModelStream,
  unwrapModelStream,
  wrapModelContextCall,
  unwrapModelContextCall,
  wrapModelContextStream,
  unwrapModelContextStream,
  wrapModelResume,
  unwrapModelResume,
  wrapModelResumeStream,
  unwrapModelResumeStream,
  wrapModelContextResume,
  unwrapModelContextResume,
  wrapModelContextResumeStream,
  unwrapModelContextResumeStream,
  wrapAllModelMethods,
  unwrapAllModelMethods,
  isModelInstrumented,
} from "./model";

// Store original methods for verification
const originalCall = Model.prototype.call;
const originalStream = Model.prototype.stream;
const originalContextCall = Model.prototype.contextCall;
const originalContextStream = Model.prototype.contextStream;
const originalResume = Model.prototype.resume;
const originalResumeStream = Model.prototype.resumeStream;
const originalContextResume = Model.prototype.contextResume;
const originalContextResumeStream = Model.prototype.contextResumeStream;

describe("Model Instrumentation", () => {
  beforeEach(() => {
    // Ensure clean state
    unwrapAllModelMethods();
  });

  afterEach(() => {
    // Reset to original methods
    unwrapAllModelMethods();
  });

  describe("wrapModelCall / unwrapModelCall", () => {
    it("replaces Model.prototype.call", () => {
      expect(Model.prototype.call).toBe(originalCall);

      wrapModelCall();

      expect(Model.prototype.call).not.toBe(originalCall);
    });

    it("restores original on unwrap", () => {
      wrapModelCall();
      expect(Model.prototype.call).not.toBe(originalCall);

      unwrapModelCall();
      expect(Model.prototype.call).toBe(originalCall);
    });

    it("is idempotent", () => {
      wrapModelCall();
      const wrapped = Model.prototype.call;

      wrapModelCall();
      expect(Model.prototype.call).toBe(wrapped);

      unwrapModelCall();
      unwrapModelCall();
      expect(Model.prototype.call).toBe(originalCall);
    });
  });

  describe("wrapModelStream / unwrapModelStream", () => {
    it("replaces Model.prototype.stream", () => {
      expect(Model.prototype.stream).toBe(originalStream);

      wrapModelStream();

      expect(Model.prototype.stream).not.toBe(originalStream);
    });

    it("restores original on unwrap", () => {
      wrapModelStream();
      unwrapModelStream();

      expect(Model.prototype.stream).toBe(originalStream);
    });
  });

  describe("wrapModelContextCall / unwrapModelContextCall", () => {
    it("replaces Model.prototype.contextCall", () => {
      expect(Model.prototype.contextCall).toBe(originalContextCall);

      wrapModelContextCall();

      expect(Model.prototype.contextCall).not.toBe(originalContextCall);
    });

    it("restores original on unwrap", () => {
      wrapModelContextCall();
      unwrapModelContextCall();

      expect(Model.prototype.contextCall).toBe(originalContextCall);
    });
  });

  describe("wrapModelContextStream / unwrapModelContextStream", () => {
    it("replaces Model.prototype.contextStream", () => {
      expect(Model.prototype.contextStream).toBe(originalContextStream);

      wrapModelContextStream();

      expect(Model.prototype.contextStream).not.toBe(originalContextStream);
    });

    it("restores original on unwrap", () => {
      wrapModelContextStream();
      unwrapModelContextStream();

      expect(Model.prototype.contextStream).toBe(originalContextStream);
    });
  });

  describe("wrapModelResume / unwrapModelResume", () => {
    it("replaces Model.prototype.resume", () => {
      expect(Model.prototype.resume).toBe(originalResume);

      wrapModelResume();

      expect(Model.prototype.resume).not.toBe(originalResume);
    });

    it("restores original on unwrap", () => {
      wrapModelResume();
      unwrapModelResume();

      expect(Model.prototype.resume).toBe(originalResume);
    });
  });

  describe("wrapModelResumeStream / unwrapModelResumeStream", () => {
    it("replaces Model.prototype.resumeStream", () => {
      expect(Model.prototype.resumeStream).toBe(originalResumeStream);

      wrapModelResumeStream();

      expect(Model.prototype.resumeStream).not.toBe(originalResumeStream);
    });

    it("restores original on unwrap", () => {
      wrapModelResumeStream();
      unwrapModelResumeStream();

      expect(Model.prototype.resumeStream).toBe(originalResumeStream);
    });
  });

  describe("wrapModelContextResume / unwrapModelContextResume", () => {
    it("replaces Model.prototype.contextResume", () => {
      expect(Model.prototype.contextResume).toBe(originalContextResume);

      wrapModelContextResume();

      expect(Model.prototype.contextResume).not.toBe(originalContextResume);
    });

    it("restores original on unwrap", () => {
      wrapModelContextResume();
      unwrapModelContextResume();

      expect(Model.prototype.contextResume).toBe(originalContextResume);
    });
  });

  describe("wrapModelContextResumeStream / unwrapModelContextResumeStream", () => {
    it("replaces Model.prototype.contextResumeStream", () => {
      expect(Model.prototype.contextResumeStream).toBe(
        originalContextResumeStream,
      );

      wrapModelContextResumeStream();

      expect(Model.prototype.contextResumeStream).not.toBe(
        originalContextResumeStream,
      );
    });

    it("restores original on unwrap", () => {
      wrapModelContextResumeStream();
      unwrapModelContextResumeStream();

      expect(Model.prototype.contextResumeStream).toBe(
        originalContextResumeStream,
      );
    });
  });

  describe("wrapAllModelMethods / unwrapAllModelMethods", () => {
    it("wraps all model methods", () => {
      wrapAllModelMethods();

      expect(Model.prototype.call).not.toBe(originalCall);
      expect(Model.prototype.stream).not.toBe(originalStream);
      expect(Model.prototype.contextCall).not.toBe(originalContextCall);
      expect(Model.prototype.contextStream).not.toBe(originalContextStream);
      expect(Model.prototype.resume).not.toBe(originalResume);
      expect(Model.prototype.resumeStream).not.toBe(originalResumeStream);
      expect(Model.prototype.contextResume).not.toBe(originalContextResume);
      expect(Model.prototype.contextResumeStream).not.toBe(
        originalContextResumeStream,
      );
    });

    it("unwraps all model methods", () => {
      wrapAllModelMethods();
      unwrapAllModelMethods();

      expect(Model.prototype.call).toBe(originalCall);
      expect(Model.prototype.stream).toBe(originalStream);
      expect(Model.prototype.contextCall).toBe(originalContextCall);
      expect(Model.prototype.contextStream).toBe(originalContextStream);
      expect(Model.prototype.resume).toBe(originalResume);
      expect(Model.prototype.resumeStream).toBe(originalResumeStream);
      expect(Model.prototype.contextResume).toBe(originalContextResume);
      expect(Model.prototype.contextResumeStream).toBe(
        originalContextResumeStream,
      );
    });
  });

  describe("isModelInstrumented", () => {
    it("returns false when no methods are wrapped", () => {
      expect(isModelInstrumented()).toBe(false);
    });

    it("returns true when any method is wrapped", () => {
      wrapModelCall();
      expect(isModelInstrumented()).toBe(true);
    });

    it("returns true when all methods are wrapped", () => {
      wrapAllModelMethods();
      expect(isModelInstrumented()).toBe(true);
    });

    it("returns false after unwrapping all methods", () => {
      wrapAllModelMethods();
      unwrapAllModelMethods();
      expect(isModelInstrumented()).toBe(false);
    });
  });
});
