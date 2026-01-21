import { Img } from "@react-email/components";

/**
 * Mirascope logo component for email templates.
 *
 * Displays the Mirascope logo centered with appropriate sizing for emails.
 * Logo is loaded from the production CDN URL.
 */
export function Logo() {
  return (
    <Img
      src="https://mirascope.com/icons/logo.svg"
      width="64"
      height="64"
      alt="Mirascope"
      style={{
        display: "block",
        margin: "0 auto",
      }}
    />
  );
}
