import { DISCORD_INVITE_URL } from "@/app/lib/site";
import { cn } from "@/app/lib/utils";

interface DiscordLinkProps {
  className?: string;
}

export default function DiscordLink({ className }: DiscordLinkProps) {
  return (
    <a
      href={DISCORD_INVITE_URL}
      target="_blank"
      rel="noopener noreferrer"
      className={cn(
        "flex flex-col px-2 py-1 hover:cursor-pointer",
        "nav-text",
        className,
      )}
    >
      {/* "Join our" text on first line */}
      <div className="flex items-center text-base font-medium">
        <span>Join our</span>
      </div>

      {/* Discord logo on second line */}
      <div className="mt-0.5 flex items-center">
        <div
          className="h-2.5 w-full discord-logo"
          role="img"
          aria-label="Discord"
        />
      </div>
    </a>
  );
}
