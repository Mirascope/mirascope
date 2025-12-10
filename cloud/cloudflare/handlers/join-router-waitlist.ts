import { Resend } from "resend";

export async function joinRouterWaitlistHandler(
  request: Request,
  env: any,
): Promise<Response> {
  if (request.method !== "POST") {
    return new Response("Method not allowed", { status: 405 });
  }

  try {
    const { firstName, lastName, email } = (await request.json()) as {
      firstName: string;
      lastName: string;
      email: string;
    };

    const resend = new Resend(env.RESEND_API_KEY);

    await resend.contacts.create({
      email,
      firstName,
      lastName,
      unsubscribed: false,
      audienceId: env.RESEND_AUDIENCE_ID,
    });

    return new Response(JSON.stringify({ success: true }), {
      headers: { "Content-Type": "application/json" },
    });
  } catch (error) {
    return new Response(JSON.stringify({ error: "Failed to join waitlist" }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
}
