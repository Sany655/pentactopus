export async function sendMagicLink(email: string, token: string): Promise<void> {
  const apiKey = process.env.RESEND_API_KEY;
  const from = process.env.RESEND_FROM_EMAIL;
  const origin = process.env.APP_ORIGIN;
  if (!apiKey || !from || !origin) {
    throw new Error("RESEND_API_KEY, RESEND_FROM_EMAIL, and APP_ORIGIN are required");
  }
  const link = new URL("/account/consume", origin);
  link.hash = `token=${encodeURIComponent(token)}`;
  const response = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      from,
      to: [email],
      subject: "Sign in to Pentactopus",
      text: `Confirm sign-in to Pentactopus using this one-time link:\n\n${link.toString()}\n\nIt expires in 15 minutes. If you did not request this, ignore this email.`,
    }),
    signal: AbortSignal.timeout(10_000),
  });
  if (!response.ok) {
    const safeStatus = response.status;
    throw new Error(`Magic-link delivery failed with status ${safeStatus}`);
  }
}
