import { deviceRoute, webRoute } from "@/lib/api";
import { query } from "@/lib/db";
import { success } from "@/lib/http";

export const runtime = "nodejs";

async function listDevices(userId: string): Promise<Response> {
  const result = await query(
    `SELECT id, name, platform, public_key, created_at, last_seen_at,
            CASE WHEN last_seen_at > now() - interval '30 seconds' THEN 'online' ELSE 'offline' END AS status
       FROM devices WHERE user_id = $1 AND revoked_at IS NULL ORDER BY created_at`,
    [userId],
  );
  return success({
    devices: result.rows.map((device) => ({
      ...device,
      public_key: Buffer.from(device.public_key).toString("base64url"),
    })),
  });
}

export async function GET(request: Request): Promise<Response> {
  if (request.headers.has("x-device-id")) {
    return deviceRoute(request, null, async (principal) => listDevices(principal.userId));
  }
  return webRoute(request, {}, async (principal) => listDevices(principal.id));
}
