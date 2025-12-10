import { cn } from "@/src/lib/utils";

interface DiscordLinkProps {
  isLandingPage: boolean;
  className?: string;
}

export default function DiscordLink({
  isLandingPage,
  className,
}: DiscordLinkProps) {
  const logoColor = isLandingPage ? "White" : "Blurple";

  return (
    <a
      href="/discord-invite"
      target="_blank"
      rel="noopener noreferrer"
      className={cn("flex flex-col px-2 py-1", "nav-text", className)}
    >
      {/* "Join our" text on first line */}
      <div className="flex items-center text-base font-medium">
        <span>Join our</span>
      </div>

      {/* Discord logo on second line */}
      <div className="mt-0.5 flex items-center">
        <img
          src={`/assets/branding/Discord-Logo-${logoColor}.svg`}
          alt="Discord"
          className="h-2.5 w-full"
        />
      </div>
    </a>
  );
}
