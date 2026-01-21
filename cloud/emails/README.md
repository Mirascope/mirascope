# Emails

This directory contains email templates and related services for Mirascope Cloud, built with [React Email](https://react.email/).

## Directory Structure

- `templates/` - Email templates built with React Email components
- `client.ts` - Email client for sending emails (Resend wrapper)
- `service.ts` - Email service layer
- `render.tsx` - Email rendering utilities
- `audience.ts` - Audience management for email campaigns

## Testing Email Templates

To preview and test changes to email templates locally:

```bash
bun run email:dev
```

This command (defined in `package.json:24`) starts the React Email preview server at `http://localhost:3333`, allowing you to:

- Preview all email templates in the browser
- See real-time updates as you edit templates
- Test templates with different data
- View both HTML and plain text versions

### From Repository Root

If you're in the repository root, use:

```bash
cd cloud && bun run email:dev
```

## Creating New Templates

1. Create a new `.tsx` file in `templates/`
2. Build your template using `@react-email/components`
3. Export the component and add it to `templates/index.ts`
4. Test using the preview server
5. Add tests in a corresponding `.test.tsx` file

## Sending Emails

Email sending is handled through the Effect-based `Emails` client (wrapper around Resend):

```typescript
import { Emails } from "./client";

// Send an email
Effect.gen(function* () {
  const emails = yield* Emails;
  yield* emails.send({
    to: "user@example.com",
    subject: "Welcome!",
    react: <WelcomeEmail name="User" />,
  });
});
```
