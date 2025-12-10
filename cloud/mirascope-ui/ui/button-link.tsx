import { Link } from "@tanstack/react-router";
import type { LinkProps } from "@tanstack/react-router";
import { buttonVariants } from "./button";
import { cn } from "@/mirascope-ui/lib/utils";
import type { ButtonProps } from "./button";

export interface ButtonLinkProps {
  href: string;
  external?: boolean;
  variant?: ButtonProps["variant"];
  size?: ButtonProps["size"];
  className?: string;
  children?: React.ReactNode;
}

export function ButtonLink({
  className,
  variant = "outline",
  size = "default",
  href,
  external,
  children,
  ...props
}: ButtonLinkProps & Omit<React.AnchorHTMLAttributes<HTMLAnchorElement>, keyof ButtonLinkProps>) {
  const isExternal =
    external || href.startsWith("http") || href.startsWith("https") || href.startsWith("//");

  const classNames = cn(buttonVariants({ variant, size, className }));

  if (isExternal) {
    return (
      <a href={href} className={classNames} target="_blank" rel="noopener noreferrer" {...props}>
        {children}
      </a>
    );
  }

  return (
    <Link
      to={href as LinkProps["to"]}
      className={classNames}
      {...(props as Omit<LinkProps, "to" | "className">)}
    >
      {children}
    </Link>
  );
}
