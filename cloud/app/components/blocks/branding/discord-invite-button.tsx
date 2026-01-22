import * as React from "react";
import { cn } from "@/app/lib/utils";
import { DISCORD_INVITE_URL } from "@/app/lib/site";
import { buttonVariants } from "@/app/components/ui/button";
import type { ButtonProps } from "@/app/components/ui/button";

interface DiscordInviteButtonProps {
  variant?: ButtonProps["variant"];
  size?: ButtonProps["size"];
  className?: string;
  children?: React.ReactNode;
}

export default function DiscordInviteButton({
  variant = "default",
  size = "default",
  className,
  children,
}: DiscordInviteButtonProps) {
  return (
    <a
      href={DISCORD_INVITE_URL}
      target="_blank"
      rel="noopener noreferrer"
      className={cn(buttonVariants({ variant, size }), className)}
    >
      {children}
    </a>
  );
}
