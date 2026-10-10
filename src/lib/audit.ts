import { query } from "./db";
import type { PoolClient } from "@neondatabase/serverless";

const ALLOWED_METADATA = new Set([
  "count",
  "target_device_id",
  "source_device_id",
  "status",
  "tier",
  "byte_length",
  "expires_at",
  "device_name",
  "platform",
  "message_presentation",
  "approval_id",
  "artifact_id",
  "inbox_id",
  "turn_count",
]);

export async function audit(
  userId: string,
  eventType: string,
  actorDeviceId: string | null,
  taskId: string | null,
  metadata: Record<string, string | number | boolean | null> = {},
  client?: PoolClient,
): Promise<void> {
  if (Object.keys(metadata).some((key) => !ALLOWED_METADATA.has(key))) {
    throw new Error("Audit metadata contains a non-allowlisted field");
  }
  const sql = client?.query.bind(client) ?? query;
  await sql(
    `INSERT INTO audit_events (user_id, actor_device_id, task_id, event_type, metadata)
     VALUES ($1, $2, $3, $4, $5::jsonb)`,
    [userId, actorDeviceId, taskId, eventType, JSON.stringify(metadata)],
  );
}
