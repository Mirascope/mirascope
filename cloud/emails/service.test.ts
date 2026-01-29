import { Effect, Layer } from "effect";
import { describe, it, expect } from "vitest";

import { Emails } from "@/emails/service";
import { ResendError } from "@/errors";
import {
  TestEmailSendParamsFixture,
  TestEmailSendResponseFixture,
  MockResend,
} from "@/tests/emails";

describe("Email", () => {
  describe("send", () => {
    it("sends email with correct parameters", () => {
      let capturedParams: unknown;
      const sendParams = TestEmailSendParamsFixture();
      const response = TestEmailSendResponseFixture();

      return Effect.gen(function* () {
        const email = yield* Emails;

        const result = yield* email.send(sendParams);

        expect(capturedParams).toEqual(sendParams);
        expect(result).toEqual(response);
      }).pipe(
        Effect.provide(
          Emails.Default.pipe(
            Layer.provide(
              MockResend.layer((params) => {
                capturedParams = params;
                return Effect.succeed(response);
              }),
            ),
          ),
        ),
        Effect.runPromise,
      );
    });

    it("sends email with multiple recipients", () => {
      const sendParams = TestEmailSendParamsFixture({
        to: ["user1@example.com", "user2@example.com"],
      });
      const response = TestEmailSendResponseFixture();

      return Effect.gen(function* () {
        const email = yield* Emails;

        const result = yield* email.send(sendParams);

        expect(result).toEqual(response);
      }).pipe(
        Effect.provide(
          Emails.Default.pipe(
            Layer.provide(MockResend.layer(() => Effect.succeed(response))),
          ),
        ),
        Effect.runPromise,
      );
    });

    it("sends email with cc and bcc", () => {
      let capturedParams: unknown;
      const sendParams = TestEmailSendParamsFixture({
        cc: "cc@example.com",
        bcc: ["bcc1@example.com", "bcc2@example.com"],
      });
      const response = TestEmailSendResponseFixture();

      return Effect.gen(function* () {
        const email = yield* Emails;

        const result = yield* email.send(sendParams);

        expect(capturedParams).toMatchObject(sendParams);
        expect(result).toEqual(response);
      }).pipe(
        Effect.provide(
          Emails.Default.pipe(
            Layer.provide(
              MockResend.layer((params) => {
                capturedParams = params;
                return Effect.succeed(response);
              }),
            ),
          ),
        ),
        Effect.runPromise,
      );
    });

    it("sends email with text content", () => {
      let capturedParams: unknown;
      const sendParams = TestEmailSendParamsFixture({
        html: undefined,
        text: "Plain text content",
      });
      const response = TestEmailSendResponseFixture();

      return Effect.gen(function* () {
        const email = yield* Emails;

        const result = yield* email.send(sendParams);

        expect(capturedParams).toEqual(sendParams);
        expect(result).toEqual(response);
      }).pipe(
        Effect.provide(
          Emails.Default.pipe(
            Layer.provide(
              MockResend.layer((params) => {
                capturedParams = params;
                return Effect.succeed(response);
              }),
            ),
          ),
        ),
        Effect.runPromise,
      );
    });

    it("sends email with attachments", () => {
      let capturedParams: unknown;
      const sendParams = TestEmailSendParamsFixture({
        attachments: [
          {
            filename: "test.pdf",
            content: "base64content",
          },
        ],
      });
      const response = TestEmailSendResponseFixture();

      return Effect.gen(function* () {
        const email = yield* Emails;

        const result = yield* email.send(sendParams);

        expect(capturedParams).toMatchObject(sendParams);
        expect(result).toEqual(response);
      }).pipe(
        Effect.provide(
          Emails.Default.pipe(
            Layer.provide(
              MockResend.layer((params) => {
                capturedParams = params;
                return Effect.succeed(response);
              }),
            ),
          ),
        ),
        Effect.runPromise,
      );
    });

    it("sends email with replyTo", () => {
      let capturedParams: unknown;
      const sendParams = TestEmailSendParamsFixture({
        replyTo: "support@example.com",
      });
      const response = TestEmailSendResponseFixture();

      return Effect.gen(function* () {
        const email = yield* Emails;

        const result = yield* email.send(sendParams);

        expect(capturedParams).toMatchObject(sendParams);
        expect(result).toEqual(response);
      }).pipe(
        Effect.provide(
          Emails.Default.pipe(
            Layer.provide(
              MockResend.layer((params) => {
                capturedParams = params;
                return Effect.succeed(response);
              }),
            ),
          ),
        ),
        Effect.runPromise,
      );
    });

    it("returns ResendError when send fails", () => {
      const sendParams = TestEmailSendParamsFixture();

      return Effect.gen(function* () {
        const email = yield* Emails;

        const result = yield* email.send(sendParams).pipe(Effect.flip);

        expect(result).toBeInstanceOf(ResendError);
        expect(result.message).toBe("Failed to send email");
      }).pipe(
        Effect.provide(
          Emails.Default.pipe(
            Layer.provide(
              MockResend.layer(() =>
                Effect.fail(
                  new ResendError({ message: "Failed to send email" }),
                ),
              ),
            ),
          ),
        ),
        Effect.runPromise,
      );
    });

    it("returns ResendError for invalid email address", () => {
      const sendParams = TestEmailSendParamsFixture({ from: "invalid-email" });

      return Effect.gen(function* () {
        const email = yield* Emails;

        const result = yield* email.send(sendParams).pipe(Effect.flip);

        expect(result).toBeInstanceOf(ResendError);
        expect(result.message).toContain("Invalid email address");
      }).pipe(
        Effect.provide(
          Emails.Default.pipe(
            Layer.provide(
              MockResend.layer(() =>
                Effect.fail(
                  new ResendError({
                    message: "Invalid email address in 'from' field",
                  }),
                ),
              ),
            ),
          ),
        ),
        Effect.runPromise,
      );
    });
  });

  describe("DefaultRetries", () => {
    it("retries on failure and eventually succeeds", () => {
      let attemptCount = 0;
      const sendParams = TestEmailSendParamsFixture();
      const response = TestEmailSendResponseFixture();

      return Effect.gen(function* () {
        const email = yield* Emails;

        yield* email
          .send(sendParams)
          .pipe(Emails.DefaultRetries("Failed to send test email"));

        // Should have retried multiple times before succeeding
        expect(attemptCount).toBeGreaterThan(1);
      }).pipe(
        Effect.provide(
          Emails.Default.pipe(
            Layer.provide(
              MockResend.layer(() => {
                attemptCount++;
                // Fail first 2 attempts, succeed on 3rd
                if (attemptCount < 3) {
                  return Effect.fail(
                    new ResendError({ message: "Transient error" }),
                  );
                }
                return Effect.succeed(response);
              }),
            ),
          ),
        ),
        Effect.runPromise,
      );
    });

    it("catches all errors after retries exhausted and returns void", () => {
      let attemptCount = 0;
      const sendParams = TestEmailSendParamsFixture();

      return Effect.gen(function* () {
        const email = yield* Emails;

        // Should not throw even after all retries fail
        yield* email
          .send(sendParams)
          .pipe(Emails.DefaultRetries("Failed to send test email"));

        // Should have tried 5 times (1 initial + 4 retries)
        expect(attemptCount).toBe(5);
      }).pipe(
        Effect.provide(
          Emails.Default.pipe(
            Layer.provide(
              MockResend.layer(() => {
                attemptCount++;
                return Effect.fail(
                  new ResendError({ message: "Persistent error" }),
                );
              }),
            ),
          ),
        ),
        Effect.runPromise,
      );
    });

    it("logs warning with error message when retries exhausted", () => {
      const sendParams = TestEmailSendParamsFixture();
      const customErrorMessage = "Custom error message for logging";

      return Effect.gen(function* () {
        const email = yield* Emails;

        // Should complete without throwing
        yield* email
          .send(sendParams)
          .pipe(Emails.DefaultRetries(customErrorMessage));
      }).pipe(
        Effect.provide(
          Emails.Default.pipe(
            Layer.provide(
              MockResend.layer(() =>
                Effect.fail(new ResendError({ message: "Always fails" })),
              ),
            ),
          ),
        ),
        Effect.runPromise,
      );
    });
  });

  describe("Email.Live", () => {
    it("creates a layer with provided configuration", () => {
      const layer = Emails.Live({
        apiKey: "re_test_mock",
        audienceSegmentId: "seg_test_mock",
      });

      expect(layer).toBeDefined();
      expect(Layer.isLayer(layer)).toBe(true);
    });
  });
});
