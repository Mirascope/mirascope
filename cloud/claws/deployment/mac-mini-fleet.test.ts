/**
 * @fileoverview Tests for the Mac Mini fleet service.
 */

import { describe, it, expect } from "@effect/vitest";
import { Effect, Layer } from "effect";

import { ClawDeploymentError } from "@/claws/deployment/errors";
import {
  MacMiniFleetService,
  type MacMiniFleetServiceInterface,
} from "@/claws/deployment/mac-mini-fleet";

describe("MacMiniFleetService", () => {
  describe("findAvailableMini", () => {
    it.effect("returns a mini with available capacity", () =>
      Effect.gen(function* () {
        const fleet = yield* MacMiniFleetService;
        const result = yield* fleet.findAvailableMini();

        expect(result.miniId).toBe("mini-1");
        expect(result.agentUrl).toBe("https://agent.mini1.example.com");
        expect(result.port).toBe(3001);
        expect(result.tunnelHostnameSuffix).toBe("claws.example.com");
      }).pipe(
        Effect.provide(
          Layer.succeed(MacMiniFleetService, {
            findAvailableMini: () =>
              Effect.succeed({
                miniId: "mini-1",
                agentUrl: "https://agent.mini1.example.com",
                port: 3001,
                tunnelHostnameSuffix: "claws.example.com",
              }),
            callAgent: () => Effect.succeed(null),
          }),
        ),
      ),
    );

    it.effect("fails when no minis are available", () =>
      Effect.gen(function* () {
        const fleet = yield* MacMiniFleetService;
        const result = yield* fleet.findAvailableMini().pipe(
          Effect.flip,
        );

        expect(result).toBeInstanceOf(ClawDeploymentError);
        expect(result.message).toContain("No Mac Minis available");
      }).pipe(
        Effect.provide(
          Layer.succeed(MacMiniFleetService, {
            findAvailableMini: () =>
              Effect.fail(
                new ClawDeploymentError({
                  message: "No Mac Minis available with capacity",
                }),
              ),
            callAgent: () => Effect.succeed(null),
          }),
        ),
      ),
    );
  });

  describe("callAgent", () => {
    it.effect("makes HTTP request and returns response", () =>
      Effect.gen(function* () {
        const fleet = yield* MacMiniFleetService;
        const result = yield* fleet.callAgent(
          "mini-1",
          "GET",
          "/claws/test/status",
        );

        expect(result).toEqual({ status: "running" });
      }).pipe(
        Effect.provide(
          Layer.succeed(MacMiniFleetService, {
            findAvailableMini: () =>
              Effect.fail(
                new ClawDeploymentError({ message: "not implemented" }),
              ),
            callAgent: (_miniId, _method, _path) =>
              Effect.succeed({ status: "running" }),
          }),
        ),
      ),
    );
  });
});
