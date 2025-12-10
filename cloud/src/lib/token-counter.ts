import { encodingForModel } from "js-tiktoken";

/**
 * Token counter utility using OpenAI's tiktoken
 */

// Cache the encoder to avoid recreating it
let encoder: ReturnType<typeof encodingForModel> | null = null;

function getEncoder() {
  if (!encoder) {
    // Use gpt-4 encoding (cl100k_base) which is the most common
    encoder = encodingForModel("gpt-4");
  }
  return encoder;
}

/**
 * Count tokens in text using OpenAI's tiktoken
 * @param text - The text to count tokens for
 * @returns Number of tokens
 */
export function countTokens(text: string): number {
  try {
    const enc = getEncoder();
    const tokens = enc.encode(text);
    return tokens.length;
  } catch (error) {
    console.warn(
      "Token counting failed, falling back to approximation:",
      error,
    );
    // Fallback to rough approximation
    return Math.ceil(text.length / 4);
  }
}

/**
 * Format token count with locale-appropriate thousands separators
 * @param count - Token count
 * @returns Formatted string
 */
export function formatTokenCount(count: number): string {
  return count.toLocaleString();
}
