import { deviceRoute, webRoute } from "@/lib/api";
import { audit } from "@/lib/audit";
import { transaction, query } from "@/lib/db";
import { success } from "@/lib/http";

export const runtime = "nodejs";

async function readSettings(userId: string): Promise<Response> {
  const result = await query(
    `SELECT message_presentation, updated_at
       FROM user_settings WHERE user_id = $1`,
    [userId],
  );
  return success({ settings: result.rows[0] ?? { message_presentation: "full", updated_at: null } });
}

async function writeSettings(
  userId: string,
  actorDeviceId: string | null,
  body: { message_presentation: "full" | "summary" },
): Promise<Response> {
  const result = await transaction(async (client) => {
    const updated = await client.query(
      `INSERT INTO user_settings (user_id, message_presentation, updated_at)
       VALUES ($1, $2, now())
       ON CONFLICT (user_id) DO UPDATE
         SET message_presentation = EXCLUDED.message_presentation, updated_at = now()
       RETURNING message_presentation, updated_at`,
      [userId, body.message_presentation],
    );
    await audit(userId, "settings.updated", actorDeviceId, null, {
      message_presentation: body.message_presentation,
    }, client);
    return updated.rows[0];
  });
  return success({ settings: result });
}

export async function GET(request: Request): Promise<Response> {
  if (request.headers.has("x-device-id")) {
    return deviceRoute(request, null, async (principal) => readSettings(principal.userId));
  }
  return webRoute(request, {}, async (principal) => readSettings(principal.id));
}

export async function PUT(request: Request): Promise<Response> {
  if (request.headers.has("x-device-id")) {
    return deviceRoute(request, "settingsUpdate", async (principal, body) => (
      writeSettings(principal.userId, principal.id, body as { message_presentation: "full" | "summary" })
    ));
  }
  return webRoute(request, { mutation: true, schema: "settingsUpdate" }, async (principal, body) => (
    writeSettings(principal.id, null, body as { message_presentation: "full" | "summary" })
  ));
}
