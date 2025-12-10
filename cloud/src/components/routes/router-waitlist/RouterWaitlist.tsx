import { PageMeta } from "@/src/components/";
import { RouterWaitlistForm } from "./RouterWaitlistForm";
import { MirascopeV2Block } from "./MirascopeV2Block";
import { ProviderContextProvider } from "@/src/components/core/providers/ProviderContext";

export function RouterWaitlist() {
  return (
    <>
      <PageMeta title="Router Waitlist" description="The AI Engineer's Developer Stack" />
      <div className="mt-4 sm:mt-32">
        <ProviderContextProvider>
          <div data-gradient-fade={true} className="mb-4">
            <MirascopeV2Block />
          </div>
        </ProviderContextProvider>
        <RouterWaitlistForm />
      </div>
    </>
  );
}
