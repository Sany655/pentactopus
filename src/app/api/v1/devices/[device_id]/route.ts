import { webRoute } from "@/lib/api";
import { audit } from "@/lib/audit";
import { transaction, query } from "@/lib/db";
import { HttpError, requireUuid, success } from "@/lib/http";
import { redis } from "@/lib/redis";

export const runtime = "nodejs";

type Context = { params: Promise<{ device_id: string }> };

export async function PATCH(request: Request, context: Context): Promise<Response> {
  const { device_id: deviceId } = await context.params;
  return webRoute(request, { mutation: true, schema: "deviceRename" }, async (principal, body) => {
    requireUuid(deviceId);
    const name = (body as { name: string }).name.trim();
    if (!/^[A-Za-z0-9][A-Za-z0-9 ._-]{0,79}$/.test(name)) {
      throw new HttpError(400, "invalid_device_name", "Device name is invalid");
    }
    try {
      const result = await query(
        `UPDATE devices SET name = $3
          WHERE user_id = $1 AND id = $2 AND revoked_at IS NULL
          RETURNING id, name, platform`,
        [principal.id, deviceId, name],
      );
      if (!result.rowCount) throw new HttpError(404, "not_found", "Device not found");
      await audit(principal.id, "device.renamed", null, null, { device_name: name });
      return success({ device: result.rows[0] });
    } catch (error) {
      if ((error as { code?: string }).code === "23505") {
        throw new HttpError(409, "device_name_conflict", "A device with that name already exists");
      }
      throw error;
    }
  });
}

export async function DELETE(request: Request, context: Context): Promise<Response> {
  const { device_id: deviceId } = await context.params;
  return webRoute(request, { mutation: true, schema: "emptyObject" }, async (session) => {
    requireUuid(deviceId);
    const revoked = await transaction(async (client) => {
      const result = await client.query<{ name: string }>(
        `UPDATE devices SET revoked_at = now()
          WHERE user_id = $1 AND id = $2 AND revoked_at IS NULL
          RETURNING name`,
        [session.id, deviceId],
      );
      if (!result.rows[0]) throw new HttpError(404, "not_found", "Device not found");
      const tasks = await client.query<{ id: string; pipeline_id: string }>(
        `UPDATE tasks SET status = 'failed', updated_at = now()
          WHERE user_id = $1 AND target_device_id = $2
            AND status IN ('queued', 'claimed', 'awaiting_approval', 'running')
          RETURNING id, pipeline_id`,
        [session.id, deviceId],
      );
      const taskIds = tasks.rows.map((task) => task.id);
      await client.query(
        `UPDATE approvals SET status = 'expired'
          WHERE user_id = $1 AND status IN ('pending', 'approved')
            AND task_id = ANY($2::uuid[])`,
        [session.id, taskIds],
      );
      await client.query(
        `UPDATE pipelines SET status = 'failed'
          WHERE user_id = $1 AND id = ANY($2::uuid[])`,
        [session.id, tasks.rows.map((task) => task.pipeline_id)],
      );
      await client.query(
        `UPDATE pipeline_steps SET status = 'failed'
          WHERE user_id = $1 AND task_id = ANY($2::uuid[])`,
        [session.id, taskIds],
      );
      await audit(session.id, "device.revoked", null, null, { device_name: result.rows[0].name }, client);
      return {
        name: result.rows[0].name,
        taskIds,
      };
    });
    const blobs = await query<{ redis_key: string }>(
      `SELECT redis_key FROM inbox_items
        WHERE user_id = $1 AND (source_device_id = $2 OR target_device_id = $2)
          AND deleted_at IS NULL
       UNION ALL
       SELECT redis_key FROM artifacts
        WHERE user_id = $1 AND (created_by_device_id = $2 OR intended_device_id = $2)
          AND deleted_at IS NULL`,
      [session.id, deviceId],
    );
    const keys = blobs.rows.map((blob) => blob.redis_key);
    for (let offset = 0; offset < keys.length; offset += 100) {
      await redis().del(...keys.slice(offset, offset + 100));
    }
    await query(
      `UPDATE inbox_items SET deleted_at = now()
        WHERE user_id = $1 AND (source_device_id = $2 OR target_device_id = $2)
          AND deleted_at IS NULL`,
      [session.id, deviceId],
    );
    await query(
      `UPDATE artifacts SET deleted_at = now()
        WHERE user_id = $1 AND (created_by_device_id = $2 OR intended_device_id = $2)
          AND deleted_at IS NULL`,
      [session.id, deviceId],
    );
    return success({ revoked: true, device_name: revoked.name, failed_task_count: revoked.taskIds.length });
  });
}
