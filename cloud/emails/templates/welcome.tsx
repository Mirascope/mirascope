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
  Tailwind,
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
      <Tailwind>
        <Body className="bg-gray-50 font-sans">
          <Container className="bg-white mx-auto py-5 mb-16">
            {/* Logo Section */}
            <Section className="py-8 text-center">
              <Logo />
            </Section>

            {/* Main Content */}
            <Section className="px-12">
              <Heading className="text-gray-900 text-2xl font-bold leading-8 mt-0 mb-4">
                Welcome to Mirascope Cloud!
              </Heading>

              <Text className="text-gray-700 text-base leading-6 my-4">
                {greeting},
              </Text>

              <Text className="text-gray-700 text-base leading-6 my-4">
                I'm William, founder of Mirascope. Thank you for signing up!
                We're excited to have you building with us.
              </Text>

              <Text className="text-gray-700 text-base leading-6 my-4">
                To get you started, here are some helpful resources:
              </Text>

              {/* Resources Section */}
              <Section className="text-center my-6">
                <Button href="https://mirascope.com/docs">
                  View Documentation
                </Button>
              </Section>

              {/* Credit Incentive Program */}
              <Hr className="border-gray-200 my-8" />

              <Heading
                as="h2"
                className="text-gray-900 text-xl font-semibold leading-7 my-6"
              >
                Earn Up to $30 in Credits
              </Heading>

              <Text className="text-gray-700 text-base leading-6 my-4">
                We'd love to learn more about how you're using Mirascope. Here's
                how you can earn additional credits:
              </Text>

              <ul className="pl-5 my-4">
                <li className="mb-3">
                  <Text className="text-gray-700 text-base leading-6 my-2">
                    <strong>$5</strong> - Join our Discord and introduce
                    yourself
                  </Text>
                </li>
                <li className="mb-3">
                  <Text className="text-gray-700 text-base leading-6 my-2">
                    <strong>$5</strong> - Share your project in our
                    show-and-tell channel
                  </Text>
                </li>
                <li className="mb-3">
                  <Text className="text-gray-700 text-base leading-6 my-2">
                    <strong>$20</strong> - Schedule a user interview after using
                    your credits
                  </Text>
                </li>
              </ul>

              <Section className="text-center my-6">
                <Button href="https://mirascope.com/discord-invite">
                  Join Our Discord
                </Button>
              </Section>

              <Hr className="border-gray-200 my-8" />

              {/* Personal Touch */}
              <Text className="text-gray-700 text-base leading-6 my-4">
                Have questions or feedback? Just reply to this email - I read
                and respond to every message personally.
              </Text>

              <Text className="text-gray-700 text-base leading-6 my-8">
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
      </Tailwind>
    </Html>
  );
}

// Preview props for React Email dev server
WelcomeEmail.PreviewProps = {
  name: "John Doe",
} satisfies WelcomeEmailProps;

export default WelcomeEmail;
