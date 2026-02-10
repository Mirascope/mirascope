/**
 * URL construction helpers for slug-based cloud routes.
 */

export function orgRoute(orgSlug: string) {
  return `/${orgSlug}`;
}

export function clawsRoute(orgSlug: string) {
  return `/${orgSlug}/claws`;
}

export function clawChatRoute(orgSlug: string, clawSlug: string) {
  return `/${orgSlug}/claws/${clawSlug}/chat`;
}

export function clawSecretsRoute(orgSlug: string, clawSlug: string) {
  return `/${orgSlug}/claws/${clawSlug}/secrets`;
}

export function projectsRoute(orgSlug: string) {
  return `/${orgSlug}/projects`;
}

export function projectEnvRoute(
  orgSlug: string,
  projectSlug: string,
  envSlug: string,
) {
  return `/${orgSlug}/projects/${projectSlug}/${envSlug}`;
}

export function projectEnvSubRoute(
  orgSlug: string,
  projectSlug: string,
  envSlug: string,
  sub: string,
) {
  return `/${orgSlug}/projects/${projectSlug}/${envSlug}/${sub}`;
}

export function settingsRoute(orgSlug: string, sub?: string) {
  if (sub) {
    return `/${orgSlug}/settings/${sub}`;
  }
  return `/${orgSlug}/settings`;
}
