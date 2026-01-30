/**
 * TypeScript transformer for injecting schemas into tool and format definitions.
 *
 * This transformer finds calls to `defineTool<T>()`, `defineContextTool<T, DepsT>()`,
 * and `defineFormat<T>()` and injects the `__schema` property with the JSON schema
 * generated from type T.
 */

import ts from "typescript";

import { typeToToolParameterSchema } from "./type-to-schema";

/**
 * Names of functions that should have schemas injected.
 */
const TOOL_FUNCTION_NAMES = new Set(["defineTool", "defineContextTool"]);

/**
 * Names of format functions that should have schemas injected.
 */
const FORMAT_FUNCTION_NAMES = new Set(["defineFormat"]);

/**
 * Create a TypeScript transformer that injects __schema into tool definitions.
 *
 * @param program - The TypeScript program.
 * @returns A transformer factory.
 */
export function createToolSchemaTransformer(
  program: ts.Program,
): ts.TransformerFactory<ts.SourceFile> {
  const checker = program.getTypeChecker();

  return (context: ts.TransformationContext) => {
    return (sourceFile: ts.SourceFile) => {
      const visitor = (node: ts.Node): ts.Node => {
        // Look for call expressions
        if (ts.isCallExpression(node)) {
          // Try tool transform first
          const toolTransformed = tryTransformToolCall(node, checker, context);
          if (toolTransformed) {
            return toolTransformed;
          }

          // Try format transform
          const formatTransformed = tryTransformFormatCall(
            node,
            checker,
            context,
          );
          if (formatTransformed) {
            return formatTransformed;
          }
        }

        // Continue visiting children
        return ts.visitEachChild(node, visitor, context);
      };

      return ts.visitNode(sourceFile, visitor) as ts.SourceFile;
    };
  };
}

/**
 * Try to transform a call expression if it's a tool definition.
 *
 * @param node - The call expression node.
 * @param checker - The type checker.
 * @param context - The transformation context.
 * @returns The transformed node, or undefined if not a tool definition.
 */
function tryTransformToolCall(
  node: ts.CallExpression,
  checker: ts.TypeChecker,
  context: ts.TransformationContext,
): ts.CallExpression | undefined {
  // Check if this is a call to defineTool or defineContextTool
  const functionName = getFunctionName(node);
  if (!functionName || !TOOL_FUNCTION_NAMES.has(functionName)) {
    return undefined;
  }

  // Get the type arguments (the generic parameter T)
  const typeArgs = node.typeArguments;
  if (!typeArgs || typeArgs.length === 0) {
    // No type arguments - can't generate schema
    return undefined;
  }

  // Get the first type argument (T for args type)
  const argsTypeNode = typeArgs[0]!;
  const argsType = checker.getTypeFromTypeNode(argsTypeNode);

  // Generate the schema from the type
  let schema;
  try {
    schema = typeToToolParameterSchema(argsType, checker);
  } catch {
    // If schema generation fails, leave the call unchanged
    return undefined;
  }

  // Get the first argument (the options object)
  const args = node.arguments;
  const firstArg = args[0];
  if (!firstArg || !ts.isObjectLiteralExpression(firstArg)) {
    return undefined;
  }

  const optionsObject = firstArg;

  // Check if __schema is already present
  const hasSchema = optionsObject.properties.some(
    (prop) =>
      ts.isPropertyAssignment(prop) &&
      ts.isIdentifier(prop.name) &&
      prop.name.text === "__schema",
  );

  if (hasSchema) {
    // Already has a schema, don't override
    return undefined;
  }

  // Create the __schema property
  const schemaProperty = createSchemaProperty(schema, context.factory);

  // Create a new options object with __schema added
  const newProperties = [...optionsObject.properties, schemaProperty];
  const newOptionsObject = context.factory.updateObjectLiteralExpression(
    optionsObject,
    newProperties,
  );

  // Create a new call expression with the updated options
  const newArgs = [newOptionsObject, ...args.slice(1)];
  return context.factory.updateCallExpression(
    node,
    node.expression,
    node.typeArguments,
    newArgs,
  );
}

/**
 * Try to transform a call expression if it's a format definition.
 *
 * For defineFormat<T>(options):
 * - If the options arg is an object literal, inject __schema from type T
 * - If __schema is already present, leave unchanged
 * - If options has a validator, the validator's schema is used at runtime
 *
 * @param node - The call expression node.
 * @param checker - The type checker.
 * @param context - The transformation context.
 * @returns The transformed node, or undefined if not a format definition.
 */
function tryTransformFormatCall(
  node: ts.CallExpression,
  checker: ts.TypeChecker,
  context: ts.TransformationContext,
): ts.CallExpression | undefined {
  // Check if this is a call to defineFormat
  const functionName = getFunctionName(node);
  if (!functionName || !FORMAT_FUNCTION_NAMES.has(functionName)) {
    return undefined;
  }

  // Get the type arguments (the generic parameter T)
  const typeArgs = node.typeArguments;
  if (!typeArgs || typeArgs.length === 0) {
    // No type arguments - can't generate schema
    return undefined;
  }

  // Get the first type argument (T for the output type)
  const outputTypeNode = typeArgs[0]!;
  const outputType = checker.getTypeFromTypeNode(outputTypeNode);

  // Get the first argument
  const args = node.arguments;
  const firstArg = args[0];
  if (!firstArg) {
    return undefined;
  }

  // If first arg is an object literal (FormatSpec), inject __schema
  if (ts.isObjectLiteralExpression(firstArg)) {
    const formatSpecObject = firstArg;

    // Check if __schema is already present
    const hasSchema = formatSpecObject.properties.some(
      (prop) =>
        ts.isPropertyAssignment(prop) &&
        ts.isIdentifier(prop.name) &&
        prop.name.text === "__schema",
    );

    if (hasSchema) {
      // Already has a schema, don't override
      return undefined;
    }

    // Generate the schema from the type
    let schema;
    try {
      schema = typeToToolParameterSchema(outputType, checker);
    } catch {
      // If schema generation fails, leave the call unchanged
      return undefined;
    }

    // Create the __schema property
    const schemaProperty = createSchemaProperty(schema, context.factory);

    // Create a new format spec object with __schema added
    const newProperties = [...formatSpecObject.properties, schemaProperty];
    const newFormatSpecObject = context.factory.updateObjectLiteralExpression(
      formatSpecObject,
      newProperties,
    );

    // Create a new call expression with the updated format spec
    const newArgs = [newFormatSpecObject, ...args.slice(1)];
    return context.factory.updateCallExpression(
      node,
      node.expression,
      node.typeArguments,
      newArgs,
    );
  }

  // If first arg is not an object literal (e.g., a Zod schema identifier),
  // leave unchanged - Zod schemas handle their own schema generation
  return undefined;
}

/**
 * Get the function name from a call expression.
 */
/* v8 ignore start */
function getFunctionName(node: ts.CallExpression): string | undefined {
  const expression = node.expression;

  // Direct call: defineTool(...)
  if (ts.isIdentifier(expression)) {
    return expression.text;
  }

  // Property access: llm.defineTool(...)
  if (ts.isPropertyAccessExpression(expression)) {
    return expression.name.text;
  }

  return undefined;
}
/* v8 ignore end */

/**
 * Create a __schema property assignment from a schema object.
 */
function createSchemaProperty(
  schema: object,
  factory: ts.NodeFactory,
): ts.PropertyAssignment {
  return factory.createPropertyAssignment(
    factory.createIdentifier("__schema"),
    jsonToAst(schema, factory),
  );
}

/**
 * Convert a JSON value to a TypeScript AST expression.
 *
 * Coverage notes: Some branches are ignored because JSON Schema values
 * are always one of: null, string, number, boolean, array, or object.
 * The ignored branches handle edge cases that can't occur with valid schemas.
 */
function jsonToAst(value: unknown, factory: ts.NodeFactory): ts.Expression {
  // Coverage ignored: JSON schemas from typeToToolParameterSchema never contain
  // top-level null/undefined values, but we handle them defensively
  /* v8 ignore start */
  if (value === null) {
    return factory.createNull();
  }
  if (value === undefined) {
    return factory.createIdentifier("undefined");
  }
  /* v8 ignore end */

  if (typeof value === "string") {
    return factory.createStringLiteral(value);
  }

  if (typeof value === "number") {
    return factory.createNumericLiteral(value);
  }

  if (typeof value === "boolean") {
    /* v8 ignore next */
    return value ? factory.createTrue() : factory.createFalse();
  }

  if (Array.isArray(value)) {
    return factory.createArrayLiteralExpression(
      value.map((item) => jsonToAst(item, factory)),
    );
  }

  if (typeof value === "object") {
    const properties = Object.entries(value).map(([key, val]) =>
      factory.createPropertyAssignment(
        factory.createIdentifier(key),
        jsonToAst(val, factory),
      ),
    );
    return factory.createObjectLiteralExpression(properties, true);
  }

  // Coverage ignored: After handling all JSON-valid types (null, undefined,
  // string, number, boolean, array, object), this is unreachable
  /* v8 ignore next */
  return factory.createIdentifier("undefined");
}

/**
 * Default export for ts-patch and other transformer loaders.
 */
export default function transformer(
  program: ts.Program,
): ts.TransformerFactory<ts.SourceFile> {
  return createToolSchemaTransformer(program);
}
