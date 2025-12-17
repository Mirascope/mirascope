import { createFileRoute } from "@tanstack/react-router";
import { TempPage } from "@/app/components/temp-page";

export const Route = createFileRoute("/blog")({
  // todo(sebastian): temp route ahead of porting md/mdx files
  component: () => <TempPage name="Blog" />,
});
