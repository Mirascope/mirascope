import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect } from "react";

import { Protected } from "@/app/components/protected";

function ProjectsIndexPage() {
  const navigate = useNavigate();

  useEffect(() => {
    void navigate({ to: "/cloud/projects/dashboard", replace: true });
  }, [navigate]);

  return null;
}

export const Route = createFileRoute("/cloud/projects/")({
  component: () => (
    <Protected>
      <ProjectsIndexPage />
    </Protected>
  ),
});
