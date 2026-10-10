import { deviceRoute } from "@/lib/api";
import { query } from "@/lib/db";
import { requireContract, success } from "@/lib/http";

export const runtime = "nodejs";

export async function POST(request: Request): Promise<Response> {
  return deviceRoute(request, "emptyObject", async (principal) => {
    const result = await query(
      `UPDATE devices SET last_seen_at = now()
        WHERE id = $1 AND user_id = $2 AND revoked_at IS NULL
        RETURNING last_seen_at`,
      [principal.id, principal.userId],
    );
    if (!result.rowCount) return Response.json(
      { schema_version: "1.0.3", error: { code: "device_revoked", message: "Device is no longer registered" } },
      { status: 401 },
    );
    return success({ last_seen_at: result.rows[0].last_seen_at });
  });
}
