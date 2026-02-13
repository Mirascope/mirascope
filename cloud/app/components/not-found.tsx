import { Link } from "@tanstack/react-router";

import { useOrganization } from "@/app/contexts/organization";

function useHomeLink(): string {
  try {
    const { selectedOrganization } = useOrganization();
    if (selectedOrganization) {
      return `/${selectedOrganization.slug}`;
    }
  } catch {
    // Outside OrganizationProvider or context unavailable
  }
  return "/";
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function NotFound({ children }: { children?: any }) {
  const homeLink = useHomeLink();

  return (
    <div className="space-y-2 p-2">
      <div className="text-gray-600 dark:text-gray-400">
        {children || <p>The page you are looking for does not exist.</p>}
      </div>
      <p className="flex items-center gap-2 flex-wrap">
        <button
          onClick={() => window.history.back()}
          className="bg-emerald-500 text-white px-2 py-1 rounded-sm uppercase font-black text-sm"
        >
          Go back
        </button>
        <Link
          to={homeLink}
          className="bg-cyan-600 text-white px-2 py-1 rounded-sm uppercase font-black text-sm"
        >
          Start Over
        </Link>
      </p>
    </div>
  );
}
