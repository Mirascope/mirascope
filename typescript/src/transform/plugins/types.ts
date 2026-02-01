/**
 * Shared types for build system plugins.
 */

import type ts from 'typescript';

/**
 * Common transformer configuration that can be passed to build plugins.
 */
export interface TransformerConfig {
  /**
   * Additional transformers to run before the Mirascope transformer.
   */
  before?: ts.TransformerFactory<ts.SourceFile>[];

  /**
   * Additional transformers to run after the Mirascope transformer.
   */
  after?: ts.TransformerFactory<ts.SourceFile>[];
}
