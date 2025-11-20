import { HomePage } from "@/src/components/home-page";
// import { Protected } from '@/src/components/protected';
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/")({
  component: App,
});

function App() {
  return (
    // <Protected>
    <HomePage />
    // </Protected>
  );
}
