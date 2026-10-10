import { webRoute } from "@/lib/api";
import { query } from "@/lib/db";
import { HttpError, success } from "@/lib/http";

export const runtime = "nodejs";

export async function GET(request: Request): Promise<Response> {
  const url = new URL(request.url);
  const rawLimit = url.searchParams.get("limit") ?? "50";
  const limit = Number(rawLimit);
  if (!/^\d{1,3}$/.test(rawLimit) || limit < 1 || limit > 100) {
    return Response.json(
      { schema_version: "1.0.3", error: { code: "invalid_limit", message: "Limit must be between 1 and 100" } },
      { status: 400 },
    );
  }
  const cursor = url.searchParams.get("cursor");
  if (cursor && !/^[1-9]\d{0,18}$/.test(cursor)) {
    return Response.json(
      { schema_version: "1.0.3", error: { code: "invalid_cursor", message: "Cursor is invalid" } },
      { status: 400 },
    );
  }
  return webRoute(request, {}, async (principal) => {
    const result = await query(
      `SELECT id::text AS cursor, event_type, metadata, created_at, actor_device_id, task_id
         FROM audit_events
        WHERE user_id = $1 AND ($2::bigint IS NULL OR id < $2::bigint)
        ORDER BY id DESC LIMIT $3`,
      [principal.id, cursor, limit + 1],
    );
    const hasMore = result.rows.length > limit;
    const events = result.rows.slice(0, limit);
    const nextCursor = hasMore ? events.at(-1)?.cursor ?? null : null;
    return success({ events, next_cursor: nextCursor });
  });
}
