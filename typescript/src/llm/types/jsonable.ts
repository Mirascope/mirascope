/**
 * A type that represents JSON-serializable values.
 *
 * This includes primitives (null, string, number, boolean),
 * arrays of Jsonable values, and objects with string keys and Jsonable values.
 */
export type Jsonable =
  | null
  | string
  | number
  | boolean
  | readonly Jsonable[]
  | { readonly [key: string]: Jsonable };
