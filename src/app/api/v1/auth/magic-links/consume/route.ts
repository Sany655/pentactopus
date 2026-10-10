import { randomUUID } from "node:crypto";
import { assertSameOrigin, SESSION_MAX_AGE_SECONDS, sessionCookie } from "@/lib/auth";
import { audit } from "@/lib/audit";
import { transaction } from "@/lib/db";
import { handle, HttpError, readJson, requireContract, success } from "@/lib/http";
import { enforceRateLimit, randomToken, sha256 } from "@/lib/security";

export const runtime = "nodejs";

export async function POST(request: Request): Promise<Response> {
  return handle(async () => {
    assertSameOrigin(request);
    await enforceRateLimit(request, "magic-link-consume", 10, 15 * 60);
    const { value } = await readJson(request, 16 * 1024);
    requireContract("magicLinkConsume", value);
    const token = (value as { token: string }).token;
    const sessionToken = randomToken(32);
    const sessionId = randomUUID();
    const result = await transaction(async (client) => {
      const consumed = await client.query<{ email: string }>(
        `UPDATE magic_link_tokens SET consumed_at = now()
          WHERE token_hash = $1 AND consumed_at IS NULL AND expires_at > now()
          RETURNING email`,
        [sha256(token)],
      );
      const email = consumed.rows[0]?.email;
      if (!email) throw new HttpError(400, "invalid_or_expired_link", "This sign-in link is invalid or expired");
      const user = await client.query<{ id: string; email: string }>(
        `INSERT INTO users (id, email) VALUES ($1, $2)
         ON CONFLICT (email) DO UPDATE SET email = EXCLUDED.email
           WHERE users.disabled_at IS NULL
         RETURNING id, email`,
        [randomUUID(), email],
      );
      if (!user.rows[0]) throw new HttpError(403, "account_unavailable", "This account is unavailable");
      await client.query("INSERT INTO user_settings (user_id) VALUES ($1) ON CONFLICT DO NOTHING", [user.rows[0].id]);
      await client.query(
        `INSERT INTO web_sessions (id, user_id, token_hash, expires_at)
         VALUES ($1, $2, $3, now() + ($4 * interval '1 second'))`,
        [sessionId, user.rows[0].id, sha256(sessionToken), SESSION_MAX_AGE_SECONDS],
      );
      await audit(user.rows[0].id, "auth.signed_in", null, null, {}, client);
      return user.rows[0];
    });
    const response = success({ user: result });
    response.headers.append("Set-Cookie", sessionCookie(sessionToken));
    return response;
  });
}
