import { randomUUID } from "node:crypto";
import { NextRequest } from "next/server";
import { enforceRateLimit, randomToken, sha256 } from "@/lib/security";
import { query } from "@/lib/db";
import { sendMagicLink } from "@/lib/email";
import { handle, HttpError, readJson, requireContract, success } from "@/lib/http";

export const runtime = "nodejs";

export async function POST(request: NextRequest): Promise<Response> {
  return handle(async () => {
    const { value } = await readJson(request, 16 * 1024);
    requireContract("magicLinkRequest", value);
    const email = (value as { email: string }).email.trim().toLowerCase();
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      throw new HttpError(400, "invalid_email", "Enter a valid email address");
    }
    await enforceRateLimit(request, "magic-link-ip", 5, 15 * 60);
    await enforceRateLimit(request, "magic-link-email", 3, 60 * 60, email);

    const token = randomToken(32);
    const tokenId = randomUUID();
    await query(
      `INSERT INTO magic_link_tokens (id, email, token_hash, expires_at)
       VALUES ($1, $2, $3, now() + interval '15 minutes')`,
      [tokenId, email, sha256(token)],
    );
    try {
      await sendMagicLink(email, token);
    } catch (error) {
      await query("DELETE FROM magic_link_tokens WHERE id = $1 AND consumed_at IS NULL", [tokenId]);
      console.error("Magic-link email delivery failed", error);
    }
    return success({ accepted: true }, 202);
  });
}
