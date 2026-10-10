import { deviceRoute } from "@/lib/api";
import { audit } from "@/lib/audit";
import { transaction } from "@/lib/db";
import { success } from "@/lib/http";
import { taskEnvelope, type TaskRow } from "@/lib/tasks";
import { validateTaskEnvelope } from "@/lib/contracts";

export const runtime = "nodejs";

export async function GET(request: Request): Promise<Response> {
  return deviceRoute(request, null, async (principal) => {
    const tasks = await transaction(async (client) => {
      const expired = await client.query<{ id: string; pipeline_id: string }>(
        `UPDATE tasks SET status = 'expired', updated_at = now()
          WHERE user_id = $1 AND target_device_id = $2
            AND status IN ('queued', 'claimed', 'awaiting_approval', 'running')
            AND expires_at <= now()
          RETURNING id, pipeline_id`,
        [principal.userId, principal.id],
      );
      if (expired.rowCount) {
        await client.query(
          `UPDATE approvals SET status = 'expired'
            WHERE user_id = $1 AND task_id = ANY($2::uuid[])
              AND status IN ('pending', 'approved')`,
          [principal.userId, expired.rows.map((row) => row.id)],
        );
        await client.query(
          `UPDATE pipeline_steps SET status = 'expired'
            WHERE user_id = $1 AND task_id = ANY($2::uuid[])`,
          [principal.userId, expired.rows.map((row) => row.id)],
        );
        await client.query(
          `UPDATE pipelines SET status = 'expired'
            WHERE user_id = $1 AND id = ANY($2::uuid[])`,
          [principal.userId, expired.rows.map((row) => row.pipeline_id)],
        );
        for (const row of expired.rows) {
          await audit(principal.userId, "task.expired", principal.id, row.id, { status: "expired" }, client);
        }
      }
      const queued = await client.query<TaskRow>(
        `SELECT id, root_task_id, parent_task_id, origin_device_id,
                orchestrator_device_id, target_device_id, hop_path, depth,
                turn_count, capability, body, input_refs, requires_confirmation,
                status, expires_at
           FROM tasks
          WHERE user_id = $1 AND target_device_id = $2
            AND status = 'queued' AND expires_at > now()
          ORDER BY created_at LIMIT 25`,
        [principal.userId, principal.id],
      );
      const active = await client.query<TaskRow>(
        `SELECT id, root_task_id, parent_task_id, origin_device_id,
                orchestrator_device_id, target_device_id, hop_path, depth,
                turn_count, capability, body, input_refs, requires_confirmation,
                status, expires_at
           FROM tasks
          WHERE user_id = $1 AND target_device_id = $2
            AND status IN ('claimed', 'awaiting_approval', 'running')
          ORDER BY updated_at`,
        [principal.userId, principal.id],
      );
      return { queued: queued.rows.map(taskEnvelope), active: active.rows.map(taskEnvelope) };
    });
    for (const task of [...tasks.queued, ...tasks.active]) {
      if (!validateTaskEnvelope(task)) throw new Error("Stored task does not match the task envelope contract");
    }
    return success({
      tasks: tasks.queued,
      active_task_updates: tasks.active,
      next_cursor: null,
      server_time: new Date().toISOString(),
    });
  });
}
