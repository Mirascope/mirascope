import { describe, it, expect } from "vitest";
import { Effect, Layer } from "effect";
import { ResendError } from "@/errors";
import { Emails } from "@/emails/service";
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

  describe("Email.Live", () => {
    it("creates a layer with provided configuration", () => {
      const layer = Emails.Live({
        apiKey: "re_test_mock",
      });

      expect(layer).toBeDefined();
      expect(Layer.isLayer(layer)).toBe(true);
    });
  });
});
