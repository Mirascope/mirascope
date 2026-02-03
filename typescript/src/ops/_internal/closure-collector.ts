/**
 * Closure dependency collection for function versioning.
 *
 * Collects all dependencies (imports, globals, definitions) needed
 * to compute a complete closure for a function.
 */

import * as fs from "fs";
import * as path from "path";
import * as ts from "typescript";

import type { Closure, DependencyInfo, RawClosure } from "./closure";

import { createClosure } from "./closure";

/**
 * Information about an import statement.
 */
interface ImportInfo {
  /** The full import statement */
  statement: string;
  /** Whether this is a third-party import */
  isThirdParty: boolean;
  /** Whether this is a type-only import */
  isTypeOnly: boolean;
  /** The imported names (for named imports) */
  importedNames: string[];
  /** The module specifier */
  moduleSpecifier: string;
}

/**
 * Collects all names (identifiers) used within an AST node.
 */
class NameCollector {
  private usedNames: Set<string> = new Set();

  /**
   * Collect all names used in the given node.
   */
  collect(node: ts.Node): Set<string> {
    this.visit(node);
    return this.usedNames;
  }

  private visit(node: ts.Node): void {
    if (ts.isIdentifier(node)) {
      this.usedNames.add(node.text);
    } else if (ts.isPropertyAccessExpression(node)) {
      // Collect the full dotted path and the base name
      const fullPath = this.getPropertyAccessPath(node);
      if (fullPath) {
        this.usedNames.add(fullPath);
        const baseName = fullPath.split(".")[0];
        if (baseName) {
          this.usedNames.add(baseName);
        }
      }
      // Also visit the expression part
      this.visit(node.expression);
    } else if (ts.isCallExpression(node)) {
      // Collect the function name
      if (ts.isIdentifier(node.expression)) {
        this.usedNames.add(node.expression.text);
      }
      ts.forEachChild(node, (child) => this.visit(child));
    } else {
      ts.forEachChild(node, (child) => this.visit(child));
    }
  }

  /**
   * Get the full dotted path from a property access expression.
   */
  private getPropertyAccessPath(
    node: ts.PropertyAccessExpression,
  ): string | null {
    const parts: string[] = [];
    let current: ts.Expression = node;

    while (ts.isPropertyAccessExpression(current)) {
      parts.unshift(current.name.text);
      current = current.expression;
    }

    if (ts.isIdentifier(current)) {
      parts.unshift(current.text);
      return parts.join(".");
    }

    return null;
  }
}

/**
 * Collects import statements from a source file based on used names.
 */
class ImportCollector {
  private imports: ImportInfo[] = [];
  private usedNames: Set<string>;
  private sourceFile: ts.SourceFile;
  private program: ts.Program;

  constructor(
    sourceFile: ts.SourceFile,
    usedNames: Set<string>,
    program: ts.Program,
  ) {
    this.sourceFile = sourceFile;
    this.usedNames = usedNames;
    this.program = program;
  }

  /**
   * Collect all relevant import statements.
   */
  collect(): ImportInfo[] {
    ts.forEachChild(this.sourceFile, (node) => {
      if (ts.isImportDeclaration(node)) {
        this.processImportDeclaration(node);
      }
    });
    return this.imports;
  }

  private processImportDeclaration(node: ts.ImportDeclaration): void {
    const moduleSpecifier = (node.moduleSpecifier as ts.StringLiteral).text;
    const importClause = node.importClause;
    const isTypeOnly = importClause?.isTypeOnly ?? false;

    if (!importClause) {
      // Side-effect import: import "module"
      return;
    }

    const isThirdParty = this.isThirdPartyModule(moduleSpecifier);
    const importedNames: string[] = [];

    // Default import: import foo from "module"
    if (importClause.name) {
      const name = importClause.name.text;
      if (this.isUsedImport(name)) {
        importedNames.push(name);
      }
    }

    // Named imports: import { foo, bar } from "module"
    if (importClause.namedBindings) {
      if (ts.isNamedImports(importClause.namedBindings)) {
        for (const element of importClause.namedBindings.elements) {
          const name = element.name.text;
          if (this.isUsedImport(name)) {
            importedNames.push(name);
          }
        }
      } else if (ts.isNamespaceImport(importClause.namedBindings)) {
        // Namespace import: import * as foo from "module"
        const name = importClause.namedBindings.name.text;
        if (this.isUsedImport(name)) {
          importedNames.push(name);
        }
      }
    }

    if (importedNames.length > 0) {
      // Reconstruct the import statement with only the used names
      const statement = this.reconstructImportStatement(node, importedNames);
      this.imports.push({
        statement,
        isThirdParty,
        isTypeOnly,
        importedNames,
        moduleSpecifier,
      });
    }
  }

  private isUsedImport(name: string): boolean {
    return (
      this.usedNames.has(name) ||
      Array.from(this.usedNames).some((used) => used.startsWith(`${name}.`))
    );
  }

  private isThirdPartyModule(moduleSpecifier: string): boolean {
    // Relative imports are not third-party
    if (
      moduleSpecifier.startsWith(".") ||
      moduleSpecifier.startsWith("/") ||
      moduleSpecifier.startsWith("@/")
    ) {
      return false;
    }

    // Node built-ins
    const nodeBuiltins = new Set([
      "fs",
      "path",
      "crypto",
      "http",
      "https",
      "url",
      "util",
      "os",
      "events",
      "stream",
      "buffer",
      "child_process",
      "cluster",
      "dgram",
      "dns",
      "net",
      "readline",
      "tls",
      "tty",
      "zlib",
      "assert",
      "async_hooks",
      "console",
      "constants",
      "domain",
      "inspector",
      "module",
      "perf_hooks",
      "process",
      "punycode",
      "querystring",
      "string_decoder",
      "timers",
      "trace_events",
      "v8",
      "vm",
      "wasi",
      "worker_threads",
    ]);

    const baseModule = moduleSpecifier.split("/")[0]!;
    if (nodeBuiltins.has(baseModule) || moduleSpecifier.startsWith("node:")) {
      return true;
    }

    // Everything else (npm packages) is third-party
    return true;
  }

  private reconstructImportStatement(
    node: ts.ImportDeclaration,
    usedNames: string[],
  ): string {
    const moduleSpecifier = (node.moduleSpecifier as ts.StringLiteral).text;
    const importClause = node.importClause!;
    const isTypeOnly = importClause.isTypeOnly;

    const typePrefix = isTypeOnly ? "type " : "";
    const parts: string[] = [];

    // Check for default import
    if (importClause.name && usedNames.includes(importClause.name.text)) {
      parts.push(importClause.name.text);
    }

    // Check for named imports
    if (importClause.namedBindings) {
      if (ts.isNamedImports(importClause.namedBindings)) {
        const namedParts: string[] = [];
        for (const element of importClause.namedBindings.elements) {
          if (usedNames.includes(element.name.text)) {
            if (element.propertyName) {
              namedParts.push(
                `${element.propertyName.text} as ${element.name.text}`,
              );
            } else {
              namedParts.push(element.name.text);
            }
          }
        }
        if (namedParts.length > 0) {
          parts.push(`{ ${namedParts.join(", ")} }`);
        }
      } else if (ts.isNamespaceImport(importClause.namedBindings)) {
        if (usedNames.includes(importClause.namedBindings.name.text)) {
          parts.push(`* as ${importClause.namedBindings.name.text}`);
        }
      }
    }

    return `import ${typePrefix}${parts.join(", ")} from "${moduleSpecifier}";`;
  }
}

/**
 * Information about a top-level definition (function, class, type, interface, enum).
 */
interface DefinitionInfo {
  node: ts.Node;
  name: string;
  kind: "function" | "class" | "type" | "interface" | "enum";
}

/**
 * Collects function and class definitions from a source file.
 */
class DefinitionCollector {
  private sourceFile: ts.SourceFile;
  private usedNames: Set<string>;
  private definitions: Map<string, string> = new Map();
  private visitedNames: Set<string> = new Set();
  /** Map from definition name to its info for O(1) lookup */
  private definitionMap: Map<string, DefinitionInfo> = new Map();

  constructor(sourceFile: ts.SourceFile, usedNames: Set<string>) {
    this.sourceFile = sourceFile;
    this.usedNames = usedNames;
    this.buildDefinitionMap();
  }

  /**
   * Build a map of all top-level definitions for O(1) lookup.
   */
  private buildDefinitionMap(): void {
    ts.forEachChild(this.sourceFile, (node) => {
      if (ts.isFunctionDeclaration(node) && node.name) {
        this.definitionMap.set(node.name.text, {
          node,
          name: node.name.text,
          kind: "function",
        });
      } else if (ts.isClassDeclaration(node) && node.name) {
        this.definitionMap.set(node.name.text, {
          node,
          name: node.name.text,
          kind: "class",
        });
      } else if (ts.isTypeAliasDeclaration(node)) {
        this.definitionMap.set(node.name.text, {
          node,
          name: node.name.text,
          kind: "type",
        });
      } else if (ts.isInterfaceDeclaration(node)) {
        this.definitionMap.set(node.name.text, {
          node,
          name: node.name.text,
          kind: "interface",
        });
      } else if (ts.isEnumDeclaration(node)) {
        this.definitionMap.set(node.name.text, {
          node,
          name: node.name.text,
          kind: "enum",
        });
      }
    });
  }

  /**
   * Collect all referenced definitions using a work queue.
   */
  collect(): string[] {
    const queue = Array.from(this.usedNames);

    while (queue.length > 0) {
      const name = queue.shift()!;
      if (this.visitedNames.has(name)) continue;

      const info = this.definitionMap.get(name);
      if (!info) continue;

      this.visitedNames.add(name);
      const text = this.getNodeText(info.node);

      if (info.kind === "function") {
        this.definitions.set(name, this.removeVersionDecorator(text));
      } else {
        this.definitions.set(name, text);
      }

      // For functions and classes, collect nested dependencies
      if (info.kind === "function" || info.kind === "class") {
        const newDeps = this.collectNestedDependencies(info.node, name);
        for (const dep of newDeps) {
          if (!this.visitedNames.has(dep)) {
            this.usedNames.add(dep);
            queue.push(dep);
          }
        }
      }
    }

    return Array.from(this.definitions.values());
  }

  /**
   * Collect nested dependencies from a node.
   * Returns the names used in the node (excluding the node's own name).
   */
  private collectNestedDependencies(
    node: ts.Node,
    currentName: string,
  ): Set<string> {
    const nestedCollector = new NameCollector();
    const nestedNames = nestedCollector.collect(node);
    nestedNames.delete(currentName);
    return nestedNames;
  }

  private getNodeText(node: ts.Node): string {
    return node.getText(this.sourceFile);
  }

  private removeVersionDecorator(code: string): string {
    // Remove @version and version() decorators
    // This is a simple regex-based approach
    return code
      .replace(/@version\s*\([^)]*\)\s*/g, "")
      .replace(/@version\s*/g, "")
      .replace(/@ops\.version\s*\([^)]*\)\s*/g, "")
      .replace(/@ops\.version\s*/g, "");
  }
}

/**
 * Collects global variable assignments from a source file.
 */
class GlobalAssignmentCollector {
  private sourceFile: ts.SourceFile;
  private usedNames: Set<string>;
  private assignments: string[] = [];
  private visitedNames: Set<string> = new Set();
  /** Map from variable name to its declaration node and statement */
  private variableMap: Map<
    string,
    { declaration: ts.VariableDeclaration; statement: ts.VariableStatement }
  > = new Map();

  constructor(sourceFile: ts.SourceFile, usedNames: Set<string>) {
    this.sourceFile = sourceFile;
    this.usedNames = usedNames;
    this.buildVariableMap();
  }

  /**
   * Build a map of all top-level variable declarations for O(1) lookup.
   */
  private buildVariableMap(): void {
    ts.forEachChild(this.sourceFile, (node) => {
      if (ts.isVariableStatement(node)) {
        for (const declaration of node.declarationList.declarations) {
          if (ts.isIdentifier(declaration.name)) {
            this.variableMap.set(declaration.name.text, {
              declaration,
              statement: node,
            });
          }
        }
      }
    });
  }

  /**
   * Collect all used global variable assignments using a work queue.
   */
  collect(): string[] {
    const queue = Array.from(this.usedNames);
    const visitedStatements = new Set<ts.VariableStatement>();

    while (queue.length > 0) {
      const name = queue.shift()!;
      if (this.visitedNames.has(name)) continue;

      const entry = this.variableMap.get(name);
      if (!entry) continue;

      this.visitedNames.add(name);

      // Only add statement once even if multiple variables from it are used
      if (!visitedStatements.has(entry.statement)) {
        visitedStatements.add(entry.statement);
        this.assignments.push(entry.statement.getText(this.sourceFile));
      }

      // Collect dependencies from this variable's initializer and add to queue
      const newDeps = this.collectNestedDependencies(entry.declaration);
      for (const dep of newDeps) {
        if (!this.visitedNames.has(dep)) {
          this.usedNames.add(dep);
          queue.push(dep);
        }
      }
    }

    return this.assignments;
  }

  /**
   * Collect nested dependencies from a variable declaration.
   * Returns the names used in the initializer.
   */
  private collectNestedDependencies(
    declaration: ts.VariableDeclaration,
  ): Set<string> {
    if (!declaration.initializer) return new Set();

    const nestedCollector = new NameCollector();
    return nestedCollector.collect(declaration.initializer);
  }
}

/**
 * Extract package dependencies from package.json files.
 */
function extractPackageDependencies(
  imports: ImportInfo[],
  projectRoot: string,
): Record<string, DependencyInfo> {
  const dependencies: Record<string, DependencyInfo> = {};
  const packageJsonPath = path.join(projectRoot, "package.json");

  if (!fs.existsSync(packageJsonPath)) {
    return dependencies;
  }

  let packageJson: {
    dependencies?: Record<string, string>;
    devDependencies?: Record<string, string>;
  };
  try {
    packageJson = JSON.parse(fs.readFileSync(packageJsonPath, "utf-8")) as {
      dependencies?: Record<string, string>;
      devDependencies?: Record<string, string>;
    };
  } catch {
    return dependencies;
  }

  const allDeps = {
    ...packageJson.dependencies,
    ...packageJson.devDependencies,
  };

  for (const importInfo of imports) {
    if (!importInfo.isThirdParty) continue;

    // Get the package name from the module specifier
    const moduleSpecifier = importInfo.moduleSpecifier;
    let packageName: string;

    if (moduleSpecifier.startsWith("@")) {
      // Scoped package: @scope/package
      const parts = moduleSpecifier.split("/");
      packageName = `${parts[0]}/${parts[1]}`;
    } else {
      // Regular package
      packageName = moduleSpecifier.split("/")[0]!;
    }

    // Skip node built-ins
    if (moduleSpecifier.startsWith("node:")) continue;

    const version = allDeps[packageName];
    if (version && !dependencies[packageName]) {
      dependencies[packageName] = {
        version: version.replace(/^[\^~]/, ""), // Remove version prefix
      };
    }
  }

  return dependencies;
}

/**
 * Options for collecting closure data.
 */
export interface CollectorOptions {
  /** The TypeScript program for type checking */
  program: ts.Program;
  /** The project root directory for package.json lookup */
  projectRoot?: string;
}

/**
 * Main closure collector that orchestrates all the sub-collectors.
 */
export class ClosureCollector {
  private program: ts.Program;
  private projectRoot: string;

  constructor(options: CollectorOptions) {
    this.program = options.program;
    this.projectRoot = options.projectRoot ?? process.cwd();
  }

  /**
   * Collect closure data for a function node.
   *
   * @param node - The function node (arrow function, function expression, or function declaration)
   * @param sourceFile - The source file containing the node
   * @param variableName - The variable name the function is assigned to (if any)
   * @returns The complete Closure object
   */
  collect(
    node: ts.Node,
    sourceFile: ts.SourceFile,
    variableName?: string,
  ): Closure {
    const rawClosure = this.collectRaw(node, sourceFile, variableName);
    return createClosure(rawClosure);
  }

  /**
   * Collect raw closure data without formatting and hashing.
   */
  collectRaw(
    node: ts.Node,
    sourceFile: ts.SourceFile,
    variableName?: string,
  ): RawClosure {
    // Extract function name
    const name = this.extractFunctionName(node, variableName);

    // Extract signature
    const signature = this.extractSignature(node, sourceFile);

    // Collect all names used in the function
    const nameCollector = new NameCollector();
    const usedNames = nameCollector.collect(node);

    // Collect definitions first - this recursively adds more names to usedNames
    // as it discovers dependencies in the collected definitions
    const definitionCollector = new DefinitionCollector(sourceFile, usedNames);
    const definitions = definitionCollector.collect();

    // Collect global assignments (variable declarations like const myTool = ...)
    // This also recursively adds nested dependencies to usedNames
    const globalCollector = new GlobalAssignmentCollector(
      sourceFile,
      usedNames,
    );
    const globals = globalCollector.collect();

    // Now collect imports - after both definitions and globals have added
    // all transitive dependencies to usedNames (e.g., if myTool uses z from zod)
    const importCollector = new ImportCollector(
      sourceFile,
      usedNames,
      this.program,
    );
    const imports = importCollector.collect();

    // Extract main declaration
    const mainDeclaration = this.extractMainDeclaration(
      node,
      sourceFile,
      variableName,
    );

    // Extract package dependencies
    const dependencies = extractPackageDependencies(imports, this.projectRoot);

    // Filter imports - only include third-party imports in the closure
    // User-defined imports are replaced with their definitions
    const thirdPartyImports = imports
      .filter((imp) => imp.isThirdParty)
      .map((imp) => imp.statement);

    return {
      name,
      signature,
      imports: thirdPartyImports,
      globals,
      definitions,
      mainDeclaration,
      dependencies,
    };
  }

  private extractFunctionName(node: ts.Node, variableName?: string): string {
    if (variableName) {
      return variableName;
    }

    if (ts.isFunctionDeclaration(node) && node.name) {
      return node.name.text;
    }

    if (ts.isFunctionExpression(node) && node.name) {
      return node.name.text;
    }

    return "anonymous";
  }

  private extractSignature(node: ts.Node, sourceFile: ts.SourceFile): string {
    if (ts.isArrowFunction(node) || ts.isFunctionExpression(node)) {
      // Build signature from parameters and return type
      const params = node.parameters
        .map((p) => p.getText(sourceFile))
        .join(", ");
      const returnType = node.type ? `: ${node.type.getText(sourceFile)}` : "";
      return `(${params})${returnType}`;
    }

    if (ts.isFunctionDeclaration(node)) {
      const params = node.parameters
        .map((p) => p.getText(sourceFile))
        .join(", ");
      const returnType = node.type ? `: ${node.type.getText(sourceFile)}` : "";
      return `(${params})${returnType}`;
    }

    // Fallback
    return "(...)";
  }

  private extractMainDeclaration(
    node: ts.Node,
    sourceFile: ts.SourceFile,
    variableName?: string,
  ): string {
    // Get the function text
    let functionText = node.getText(sourceFile);

    // Remove version wrapper if present
    functionText = this.removeVersionWrapper(functionText);

    // If we have a variable name, wrap it as a const declaration
    if (variableName) {
      return `const ${variableName} = ${functionText};`;
    }

    // For function declarations, return as-is
    if (ts.isFunctionDeclaration(node)) {
      return functionText;
    }

    return functionText;
  }

  private removeVersionWrapper(code: string): string {
    // Remove version() wrapper calls
    // Pattern: version(fn) or version(fn, options)
    const versionPattern =
      /^version\s*\(\s*([\s\S]*?)(?:\s*,\s*\{[\s\S]*?\})?\s*\)$/;
    const match = code.match(versionPattern);
    if (match && match[1]) {
      return match[1].trim();
    }

    // Pattern: versionCall(call) or versionCall(call, options)
    const versionCallPattern =
      /^versionCall\s*\(\s*([\s\S]*?)(?:\s*,\s*\{[\s\S]*?\})?\s*\)$/;
    const versionCallMatch = code.match(versionCallPattern);
    if (versionCallMatch && versionCallMatch[1]) {
      return versionCallMatch[1].trim();
    }

    return code;
  }
}

/**
 * Create a ClosureCollector with the given options.
 */
export function createClosureCollector(
  options: CollectorOptions,
): ClosureCollector {
  return new ClosureCollector(options);
}
