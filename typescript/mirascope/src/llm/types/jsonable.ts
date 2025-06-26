/**
 * Typing for JSON serializable objects.
 */

/**
 * Interface for JSON-serializable objects.
 *
 * This interface defines the contract for objects that can be serialized to
 * JSON. It is used in the `Jsonable` type definition.
 */
export interface JsonableObject {
  /**
   * Serialize the object as a JSON string.
   */
  json(): string;
}

/**
 * Type alias for JSON-serializable types.
 *
 * This recursive type represents all values that can be safely serialized
 * to JSON, including:
 * - Primitive types: null, string, number, boolean
 * - Arrays of Jsonable values
 * - Objects with string keys and Jsonable values
 * - Objects implementing the JsonableObject interface
 */
export type Jsonable =
  | null
  | string
  | number
  | boolean
  | Jsonable[]
  | { [key: string]: Jsonable }
  | JsonableObject;
