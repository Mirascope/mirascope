import { useProvider } from "@/src/components/mdx/providers";
import type { Provider } from "@/src/components/mdx/providers";
import { AnalyticsCodeBlock } from "@/src/components/mdx/elements/AnalyticsCodeBlock";
import { cn } from "@/src/lib/utils";
import { TabbedSection, Tab } from "./TabbedSection";

// Define available operating systems
export type OS = "MacOS / Linux" | "Windows";
export const operatingSystems: OS[] = ["MacOS / Linux", "Windows"];

// Define API key variables for each provider
const providerApiKeys: Record<Provider, string | null> = {
  openai: "OPENAI_API_KEY",
  anthropic: "ANTHROPIC_API_KEY",
  mistral: "MISTRAL_API_KEY",
  google: "GOOGLE_API_KEY",
  groq: "GROQ_API_KEY",
  cohere: "CO_API_KEY",
  litellm: "OPENAI_API_KEY", // LiteLLM uses OpenAI's API key by default
  azure: "AZURE_API_KEY",
  bedrock: null, // Superceded by custom instruction
  xai: "XAI_API_KEY",
};

// Special cases for providers like Bedrock, Azure, etc.
const specialInstallInstructions: Record<string, Record<OS, string>> = {
  bedrock: {
    "MacOS / Linux": "aws configure",
    Windows: "aws configure",
  },
  azure: {
    "MacOS / Linux":
      "export AZURE_INFERENCE_ENDPOINT=XXXX\nexport AZURE_INFERENCE_CREDENTIAL=XXXX",
    Windows:
      "set AZURE_INFERENCE_ENDPOINT=XXXX\nset AZURE_INFERENCE_CREDENTIAL=XXXX",
  },
};

interface InstallSnippetProps {
  className?: string;
}

export function InstallSnippet({ className = "" }: InstallSnippetProps) {
  const { provider } = useProvider();

  // Generate install commands for each OS
  const generateCommand = (os: OS) => {
    const setEnvCmd = os === "MacOS / Linux" ? "export" : "set";
    const apiKeyVar = providerApiKeys[provider];

    // Check if this provider has special install instructions
    const hasSpecialInstructions = provider in specialInstallInstructions;
    const specialInstructions = hasSpecialInstructions
      ? specialInstallInstructions[provider][os]
      : `${setEnvCmd} ${apiKeyVar}=XXXX`;

    return `pip install "mirascope[${provider}]"\n${specialInstructions}`;
  };

  return (
    <TabbedSection className={cn(className)}>
      {operatingSystems.map((os) => (
        <Tab key={os} value={os}>
          <AnalyticsCodeBlock code={generateCommand(os)} language="bash" />
        </Tab>
      ))}
    </TabbedSection>
  );
}
