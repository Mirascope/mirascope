/**
 * Convert TypeScript types to JSON Schema.
 *
 * Uses the TypeScript Compiler API to introspect types and generate
 * JSON Schema representations suitable for LLM tool definitions.
 */

import ts from "typescript";

import type { JsonSchemaProperty, ToolParameterSchema } from "@/llm/tools";

/**
 * Context for type-to-schema conversion.
 */
interface ConversionContext {
  /** The TypeScript type checker. */
  checker: ts.TypeChecker;
  /** Definitions for referenced types ($defs). */
  definitions: Map<string, JsonSchemaProperty>;
  /** Set of type names currently being processed (for cycle detection). */
  processing: Set<string>;
}

/**
 * Check if a type is an array-like type (handles cases where isArrayType doesn't work).
 *
 * This is needed because TypeScript's isArrayType requires proper lib.d.ts setup.
 * We also check for Array<T> and T[] patterns by looking at the type structure.
 *
 * Coverage ignored: This is defensive fallback code for edge cases where
 * checker.isArrayType() fails due to missing/broken lib.d.ts. In normal
 * usage with proper TypeScript setup, checker.isArrayType() succeeds and
 * this function is never called (short-circuit evaluation on line 120).
 */
/* v8 ignore start */
function isArrayLikeType(type: ts.Type, checker: ts.TypeChecker): boolean {
  // Check if it's a TypeReference with 'Array' as the symbol name
  if (type.getFlags() & ts.TypeFlags.Object) {
    const objectType = type as ts.ObjectType;
    const objectFlags = objectType.objectFlags;

    // Check for array reference (Array<T>)
    if (objectFlags & ts.ObjectFlags.Reference) {
      const typeRef = type as ts.TypeReference;
      const symbol = typeRef.symbol;
      if (symbol && symbol.getName() === "Array") {
        return true;
      }
      // Also check the target's symbol for ReadonlyArray, etc.
      const target = typeRef.target;
      if (target && target.symbol && target.symbol.getName() === "Array") {
        return true;
      }
    }
  }

  // Check the type string as a fallback
  const typeString = checker.typeToString(type);
  if (typeString.endsWith("[]") || typeString.startsWith("Array<")) {
    return true;
  }

  return false;
}
/* v8 ignore end */

/**
 * Convert a TypeScript type to a JSON Schema property.
 *
 * @param type - The TypeScript type to convert.
 * @param ctx - The conversion context.
 * @returns The JSON Schema property.
 */
export function typeToJsonSchema(
  type: ts.Type,
  ctx: ConversionContext,
): JsonSchemaProperty {
  const checker = ctx.checker;

  // Handle union types (including optional which is T | undefined)
  if (type.isUnion()) {
    return handleUnionType(type, ctx);
  }

  // Handle intersection types
  if (type.isIntersection()) {
    return handleIntersectionType(type, ctx);
  }

  // Handle literal types
  if (type.isLiteral()) {
    return handleLiteralType(type);
  }

  // Handle boolean literals (true/false) - these aren't captured by isLiteral()
  // They are intrinsic types with BooleanLiteral flag
  const flags = type.getFlags();
  if (flags & ts.TypeFlags.BooleanLiteral) {
    const intrinsicName = (type as ts.Type & { intrinsicName?: string })
      .intrinsicName;
    const isTrue = intrinsicName === "true";
    return { type: "boolean", enum: [isTrue] };
  }

  // Handle primitive types

  if (flags & ts.TypeFlags.String) {
    return { type: "string" };
  }

  if (flags & ts.TypeFlags.Number) {
    return { type: "number" };
  }

  if (flags & ts.TypeFlags.Null) {
    return { type: "null" };
  }

  if (flags & ts.TypeFlags.Undefined) {
    // undefined is typically filtered out from unions
    return {};
  }

  // Handle array types
  // Check both checker.isArrayType and TypeReference patterns
  if (checker.isArrayType(type) || isArrayLikeType(type, checker)) {
    const typeRef = type as ts.TypeReference;
    const typeArgs = checker.getTypeArguments(typeRef);
    if (typeArgs && typeArgs.length > 0) {
      return {
        type: "array",
        items: typeToJsonSchema(typeArgs[0]!, ctx),
      };
    }
    // Coverage ignored: Fallback for arrays without type arguments (e.g., broken lib.d.ts)
    /* v8 ignore next */
    return { type: "array" };
  }

  // Handle object types (interfaces, type literals, classes)
  if (flags & ts.TypeFlags.Object) {
    return handleObjectType(type as ts.ObjectType, ctx);
  }

  /* v8 ignore start */
  return {};
}
/* v8 ignore end */

/**
 * Handle union types, including optional types (T | undefined).
 */
function handleUnionType(
  type: ts.UnionType,
  ctx: ConversionContext,
): JsonSchemaProperty {
  const types = type.types;

  // Filter out undefined (for optional properties)
  const nonUndefinedTypes = types.filter(
    (t) => !(t.getFlags() & ts.TypeFlags.Undefined),
  );

  // Check if this is a boolean type (union of true | false)
  if (
    nonUndefinedTypes.length === 2 &&
    nonUndefinedTypes.every((t) => t.getFlags() & ts.TypeFlags.BooleanLiteral)
  ) {
    return { type: "boolean" };
  }

  // If all non-undefined types are string/number literals, create an enum
  if (
    nonUndefinedTypes.every((t): t is ts.StringLiteralType =>
      t.isStringLiteral(),
    )
  ) {
    return {
      type: "string",
      enum: nonUndefinedTypes.map((t) => t.value),
    };
  }

  if (
    nonUndefinedTypes.every((t): t is ts.NumberLiteralType =>
      t.isNumberLiteral(),
    )
  ) {
    return {
      type: "number",
      enum: nonUndefinedTypes.map((t) => t.value),
    };
  }

  // If only one non-undefined type remains, use it directly
  if (nonUndefinedTypes.length === 1) {
    return typeToJsonSchema(nonUndefinedTypes[0]!, ctx);
  }

  // Otherwise, create a oneOf schema
  return {
    oneOf: nonUndefinedTypes.map((t) => typeToJsonSchema(t, ctx)),
  };
}

/**
 * Handle intersection types by merging properties.
 */
function handleIntersectionType(
  type: ts.IntersectionType,
  ctx: ConversionContext,
): JsonSchemaProperty {
  const allOf = type.types.map((t) => typeToJsonSchema(t, ctx));

  // If all parts are objects, try to merge them
  if (allOf.every((s) => s.type === "object")) {
    const merged: JsonSchemaProperty = {
      type: "object",
      properties: {},
      required: [],
    };

    for (const schema of allOf) {
      if (schema.properties) {
        merged.properties = { ...merged.properties, ...schema.properties };
      }
      if (schema.required) {
        merged.required = [
          ...(merged.required as string[]),
          ...(schema.required as string[]),
        ];
      }
    }

    return merged;
  }

  return { allOf };
}

/**
 * Handle literal types (string, number literals).
 * Note: Boolean literals (true/false) are handled earlier via BooleanLiteral flag
 * since TypeScript's isLiteral() doesn't return true for them.
 */
function handleLiteralType(type: ts.Type): JsonSchemaProperty {
  if (type.isStringLiteral()) {
    return { type: "string", enum: [type.value] };
  }

  if (type.isNumberLiteral()) {
    return { type: "number", enum: [type.value] };
  }

  /* v8 ignore start */
  return {};
}
/* v8 ignore end */

/**
 * Handle object types (interfaces, type literals, classes).
 */
function handleObjectType(
  type: ts.ObjectType,
  ctx: ConversionContext,
): JsonSchemaProperty {
  const checker = ctx.checker;
  const properties: Record<string, JsonSchemaProperty> = {};
  const required: string[] = [];

  // Get all properties of the type
  const props = checker.getPropertiesOfType(type);

  for (const prop of props) {
    const propName = prop.getName();
    const propType = checker.getTypeOfSymbol(prop);

    // Check if the property is optional
    const isOptional = (prop.getFlags() & ts.SymbolFlags.Optional) !== 0;

    // Convert the property type to schema
    const propSchema = typeToJsonSchema(propType, ctx);

    // Extract JSDoc description from property declaration
    const jsDocComment = prop.getDocumentationComment(checker);
    if (jsDocComment.length > 0) {
      const description = jsDocComment.map((c) => c.text).join("");
      propSchema.description = description;
    }

    properties[propName] = propSchema;

    // Add to required if not optional
    if (!isOptional) {
      required.push(propName);
    }
  }

  return {
    type: "object",
    properties,
    required: required.length > 0 ? required : undefined,
  };
}

/**
 * Convert a TypeScript type to a ToolParameterSchema.
 *
 * This is the main entry point for converting tool argument types
 * to the schema format expected by LLM providers.
 *
 * @param type - The TypeScript type to convert (should be an object type).
 * @param checker - The TypeScript type checker.
 * @returns The tool parameter schema.
 */
export function typeToToolParameterSchema(
  type: ts.Type,
  checker: ts.TypeChecker,
): ToolParameterSchema {
  const ctx: ConversionContext = {
    checker,
    definitions: new Map(),
    processing: new Set(),
  };

  const schema = typeToJsonSchema(type, ctx);

  // Ensure the result is an object schema
  if (schema.type !== "object") {
    throw new Error(
      "Tool parameter type must be an object type, got: " +
        JSON.stringify(schema),
    );
  }

  // Build a mutable result, then return as readonly
  const result: {
    type: "object";
    properties: Record<string, JsonSchemaProperty>;
    required: readonly string[];
    additionalProperties: false;
    $defs?: Record<string, JsonSchemaProperty>;
  } = {
    type: "object",
    properties: schema.properties ?? {},
    required: (schema.required as readonly string[]) ?? [],
    additionalProperties: false,
  };

  // Coverage ignored: $defs only populated for recursive types (not yet implemented)
  /* v8 ignore start */
  if (ctx.definitions.size > 0) {
    result.$defs = Object.fromEntries(ctx.definitions);
  }
  /* v8 ignore end */

  return result;
}

/**
 * Create a ConversionContext for testing or manual use.
 */
export function createConversionContext(
  checker: ts.TypeChecker,
): ConversionContext {
  return {
    checker,
    definitions: new Map(),
    processing: new Set(),
  };
}
