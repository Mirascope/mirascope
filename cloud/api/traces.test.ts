import { Effect } from "effect";
import { describe, expect, TestApiContext } from "@/tests/api";
import type { PublicProject, PublicEnvironment } from "@/db/schema";

describe.sequential("Traces API", (it) => {
  let project: PublicProject;
  let environment: PublicEnvironment;

  it.effect(
    "POST /organizations/:orgId/projects - create project for traces test",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        project = yield* client.projects.create({
          path: { organizationId: org.id },
          payload: { name: "Traces Test Project", slug: "traces-test-project" },
        });
        expect(project.id).toBeDefined();
      }),
  );

  it.effect(
    "POST /organizations/:orgId/projects/:projId/environments - create environment for traces test",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        environment = yield* client.environments.create({
          path: { organizationId: org.id, projectId: project.id },
          payload: { name: "Traces Test Environment", slug: "traces-test-env" },
        });
        expect(environment.id).toBeDefined();
      }),
  );

  it.effect(
    "POST /organizations/:orgId/projects/:projId/environments/:envId/traces - creates trace",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const payload = {
          resourceSpans: [
            {
              resource: {
                attributes: [
                  {
                    key: "service.name",
                    value: {
                      stringValue: "test-service",
                    },
                  },
                ],
              },
              scopeSpans: [
                {
                  scope: {
                    name: "test-scope",
                    version: "1.0.0",
                  },
                  spans: [
                    {
                      traceId: "test-trace-id",
                      spanId: "test-span-id",
                      name: "test-span",
                      startTimeUnixNano: "1000000000",
                      endTimeUnixNano: "2000000000",
                    },
                  ],
                },
              ],
            },
          ],
        };

        const result = yield* client.traces.create({
          path: {
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
          },
          payload,
        });

        expect(result.partialSuccess).toBeDefined();
      }),
  );
});
