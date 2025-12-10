import { ResponsiveTextBlock } from "@/src/components/ui/responsive-text-block";
import { ProviderTabbedSection } from "@/src/components/mdx/elements/ProviderTabbedSection";
import { ProviderCodeWrapper } from "@/src/components/mdx/providers/ProviderCodeWrapper";
import { MirascopeLogo } from "@/src/components/core/branding";

export const MirascopeV2Block = () => {
  const codeExample = `import os
from enum import Enum

from mirascope import llm

# One API key gives you access to all supported providers
os.environ["MIRASCOPE_API_KEY"] = "sk-..."  # [!code highlight]


class Label(str, Enum):
    FEATURE_REQUEST = "feature_request"
    BUG = "bug"
    QUESTION = "question"
    DISCUSSION = "discussion"


@llm.call("openai:gpt-4o-mini", response_format=Label)
def triage(ticket: str) -> str:
    return f"Triage this ticket: {ticket}"


ticket = "Please add native router support!"
with llm.model("$PROVIDER:MODEL"):  # [!code highlight]
    response: llm.Response[Label] = triage(ticket)  # runs with $PROVIDER! # [!code highlight]
    label: Label = response.format()`;

  return (
    <div className="flex min-h-fit flex-col items-center justify-center px-4">
      <ResponsiveTextBlock
        lines={["One API key with access", "to all supported providers"]}
        element="h2"
        fontSize="clamp(1.5rem, 5vw, 3rem)"
        className="text-shadow-medium mb-6 text-center text-white"
        lineClassName="font-bold"
        lineSpacing="mb-2"
      />
      <div className="bg-background/60 mb-2 w-full max-w-3xl rounded-md">
        <ProviderTabbedSection
          customHeader={
            <div className="flex items-center px-1 pb-2">
              <MirascopeLogo size="micro" withText={true} />
            </div>
          }
        >
          <ProviderCodeWrapper
            className="textured-bg"
            code={codeExample}
            language="python"
          />
        </ProviderTabbedSection>
      </div>
    </div>
  );
};
