import { randomUUID } from "node:crypto";
import { audit } from "@/lib/audit";
import { transaction } from "@/lib/db";
import { handle, HttpError, readJson, requireContract, success } from "@/lib/http";
import { enforceRateLimit, sha256 } from "@/lib/security";

export const runtime = "nodejs";

export async function POST(request: Request): Promise<Response> {
  return handle(async () => {
    await enforceRateLimit(request, "device-register", 10, 60 * 60);
    const { value } = await readJson(request, 16 * 1024);
    requireContract("deviceRegistration", value);
    const input = value as {
      pairing_code: string;
      name: string;
      platform: "windows" | "android";
      public_key: string;
    };
    const name = input.name.trim();
    if (!/^[A-Za-z0-9][A-Za-z0-9 ._-]{0,79}$/.test(name)) {
      throw new HttpError(400, "invalid_device_name", "Device name is invalid");
    }
    const publicKey = Buffer.from(input.public_key, "base64url");
    if (publicKey.byteLength !== 32 || publicKey.toString("base64url") !== input.public_key) {
      throw new HttpError(400, "invalid_public_key", "Ed25519 public key is invalid");
    }
    const deviceId = randomUUID();
    try {
      await transaction(async (client) => {
      const pairing = await client.query<{ user_id: string }>(
        `UPDATE pairing_codes SET consumed_at = now()
          WHERE code_hash = $1 AND consumed_at IS NULL AND expires_at > now()
            AND EXISTS (
              SELECT 1 FROM users u
               WHERE u.id = pairing_codes.user_id AND u.disabled_at IS NULL
            )
          RETURNING user_id`,
        [sha256(input.pairing_code)],
      );
      const userId = pairing.rows[0]?.user_id;
      if (!userId) throw new HttpError(400, "invalid_pairing_code", "Pairing code is invalid or expired");
      await client.query(
        `INSERT INTO devices (id, user_id, name, platform, public_key)
         VALUES ($1, $2, $3, $4, $5)`,
        [deviceId, userId, name, input.platform, publicKey],
      );
      await audit(userId, "device.registered", deviceId, null, {
        device_name: name,
        platform: input.platform,
      }, client);
      });
    } catch (error) {
      if ((error as { code?: string }).code === "23505") {
        throw new HttpError(409, "device_name_conflict", "A device with that name already exists");
      }
      throw error;
    }
    return success({ device_id: deviceId, name }, 201);
  });
}
