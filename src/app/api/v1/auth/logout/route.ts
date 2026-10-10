import { assertSameOrigin, clearSessionCookie, readSessionToken, requireSession } from "@/lib/auth";
import { query } from "@/lib/db";
import { handle, success } from "@/lib/http";
import { sha256 } from "@/lib/security";

export const runtime = "nodejs";

export async function POST(request: Request): Promise<Response> {
  return handle(async () => {
    assertSameOrigin(request);
    const principal = await requireSession(request);
    const token = readSessionToken(request);
    if (token) {
      await query(
        "UPDATE web_sessions SET revoked_at = now() WHERE user_id = $1 AND token_hash = $2 AND revoked_at IS NULL",
        [principal.id, sha256(token)],
      );
    }
    const response = success({ signed_out: true });
    response.headers.append("Set-Cookie", clearSessionCookie());
    return response;
  });
}
