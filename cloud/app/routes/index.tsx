import { CenteredLayout } from "@/app/components/centered-layout";
import { FrontPage } from "@/app/components/front-page";
import { Protected } from "@/app/components/protected";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/")({
  component: App,
});

function App() {
  return (
    <CenteredLayout>
      <Protected>
        <FrontPage />
      </Protected>
    </CenteredLayout>
  );
}
