/** Read cache-write usage from SDK versions that may not declare the field. */
export function cacheWriteTokens(details: object | null | undefined): number {
  if (!details || !("cache_write_tokens" in details)) {
    return 0;
  }
  return typeof details.cache_write_tokens === "number"
    ? details.cache_write_tokens
    : 0;
}
