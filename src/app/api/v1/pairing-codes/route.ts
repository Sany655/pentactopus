import { randomUUID } from "node:crypto";
import { webRoute } from "@/lib/api";
import { audit } from "@/lib/audit";
import { transaction } from "@/lib/db";
import { success } from "@/lib/http";
import { enforceRateLimit, randomToken, sha256 } from "@/lib/security";

export const runtime = "nodejs";

export async function POST(request: Request): Promise<Response> {
  return webRoute(request, { mutation: true, schema: "emptyObject" }, async (principal) => {
    await enforceRateLimit(request, "pairing-create", 10, 60 * 60, principal.id);
    const code = randomToken(12);
    const id = randomUUID();
    const expiresAt = new Date(Date.now() + 10 * 60_000);
    await transaction(async (client) => {
      await client.query(
        `INSERT INTO pairing_codes (id, user_id, code_hash, expires_at)
         VALUES ($1, $2, $3, $4)`,
        [id, principal.id, sha256(code), expiresAt],
      );
      await audit(principal.id, "pairing.created", null, null, {
        expires_at: expiresAt.toISOString(),
      }, client);
    });
    return success({ pairing_code: code, expires_at: expiresAt.toISOString() }, 201);
  });
}
