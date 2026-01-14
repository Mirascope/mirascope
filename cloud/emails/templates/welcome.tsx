/**
 * @fileoverview Welcome email template for new Mirascope Cloud users.
 *
 * Sent to new users upon signup with personal message from founder,
 * helpful resources, and credit incentive program details.
 */
import {
  Html,
  Head,
  Preview,
  Body,
  Container,
  Section,
  Text,
  Heading,
  Hr,
} from "@react-email/components";
import { Logo } from "@/emails/templates/components/logo";
import { Button } from "@/emails/templates/components/button";
import { Footer } from "@/emails/templates/components/footer";

interface WelcomeEmailProps {
  name: string | null;
}

/**
 * Welcome email template for new users.
 *
 * Features:
 * - Personal greeting from founder
 * - Links to documentation and Discord
 * - Credit incentive program ($30 total)
 * - Encourages reply for direct communication
 *
 * @param name - User's name for personalization (null for generic greeting)
 */
export function WelcomeEmail({ name }: WelcomeEmailProps) {
  const greeting = name ? `Hi ${name}` : "Hello";

  return (
    <Html>
      <Head />
      <Preview>
        Welcome to Mirascope Cloud - Get Started with $30 in Credits
      </Preview>
      <Body style={main}>
        <Container style={container}>
          {/* Logo Section */}
          <Section style={logoSection}>
            <Logo />
          </Section>

          {/* Main Content */}
          <Section style={contentSection}>
            <Heading style={h1}>Welcome to Mirascope Cloud!</Heading>

            <Text style={text}>{greeting},</Text>

            <Text style={text}>
              I'm William, founder of Mirascope. Thank you for signing up! We're
              excited to have you building with us.
            </Text>

            <Text style={text}>
              To get you started, here are some helpful resources:
            </Text>

            {/* Resources Section */}
            <Section style={resourcesSection}>
              <Button href="https://mirascope.com/docs">
                View Documentation
              </Button>
            </Section>

            {/* Credit Incentive Program */}
            <Hr style={hr} />

            <Heading as="h2" style={h2}>
              Earn Up to $30 in Credits
            </Heading>

            <Text style={text}>
              We'd love to learn more about how you're using Mirascope. Here's
              how you can earn additional credits:
            </Text>

            <ul style={list}>
              <li style={listItem}>
                <Text style={incentiveText}>
                  <strong>$5</strong> - Join our Discord and introduce yourself
                </Text>
              </li>
              <li style={listItem}>
                <Text style={incentiveText}>
                  <strong>$5</strong> - Share your project in our show-and-tell
                  channel
                </Text>
              </li>
              <li style={listItem}>
                <Text style={incentiveText}>
                  <strong>$20</strong> - Schedule a user interview after using
                  your credits
                </Text>
              </li>
            </ul>

            <Section style={resourcesSection}>
              <Button href="https://mirascope.com/discord-invite">
                Join Our Discord
              </Button>
            </Section>

            <Hr style={hr} />

            {/* Personal Touch */}
            <Text style={text}>
              Have questions or feedback? Just reply to this email - I read and
              respond to every message personally.
            </Text>

            <Text style={signature}>
              Best,
              <br />
              William Bakst
              <br />
              Founder & CEO
              <br />
              Mirascope, Inc.
            </Text>
          </Section>

          <Footer />
        </Container>
      </Body>
    </Html>
  );
}

// Styles following email best practices
const main = {
  backgroundColor: "#f6f9fc",
  fontFamily:
    '-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Ubuntu,sans-serif',
};

const container = {
  backgroundColor: "#ffffff",
  margin: "0 auto",
  padding: "20px 0 48px",
  marginBottom: "64px",
};

const logoSection = {
  padding: "32px",
  textAlign: "center" as const,
};

const contentSection = {
  padding: "0 48px",
};

const h1 = {
  color: "#1f2937",
  fontSize: "24px",
  fontWeight: "700",
  lineHeight: "32px",
  margin: "0 0 16px",
};

const h2 = {
  color: "#1f2937",
  fontSize: "20px",
  fontWeight: "600",
  lineHeight: "28px",
  margin: "24px 0 16px",
};

const text = {
  color: "#374151",
  fontSize: "16px",
  lineHeight: "24px",
  margin: "16px 0",
};

const incentiveText = {
  color: "#374151",
  fontSize: "16px",
  lineHeight: "24px",
  margin: "8px 0",
};

const resourcesSection = {
  textAlign: "center" as const,
  margin: "24px 0",
};

const hr = {
  borderColor: "#e5e7eb",
  margin: "32px 0",
};

const list = {
  paddingLeft: "20px",
  margin: "16px 0",
};

const listItem = {
  marginBottom: "12px",
};

const signature = {
  color: "#374151",
  fontSize: "16px",
  lineHeight: "24px",
  margin: "32px 0 0",
};

export default WelcomeEmail;
