#!/usr/bin/env bun
/**
 * Mirascope CLI - Command-line interface.
 */

import { defineCommand, runMain } from 'citty';
import { app as registryApp } from '@/cli/registry/app';

const app = defineCommand({
  meta: {
    name: 'mirascope',
    version: '0.1.0',
    description: 'Mirascope CLI',
  },
  subCommands: {
    registry: registryApp,
  },
});

void runMain(app);
