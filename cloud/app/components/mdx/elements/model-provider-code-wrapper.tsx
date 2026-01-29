import { CodeBlock } from "@/app/components/blocks/code-block/code-block";
// No need to import React with JSX transform
import {
  useProvider,
  replaceProviderVariables,
} from "@/app/components/mdx/elements/model-provider-provider";

/**
 * A wrapper component for code blocks that handles provider-specific substitutions.
 * This allows us to use standard markdown code blocks with provider-specific variables.
 */
export function ModelProviderCodeWrapper({
  code,
  language,
  meta,
  className,
}: {
  code: string;
  language: string;
  meta?: string;
  className?: string;
}) {
  const { provider } = useProvider();

  // Only process python or bash code
  if (code && (language === "python" || language === "bash")) {
    code = replaceProviderVariables(code, provider);
  }

  return (
    <CodeBlock
      className={className}
      code={code}
      language={language}
      meta={meta}
    />
  );
}
