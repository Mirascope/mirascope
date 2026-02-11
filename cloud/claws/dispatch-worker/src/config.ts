/** Port that the OpenClaw gateway listens on inside the container */
export const GATEWAY_PORT = 18789;

/** Maximum time to wait for gateway startup (3 minutes) */
export const STARTUP_TIMEOUT_MS = 180_000;

/** Mount path for R2 persistent storage inside the container */
export const R2_MOUNT_PATH = "/data/claw";
