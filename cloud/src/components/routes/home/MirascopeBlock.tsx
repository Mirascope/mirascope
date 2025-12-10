import { ButtonLink } from "@/mirascope-ui/ui/button-link";
import { ResponsiveTextBlock } from "@/src/components/ui/responsive-text-block";
import { BookOpen, Users, ChevronDown } from "lucide-react";
import { ProviderTabbedSection } from "@/src/components/mdx/elements/ProviderTabbedSection";
import { ProviderCodeWrapper } from "@/src/components/mdx/providers/ProviderCodeWrapper";
// Import directly to avoid circular dependency through barrel exports
import MirascopeLogo from "@/src/components/core/branding/MirascopeLogo";

// Mirascope feature block component
export interface MirascopeBlockProps {
  onScrollDown?: () => void;
}

export const MirascopeBlock = ({ onScrollDown }: MirascopeBlockProps) => {
  const codeExample = `from mirascope import llm
from pydantic import BaseModel

class Book(BaseModel):
    title: str
    author: str

# [!code highlight:6]
@llm.call(
    provider="$PROVIDER", 
    model="$MODEL", 
    response_model=Book,
)
def extract_book(text: str) -> str:
    return f"Extract the book: {text}"

text = "The Name of the Wind by Patrick Rothfuss"
book: Book = extract_book(text) # [!code highlight]`;

  return (
    <div className="flex min-h-screen flex-col items-center justify-center px-4 py-16">
      <ResponsiveTextBlock
        lines={["LLM abstractions that", "aren't obstructions"]}
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

      <div className="mt-2 flex w-full max-w-3xl flex-col items-center justify-center gap-4 sm:flex-row">
        <ButtonLink
          href="/docs/mirascope"
          variant="default"
          size="default"
          className="landing-page-box-shadow landing-page-box-shadow-hover w-full min-w-[200px] px-6 py-4 text-center font-medium sm:w-auto"
        >
          <BookOpen className="size-5" aria-hidden="true" /> Mirascope Docs
        </ButtonLink>
        <ButtonLink
          href="https://mirascope.com/discord-invite"
          variant="outline"
          size="default"
          className="landing-page-box-shadow landing-page-box-shadow-hover w-full min-w-[200px] border-0 bg-white px-6 py-4 text-center font-medium text-black hover:bg-gray-100 hover:text-black sm:w-auto"
        >
          <Users className="size-5" aria-hidden="true" /> Join the Community
        </ButtonLink>
      </div>

      {/* Scroll indicator to Lilypad section */}
      {onScrollDown && (
        <div className="mt-12 flex justify-center">
          <div className="landing-page-box-shadow landing-page-box-shadow-hover relative h-12 w-12 overflow-hidden rounded-full">
            <button
              onClick={onScrollDown}
              className="bg-primary/80 hover:bg-primary absolute inset-0 flex items-center justify-center border-0 transition-all"
              aria-label="Scroll to Lilypad section"
            >
              <ChevronDown className="h-6 w-6 text-white" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
