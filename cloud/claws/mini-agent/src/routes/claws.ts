/**
 * CRUD endpoints for claw provisioning.
 */
import { Hono } from "hono";

import type { AgentConfig } from "../lib/config.js";

import { errorMessage } from "../lib/errors.js";
import * as launchd from "../services/launchd.js";
import * as monitoring from "../services/monitoring.js";
import * as provisioning from "../services/provisioning.js";

export function clawRoutes(config: AgentConfig): Hono {
  const app = new Hono();

  // POST /claws — Provision a new claw
  app.post("/claws", async (c) => {
    try {
      const body = await c.req.json();

      // Validate required fields
      const required = [
        "clawId",
        "macUsername",
        "localPort",
        "gatewayToken",
        "tunnelHostname",
      ];
      for (const field of required) {
        if (!body[field]) {
          return c.json({ error: `Missing required field: ${field}` }, 400);
        }
      }

      // Validate port is in allowed range
      if (
        body.localPort < config.portRangeStart ||
        body.localPort > config.portRangeEnd
      ) {
        return c.json(
          {
            error: `Port ${body.localPort} is outside allowed range ${config.portRangeStart}-${config.portRangeEnd}`,
          },
          400,
        );
      }

      // Validate macUsername format
      if (!/^claw-[a-z0-9]+$/.test(body.macUsername)) {
        return c.json(
          { error: "macUsername must match pattern: claw-[a-z0-9]+" },
          400,
        );
      }

      // Check capacity
      const existingClaws = await provisioning.listClawUsers();
      if (existingClaws.length >= config.maxClaws) {
        return c.json(
          {
            error: "Mini is at capacity",
            details: `${existingClaws.length}/${config.maxClaws} claws`,
          },
          503,
        );
      }

      const result = await provisioning.provision(
        {
          clawId: body.clawId,
          macUsername: body.macUsername,
          localPort: body.localPort,
          gatewayToken: body.gatewayToken,
          tunnelHostname: body.tunnelHostname,
          envVars: body.envVars ?? {},
        },
        config,
      );

      if (!result.success) {
        return c.json(
          { error: "Provisioning failed", details: result.error },
          500,
        );
      }

      return c.json(result, 201);
    } catch (error: unknown) {
      return c.json(
        { error: "Provisioning failed", details: errorMessage(error) },
        500,
      );
    }
  });

  // GET /claws — List all claws
  app.get("/claws", async (c) => {
    try {
      const clawUsers = await provisioning.listClawUsers();
      const claws = await Promise.all(
        clawUsers.map(async (macUsername) => {
          const resources = await monitoring.getClawResources(macUsername);
          const status = await launchd.getStatus(macUsername);
          return {
            macUsername,
            launchdStatus: status,
            ...resources,
          };
        }),
      );
      return c.json({ claws });
    } catch (error: unknown) {
      return c.json(
        { error: "Failed to list claws", details: errorMessage(error) },
        500,
      );
    }
  });

  // GET /claws/:clawUser/status — Get claw status
  app.get("/claws/:clawUser/status", async (c) => {
    const macUsername = c.req.param("clawUser");

    try {
      const exists = await userExists(macUsername);
      if (!exists) {
        return c.json({ error: `Claw user ${macUsername} not found` }, 404);
      }

      const [resources, status, diskMb] = await Promise.all([
        monitoring.getClawResources(macUsername),
        launchd.getStatus(macUsername),
        monitoring.getClawDiskUsage(macUsername),
      ]);

      return c.json({
        macUsername,
        launchdStatus: status,
        diskMb,
        ...resources,
      });
    } catch (error: unknown) {
      return c.json(
        { error: "Failed to get status", details: errorMessage(error) },
        500,
      );
    }
  });

  // POST /claws/:clawUser/restart — Restart gateway
  app.post("/claws/:clawUser/restart", async (c) => {
    const macUsername = c.req.param("clawUser");

    try {
      const exists = await userExists(macUsername);
      if (!exists) {
        return c.json({ error: `Claw user ${macUsername} not found` }, 404);
      }

      await launchd.restart(macUsername);
      const pid = await launchd.getPid(macUsername);
      return c.json({ success: true, gatewayPid: pid });
    } catch (error: unknown) {
      return c.json(
        { error: "Failed to restart gateway", details: errorMessage(error) },
        500,
      );
    }
  });

  // DELETE /claws/:clawUser — Deprovision a claw
  app.delete("/claws/:clawUser", async (c) => {
    const macUsername = c.req.param("clawUser");

    try {
      const exists = await userExists(macUsername);
      if (!exists) {
        return c.json({ error: `Claw user ${macUsername} not found` }, 404);
      }

      let body: provisioning.DeprovisionRequest = {};
      try {
        body = await c.req.json();
      } catch {
        // No body is fine
      }

      const result = await provisioning.deprovision(macUsername, config, body);

      if (!result.success) {
        return c.json(
          { error: "Deprovisioning failed", details: result.error },
          500,
        );
      }

      return c.json(result);
    } catch (error: unknown) {
      return c.json(
        { error: "Deprovisioning failed", details: errorMessage(error) },
        500,
      );
    }
  });

  // POST /claws/:clawUser/backup — Trigger R2 backup
  app.post("/claws/:clawUser/backup", async (c) => {
    const macUsername = c.req.param("clawUser");

    try {
      const exists = await userExists(macUsername);
      if (!exists) {
        return c.json({ error: `Claw user ${macUsername} not found` }, 404);
      }

      // TODO: Implement actual R2 backup
      const backupId = `backup-${Date.now()}`;
      console.log(
        `[backup] Triggered backup ${backupId} for ${macUsername} (not yet implemented)`,
      );

      return c.json({ success: true, backupId }, 202);
    } catch (error: unknown) {
      return c.json(
        { error: "Backup failed", details: errorMessage(error) },
        500,
      );
    }
  });

  return app;
}

/** Check if a claw user exists via dscl */
async function userExists(macUsername: string): Promise<boolean> {
  const { exec } = await import("../lib/exec.js");
  const result = await exec("id", [macUsername]);
  return result.exitCode === 0;
}
