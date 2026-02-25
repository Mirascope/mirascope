import { Eye, Rocket, Sparkles } from "lucide-react";

const PROPS = [
  {
    icon: Rocket,
    title: "Ship Faster",
    body: "Build LLM-powered features with clean abstractions. Focus on your product, not boilerplate.",
  },
  {
    icon: Sparkles,
    title: "AI-Powered Optimization",
    body: "Version, trace, and optimize your prompts and agents with built-in observability.",
  },
  {
    icon: Eye,
    title: "Full Observability",
    body: "Trace every call, monitor costs, and debug issues across all your LLM providers in one place.",
  },
] as const;

export function ValueProps() {
  return (
    <section className="mx-auto w-full max-w-md px-4 pt-2 pb-3 lg:max-w-5xl lg:px-8 lg:pt-0 lg:pb-3">
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3 lg:gap-5">
        {PROPS.map((prop) => (
          <div
            key={prop.title}
            className="rounded-xl border border-white/20 bg-white/80 p-4 shadow-sm backdrop-blur-sm dark:border-border/40 dark:bg-background/80 lg:p-5"
          >
            <h3 className="mb-1 flex items-center gap-2 font-display text-base text-slate-900 dark:text-foreground">
              <prop.icon className="size-4 text-mirple" />
              {prop.title}
            </h3>
            <p className="font-sans text-sm leading-relaxed text-slate-600 dark:text-muted-foreground">
              {prop.body}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}
