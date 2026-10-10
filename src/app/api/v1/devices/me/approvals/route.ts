import { deviceRoute } from "@/lib/api";
import { audit } from "@/lib/audit";
import { transaction } from "@/lib/db";
import { success } from "@/lib/http";

export const runtime = "nodejs";

export async function GET(request: Request): Promise<Response> {
  return deviceRoute(request, null, async (principal) => {
    const approvals = await transaction(async (client) => {
      const expired = await client.query<{ id: string; task_id: string; pipeline_id: string }>(
        `UPDATE approvals SET status = 'expired'
          WHERE user_id = $1 AND status IN ('pending', 'approved') AND expires_at <= now()
            AND task_id IN (
              SELECT id FROM tasks WHERE user_id = $1 AND status = 'awaiting_approval'
            )
          RETURNING id, task_id, (SELECT pipeline_id FROM tasks t WHERE t.id = approvals.task_id) AS pipeline_id`,
        [principal.userId],
      );
      if (expired.rowCount) {
        const taskIds = expired.rows.map((approval) => approval.task_id);
        await client.query(
          `UPDATE tasks SET status = 'failed', updated_at = now()
            WHERE user_id = $1 AND id = ANY($2::uuid[]) AND status = 'awaiting_approval'`,
          [principal.userId, taskIds],
        );
        await client.query(
          `UPDATE pipelines SET status = 'failed'
            WHERE user_id = $1 AND id = ANY($2::uuid[])`,
          [principal.userId, expired.rows.map((approval) => approval.pipeline_id)],
        );
        await client.query(
          `UPDATE pipeline_steps SET status = 'failed'
            WHERE user_id = $1 AND task_id = ANY($2::uuid[])`,
          [principal.userId, taskIds],
        );
        for (const approval of expired.rows) {
          await audit(principal.userId, "approval.expired", principal.id, approval.task_id, {
            approval_id: approval.id,
            status: "expired",
          }, client);
        }
      }
      const pending = await client.query(
        `SELECT a.id AS approval_id, a.task_id, encode(a.action_hash, 'hex') AS action_hash,
                a.tier, a.created_at, a.expires_at,
                a.requested_by_device_id, p.inbox_item_id AS preview_inbox_id
           FROM approval_packets p
           JOIN approvals a ON a.id = p.approval_id AND a.user_id = p.user_id
          WHERE p.user_id = $1 AND p.approver_device_id = $2
            AND a.status = 'pending' AND a.expires_at > now()
            AND EXISTS (
              SELECT 1 FROM inbox_items i
               WHERE i.id = p.inbox_item_id AND i.user_id = p.user_id
                 AND i.deleted_at IS NULL AND i.expires_at > now()
            )
          ORDER BY a.created_at`,
        [principal.userId, principal.id],
      );
      return pending.rows;
    });
    return success({ approvals });
  });
}
