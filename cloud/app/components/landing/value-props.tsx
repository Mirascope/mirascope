import { Plug, Rocket, Sparkles } from "lucide-react";

const PROPS = [
  {
    icon: Rocket,
    title: "Instant Deployment",
    body: "Name it, deploy it. Your Claw runs serverlessly in seconds. No infrastructure, no code, no waiting.",
  },
  {
    icon: Sparkles,
    title: "AI That Creates",
    body: "Powered by the Mirascope Skill, your Claw writes, versions, and optimizes its own AI automations.",
  },
  {
    icon: Plug,
    title: "Integrations Made Easy",
    body: "Connect to Slack, Discord, Telegram, and more. Your Claw fits right into the tools you already use.",
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
