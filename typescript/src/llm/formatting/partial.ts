/**
 * Deep partial type for streaming structured outputs.
 *
 * Used when parsing incomplete JSON during structured streaming,
 * where fields arrive incrementally.
 */

/**
 * Deep partial type - all properties become optional recursively.
 *
 * This type is used for streaming structured outputs where fields
 * arrive incrementally. During streaming, the parsed output may
 * not have all fields populated yet.
 *
 * @template T - The original type to make deeply partial.
 *
 * @example
 * ```typescript
 * interface Book {
 *   title: string;
 *   author: string;
 *   chapters: { name: string; pages: number }[];
 * }
 *
 * // DeepPartial<Book> =
 * // {
 * //   title?: string | null;
 * //   author?: string | null;
 * //   chapters?: ({ name?: string | null; pages?: number | null } | null)[] | null;
 * // }
 *
 * // During streaming:
 * for await (const partial of response.structuredStream()) {
 *   // partial.title may be undefined at first
 *   if (partial.title) {
 *     console.log('Got title:', partial.title);
 *   }
 * }
 * ```
 */
export type DeepPartial<T> = T extends (infer U)[]
  ? (DeepPartial<U> | null)[] | null
  : T extends object
    ? { [P in keyof T]?: DeepPartial<T[P]> | null }
    : T | null;
