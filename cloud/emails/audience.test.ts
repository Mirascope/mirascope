import { describe, it, expect } from "vitest";
import { Effect, Layer } from "effect";
import { ResendError } from "@/errors";
import { Emails } from "@/emails/service";
import {
  TestAudienceAddParamsFixture,
  TestAudienceAddResponseFixture,
  MockResendAudience,
} from "@/tests/emails";

describe("Audience", () => {
  describe("add", () => {
    it("creates contact and adds to audience segment with correct parameters", () => {
      let capturedCreateParams: unknown;
      let capturedAddParams: unknown;
      const expectedParams = TestAudienceAddParamsFixture();
      const response = TestAudienceAddResponseFixture();

      return Effect.gen(function* () {
        const emails = yield* Emails;

        const result = yield* emails.audience.add("user@example.com");

        expect(capturedCreateParams).toEqual({ email: "user@example.com" });
        expect(capturedAddParams).toEqual(expectedParams);
        expect(result).toEqual(response);
      }).pipe(
        Effect.provide(
          Emails.Default.pipe(
            Layer.provide(
              MockResendAudience.layer(
                (params) => {
                  capturedAddParams = params;
                  return Effect.succeed(response);
                },
                "seg_test_mock",
                (params) => {
                  capturedCreateParams = params;
                  return Effect.succeed({
                    id: "contact_123",
                    object: "contact",
                  });
                },
              ),
            ),
          ),
        ),
        Effect.runPromise,
      );
    });

    it("continues to add to segment when contact already exists", () => {
      let segmentAddCalled = false;
      const response = TestAudienceAddResponseFixture();

      return Effect.gen(function* () {
        const emails = yield* Emails;

        const result = yield* emails.audience.add("user@example.com");

        expect(segmentAddCalled).toBe(true);
        expect(result).toEqual(response);
      }).pipe(
        Effect.provide(
          Emails.Default.pipe(
            Layer.provide(
              MockResendAudience.layer(
                () => {
                  segmentAddCalled = true;
                  return Effect.succeed(response);
                },
                "seg_test_mock",
                () =>
                  Effect.fail(
                    new ResendError({ message: "Contact already exists" }),
                  ),
              ),
            ),
          ),
        ),
        Effect.runPromise,
      );
    });

    it("propagates error when contact creation fails for non-duplicate reasons", () => {
      return Effect.gen(function* () {
        const emails = yield* Emails;

        const result = yield* emails.audience
          .add("user@example.com")
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(ResendError);
        expect(result.message).toBe("Rate limit exceeded");
      }).pipe(
        Effect.provide(
          Emails.Default.pipe(
            Layer.provide(
              MockResendAudience.layer(
                () => Effect.succeed({ id: "contact_123" }),
                "seg_test_mock",
                () =>
                  Effect.fail(
                    new ResendError({ message: "Rate limit exceeded" }),
                  ),
              ),
            ),
          ),
        ),
        Effect.runPromise,
      );
    });

    it("uses the configured segment ID", () => {
      let capturedSegmentId: string | undefined;
      const response = TestAudienceAddResponseFixture();

      return Effect.gen(function* () {
        const emails = yield* Emails;

        yield* emails.audience.add("user@example.com");

        expect(capturedSegmentId).toBe("seg_custom_123");
      }).pipe(
        Effect.provide(
          Emails.Default.pipe(
            Layer.provide(
              MockResendAudience.layer((params: { segmentId: string }) => {
                capturedSegmentId = params.segmentId;
                return Effect.succeed(response);
              }, "seg_custom_123"),
            ),
          ),
        ),
        Effect.runPromise,
      );
    });

    it("returns ResendError when add fails", () => {
      return Effect.gen(function* () {
        const emails = yield* Emails;

        const result = yield* emails.audience
          .add("user@example.com")
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(ResendError);
        expect(result.message).toBe("Failed to add contact to audience");
      }).pipe(
        Effect.provide(
          Emails.Default.pipe(
            Layer.provide(
              MockResendAudience.layer(() =>
                Effect.fail(
                  new ResendError({
                    message: "Failed to add contact to audience",
                  }),
                ),
              ),
            ),
          ),
        ),
        Effect.runPromise,
      );
    });

    it("returns ResendError for invalid email address", () => {
      return Effect.gen(function* () {
        const emails = yield* Emails;

        const result = yield* emails.audience
          .add("invalid-email")
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(ResendError);
        expect(result.message).toContain("Invalid email address");
      }).pipe(
        Effect.provide(
          Emails.Default.pipe(
            Layer.provide(
              MockResendAudience.layer(() =>
                Effect.fail(
                  new ResendError({
                    message: "Invalid email address format",
                  }),
                ),
              ),
            ),
          ),
        ),
        Effect.runPromise,
      );
    });

    it("handles multiple email additions", () => {
      const addedEmails: string[] = [];

      return Effect.gen(function* () {
        const emails = yield* Emails;

        yield* emails.audience.add("user1@example.com");
        yield* emails.audience.add("user2@example.com");
        yield* emails.audience.add("user3@example.com");

        expect(addedEmails).toEqual([
          "user1@example.com",
          "user2@example.com",
          "user3@example.com",
        ]);
      }).pipe(
        Effect.provide(
          Emails.Default.pipe(
            Layer.provide(
              MockResendAudience.layer((params: { email: string }) => {
                addedEmails.push(params.email);
                return Effect.succeed({
                  id: `contact_${addedEmails.length}`,
                });
              }),
            ),
          ),
        ),
        Effect.runPromise,
      );
    });
  });
});
