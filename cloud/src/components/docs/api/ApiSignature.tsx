import React from "react";

/**
 * Component to display an API function/method signature
 */
export function ApiSignature({ children }: { children: React.ReactNode }) {
  return (
    <div className="api-signature bg-muted my-4 overflow-x-auto rounded-md p-3 font-mono">
      {children}
    </div>
  );
}
