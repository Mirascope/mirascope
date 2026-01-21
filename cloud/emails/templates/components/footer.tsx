import { Section, Text, Hr, Link } from "@react-email/components";

/**
 * Standard email footer component.
 *
 * Includes copyright notice and links to main site, documentation, and Discord.
 * Automatically displays the current year in the copyright notice.
 */
export function Footer() {
  return (
    <>
      <Hr style={hr} />
      <Section style={footer}>
        <Text style={footerText}>
          © {new Date().getFullYear()} Mirascope. All rights reserved.
        </Text>
        <Text style={footerText}>
          <Link href="https://mirascope.com" style={footerLink}>
            mirascope.com
          </Link>
          {" • "}
          <Link href="https://mirascope.com/docs" style={footerLink}>
            Documentation
          </Link>
          {" • "}
          <Link href="https://mirascope.com/discord-invite" style={footerLink}>
            Discord
          </Link>
        </Text>
      </Section>
    </>
  );
}

const hr = {
  borderColor: "#e5e7eb",
  margin: "32px 48px",
};

const footer = {
  padding: "0 48px 32px",
  textAlign: "center" as const,
};

const footerText = {
  color: "#6b7280",
  fontSize: "14px",
  lineHeight: "20px",
  margin: "8px 0",
};

const footerLink = {
  color: "#6366f1",
  textDecoration: "none",
};
