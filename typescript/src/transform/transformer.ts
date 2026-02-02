/**
 * TypeScript transformer for injecting schemas into tool and format definitions,
 * and closure metadata into version() calls.
 *
 * This transformer finds calls to:
 * - `defineTool<T>()`, `defineContextTool<T, DepsT>()` - injects `__schema` property
 * - `defineFormat<T>()` - injects `__schema` property
 * - `version()`, `ops.version()` - injects `__closure` property with hash and signature
 * - `versionCall()`, `ops.versionCall()` - injects `__closure` property for calls
 */

import { createHash } from "crypto";
import ts from "typescript";

import { ClosureCollector } from "../ops/_internal/closure-collector";
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
 * Names of version functions that should have closure metadata injected.
 */
const VERSION_FUNCTION_NAMES = new Set(["version", "versionCall"]);

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

          // Try version transform
          const versionTransformed = tryTransformVersionCall(
            node,
            context,
            sourceFile,
            program,
          );
          if (versionTransformed) {
            return versionTransformed;
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
 * Try to transform a call expression if it's a version() or versionCall() call.
 *
 * For version(fn, options?) or version(options)(fn):
 * - Extracts the function source code and all dependencies from the AST
 * - Uses ClosureCollector for robust dependency extraction
 * - Computes hash and signature using oxfmt for consistent formatting
 * - Injects __closure property into the options object
 *
 * @param node - The call expression node.
 * @param context - The transformation context.
 * @param sourceFile - The source file for extracting text.
 * @param program - The TypeScript program for type information.
 * @returns The transformed node, or undefined if not a version call.
 */
function tryTransformVersionCall(
  node: ts.CallExpression,
  context: ts.TransformationContext,
  sourceFile: ts.SourceFile,
  program: ts.Program,
): ts.CallExpression | undefined {
  // Skip transformation for test files - they test runtime behavior
  const fileName = sourceFile.fileName;
  if (fileName.includes(".test.") || fileName.includes("/tests/")) {
    return undefined;
  }

  const functionName = getFunctionName(node);
  if (!functionName || !VERSION_FUNCTION_NAMES.has(functionName)) {
    return undefined;
  }

  const args = node.arguments;
  const firstArg = args[0];

  if (!firstArg) {
    return undefined;
  }

  // Direct form: version(fn) or version(fn, options)
  // Also handles versionCall(call) or versionCall(call, options)
  if (
    isFunctionExpression(firstArg) ||
    isCallLikeExpression(firstArg, functionName)
  ) {
    return transformDirectVersionCall(
      node,
      context,
      sourceFile,
      firstArg,
      program,
    );
  }

  // Curried form: version(options) - returns a function
  // We need to look at the parent to see if this is version(options)(fn)
  if (ts.isObjectLiteralExpression(firstArg)) {
    // This is the curried form - inject __closure into options
    // The actual function will be passed to the returned wrapper at runtime
    // We can't transform this case statically without seeing the fn
    return undefined;
  }

  return undefined;
}

/**
 * Check if an expression is a call-like object for versionCall.
 * This handles identifiers that reference call objects.
 */
function isCallLikeExpression(
  node: ts.Expression,
  functionName: string,
): boolean {
  // For versionCall, the first argument can be an identifier referencing a call
  if (functionName === "versionCall") {
    return ts.isIdentifier(node) || ts.isCallExpression(node);
  }
  return false;
}

/**
 * Transform a direct version call: version(fn) or version(fn, options)
 * Also handles versionCall(call) or versionCall(call, options)
 */
function transformDirectVersionCall(
  node: ts.CallExpression,
  context: ts.TransformationContext,
  sourceFile: ts.SourceFile,
  fnArg: ts.Expression,
  program: ts.Program,
): ts.CallExpression {
  const factory = context.factory;
  const args = node.arguments;

  // Try to infer name from variable declaration: const myFn = version(...)
  const inferredName = inferVariableName(node);

  // Extract closure metadata using the robust ClosureCollector
  const closureMetadata = extractClosureMetadata(
    fnArg,
    sourceFile,
    program,
    inferredName,
  );

  // Get or create options object (second argument)
  const optionsArg = args[1];
  let newOptionsObject: ts.ObjectLiteralExpression;

  if (optionsArg && ts.isObjectLiteralExpression(optionsArg)) {
    // Options is an object literal - we can merge into it
    // Check if __closure is already present
    const hasClosure = optionsArg.properties.some(
      (prop) =>
        ts.isPropertyAssignment(prop) &&
        ts.isIdentifier(prop.name) &&
        prop.name.text === "__closure",
    );

    if (hasClosure) {
      // Already has closure, don't override
      return node;
    }

    // Check if name is already set in options
    const hasName = optionsArg.properties.some(
      (prop) =>
        ts.isPropertyAssignment(prop) &&
        ts.isIdentifier(prop.name) &&
        prop.name.text === "name",
    );

    // Build new properties: existing + inferred name (if needed) + __closure
    const newProperties = [...optionsArg.properties];

    if (!hasName && inferredName) {
      newProperties.push(
        factory.createPropertyAssignment(
          factory.createIdentifier("name"),
          factory.createStringLiteral(inferredName),
        ),
      );
    }

    newProperties.push(createClosureProperty(closureMetadata, factory));
    newOptionsObject = factory.updateObjectLiteralExpression(
      optionsArg,
      newProperties,
    );
  } else if (optionsArg) {
    // Options is a runtime expression (identifier, call, etc.) - can't merge at compile time
    // Skip transformation and let runtime handle it
    return node;
  } else {
    // No options provided - create new options object with inferred name and __closure
    const properties: ts.PropertyAssignment[] = [];

    if (inferredName) {
      properties.push(
        factory.createPropertyAssignment(
          factory.createIdentifier("name"),
          factory.createStringLiteral(inferredName),
        ),
      );
    }

    properties.push(createClosureProperty(closureMetadata, factory));
    newOptionsObject = factory.createObjectLiteralExpression(properties, true);
  }

  // Create new call expression with the function and updated options
  const newArgs = [fnArg, newOptionsObject, ...args.slice(2)];
  return factory.updateCallExpression(
    node,
    node.expression,
    node.typeArguments,
    newArgs,
  );
}

/**
 * Try to infer the variable name from a version() call's parent nodes.
 *
 * Handles patterns like:
 * - const myFn = version(...)
 * - const myFn = ops.version(...)
 * - export const myFn = version(...)
 */
function inferVariableName(node: ts.CallExpression): string | undefined {
  let current: ts.Node = node;

  // Walk up the AST to find a variable declaration
  while (current.parent) {
    const parent = current.parent;

    // Check for variable declaration: const myFn = version(...)
    if (ts.isVariableDeclaration(parent) && ts.isIdentifier(parent.name)) {
      return parent.name.text;
    }

    // Check for property assignment in object literal (less common)
    if (ts.isPropertyAssignment(parent) && ts.isIdentifier(parent.name)) {
      return parent.name.text;
    }

    // Stop if we hit a statement boundary
    if (ts.isStatement(parent)) {
      break;
    }

    current = parent;
  }

  return undefined;
}

/**
 * Extract closure metadata from a function expression using ClosureCollector.
 *
 * This collects all dependencies (imports, globals, function definitions)
 * and produces a complete closure with consistent formatting via oxfmt.
 */
function extractClosureMetadata(
  fnNode: ts.Expression,
  sourceFile: ts.SourceFile,
  program: ts.Program,
  variableName?: string,
): ClosureMetadataValue {
  try {
    // Use ClosureCollector for robust dependency extraction
    const collector = new ClosureCollector({ program });
    const closure = collector.collect(fnNode, sourceFile, variableName);

    return {
      code: closure.code,
      hash: closure.hash,
      signature: closure.signature,
      signatureHash: closure.signatureHash,
    };
  } catch {
    // Fallback to simple extraction if ClosureCollector fails
    return extractClosureMetadataSimple(fnNode, sourceFile);
  }
}

/**
 * Simple fallback closure extraction without dependency analysis.
 * Used when ClosureCollector fails (e.g., during testing).
 */
function extractClosureMetadataSimple(
  fnNode: ts.Expression,
  sourceFile: ts.SourceFile,
): ClosureMetadataValue {
  // Get the source text of the function
  const code = fnNode.getText(sourceFile);

  // Normalize the code for consistent hashing
  const normalizedCode = normalizeSourceCode(code);

  // Compute hash
  const hash = createHash("sha256").update(normalizedCode).digest("hex");

  // Extract signature
  const signature = extractSignature(fnNode, sourceFile);
  const signatureHash = createHash("sha256").update(signature).digest("hex");

  return {
    code,
    hash,
    signature,
    signatureHash,
  };
}

/**
 * Closure metadata value type for AST generation.
 */
interface ClosureMetadataValue {
  code: string;
  hash: string;
  signature: string;
  signatureHash: string;
}

/**
 * Extract function signature from a function expression.
 */
function extractSignature(
  fnNode: ts.Expression,
  sourceFile: ts.SourceFile,
): string {
  if (ts.isArrowFunction(fnNode) || ts.isFunctionExpression(fnNode)) {
    // Get parameters text
    const params = fnNode.parameters
      .map((p) => p.getText(sourceFile))
      .join(", ");

    // Get return type if available
    const returnType = fnNode.type
      ? `: ${fnNode.type.getText(sourceFile)}`
      : "";

    return `(${params})${returnType}`;
  }

  // For identifiers (function references), we can't extract the signature statically
  return "(...)";
}

/**
 * Normalize source code for consistent hashing.
 * Removes comments and normalizes whitespace.
 */
function normalizeSourceCode(code: string): string {
  // Create a minimal source file to parse the code
  const tempSourceFile = ts.createSourceFile(
    "temp.ts",
    code,
    ts.ScriptTarget.Latest,
    true,
  );

  // Print without comments for normalization
  const printer = ts.createPrinter({ removeComments: true });
  return printer.printFile(tempSourceFile).trim();
}

/**
 * Check if an expression is a function (arrow function or function expression).
 */
function isFunctionExpression(node: ts.Expression): boolean {
  return ts.isArrowFunction(node) || ts.isFunctionExpression(node);
}

/**
 * Create a __closure property assignment from closure metadata.
 */
function createClosureProperty(
  metadata: ClosureMetadataValue,
  factory: ts.NodeFactory,
): ts.PropertyAssignment {
  return factory.createPropertyAssignment(
    factory.createIdentifier("__closure"),
    jsonToAst(metadata, factory),
  );
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
