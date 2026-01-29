/**
 * @fileoverview Invitation email template for organization team members.
 *
 * Sent when OWNER/ADMIN invites a user to join their organization.
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

import { Button } from "@/emails/templates/components/button";
import { Footer } from "@/emails/templates/components/footer";
import { Logo } from "@/emails/templates/components/logo";

interface InvitationEmailProps {
  senderName: string;
  organizationName: string;
  recipientEmail: string;
  role: "ADMIN" | "MEMBER";
  acceptUrl: string;
  expiresAt: Date;
}

const roleDescriptions: Record<"ADMIN" | "MEMBER", string> = {
  ADMIN: "administrative access to manage members and settings",
  MEMBER: "access to view and work with organization resources",
};

/**
 * Invitation email template.
 *
 * Features:
 * - Personal greeting from sender
 * - Clear call-to-action button
 * - Role description
 * - Expiration notice
 * - Security notice about invitation link
 */
export function InvitationEmail({
  senderName,
  organizationName,
  recipientEmail,
  role,
  acceptUrl,
  expiresAt,
}: InvitationEmailProps) {
  const roleDescription = roleDescriptions[role];
  const expiresInDays = Math.ceil(
    (expiresAt.getTime() - Date.now()) / (1000 * 60 * 60 * 24),
  );

  return (
    <Html>
      <Head />
      <Preview>
        {senderName} invited you to join {organizationName} on Mirascope
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
                You've Been Invited!
              </Heading>

              <Text className="text-gray-700 text-base leading-6 my-4">
                <strong>{senderName}</strong> has invited you to join{" "}
                <strong>{organizationName}</strong> on Mirascope.
              </Text>

              <Text className="text-gray-700 text-base leading-6 my-4">
                As a <strong>{role}</strong>, you'll have {roleDescription}.
              </Text>

              {/* CTA Button */}
              <Section className="text-center my-8">
                <Button href={acceptUrl}>Accept Invitation</Button>
              </Section>

              <Hr className="border-gray-200 my-8" />

              {/* Additional Info */}
              <Text className="text-gray-600 text-sm leading-5 my-2">
                This invitation was sent to <strong>{recipientEmail}</strong>{" "}
                and will expire in {expiresInDays} day
                {expiresInDays !== 1 ? "s" : ""}.
              </Text>

              <Text className="text-gray-600 text-sm leading-5 my-2">
                If you don't have a Mirascope account yet, clicking the button
                above will prompt you to create one.
              </Text>

              <Hr className="border-gray-200 my-8" />

              {/* Security Notice */}
              <Text className="text-gray-600 text-xs leading-tight my-4 p-3 bg-gray-50 rounded">
                <strong>Security Notice:</strong> This invitation link is unique
                to you. Do not share it with others. If you did not expect this
                invitation, you can safely ignore this email.
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
InvitationEmail.PreviewProps = {
  senderName: "Alice Smith",
  organizationName: "Acme Corporation",
  recipientEmail: "bob.johnson@example.com",
  role: "MEMBER",
  acceptUrl: "https://app.mirascope.com/invitations/accept?token=abc123xyz",
  expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
} satisfies InvitationEmailProps;

export default InvitationEmail;
