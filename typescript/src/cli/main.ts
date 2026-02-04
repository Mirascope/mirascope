#!/usr/bin/env bun
/**
 * Mirascope CLI - Command-line interface.
 */

import { defineCommand, runMain } from "citty";

import { app as registryApp } from "@/cli/registry/app";

const app = defineCommand({
  meta: {
    name: "mirascope",
    version: "2.1.1",
    description: "Mirascope CLI",
  },
  subCommands: {
    registry: registryApp,
  },
});

void runMain(app);
