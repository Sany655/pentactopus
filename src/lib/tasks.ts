import { randomUUID } from "node:crypto";
import type { PoolClient } from "@neondatabase/serverless";
import { audit } from "./audit";
import { query, transaction } from "./db";
import { HttpError } from "./http";
import { appendDelegation, canTransition, initialTaskPath, type TaskStatus } from "./task-rules";
import { validateApiPayload } from "./contracts";

export type { TaskStatus } from "./task-rules";

export type TaskRow = {
  id: string;
  root_task_id: string;
  parent_task_id: string | null;
  origin_device_id: string;
  orchestrator_device_id: string;
  target_device_id: string;
  hop_path: string[];
  depth: number;
  turn_count: number;
  capability: string;
  body: Record<string, unknown>;
  input_refs: string[];
  requires_confirmation: boolean;
  status: TaskStatus;
  expires_at: Date;
};

export type TaskEnvelope = {
  schema_version: "1.0.3";
  task_id: string;
  root_task_id: string;
  parent_task_id: string | null;
  origin_device_id: string;
  orchestrator_device_id: string;
  target_device_id: string;
  hop_path: string[];
  depth: number;
  turn_count: number;
  capability: string;
  body: Record<string, unknown>;
  input_refs: string[];
  requires_confirmation: boolean;
  status: TaskStatus;
  expires_at: string;
};

export function taskEnvelope(row: TaskRow): TaskEnvelope {
  return {
    schema_version: "1.0.3",
    task_id: row.id,
    root_task_id: row.root_task_id,
    parent_task_id: row.parent_task_id,
    origin_device_id: row.origin_device_id,
    orchestrator_device_id: row.orchestrator_device_id,
    target_device_id: row.target_device_id,
    hop_path: row.hop_path,
    depth: row.depth,
    turn_count: row.turn_count,
    capability: row.capability,
    body: row.body,
    input_refs: row.input_refs,
    requires_confirmation: row.requires_confirmation,
    status: row.status,
    expires_at: new Date(row.expires_at).toISOString(),
  };
}

async function selectTask(
  client: PoolClient,
  userId: string,
  taskId: string,
  lock = false,
): Promise<TaskRow> {
  const result = await client.query<TaskRow>(
    `SELECT id, root_task_id, parent_task_id, origin_device_id,
            orchestrator_device_id, target_device_id, hop_path, depth,
            turn_count, capability, body, input_refs, requires_confirmation,
            status, expires_at
       FROM tasks
      WHERE user_id = $1 AND id = $2${lock ? " FOR UPDATE" : ""}`,
    [userId, taskId],
  );
  if (!result.rows[0]) throw new HttpError(404, "not_found", "Task not found");
  return result.rows[0];
}

export async function getOwnedTask(userId: string, taskId: string): Promise<TaskEnvelope> {
  return transaction(async (client) => {
    const expired = await client.query<{ pipeline_id: string }>(
      `UPDATE tasks SET status = 'expired', updated_at = now()
        WHERE user_id = $1 AND id = $2 AND expires_at <= now()
          AND status IN ('queued', 'claimed', 'awaiting_approval', 'running')
        RETURNING pipeline_id`,
      [userId, taskId],
    );
    if (expired.rowCount) {
      await client.query("UPDATE approvals SET status = 'expired' WHERE user_id = $1 AND task_id = $2 AND status IN ('pending', 'approved')", [userId, taskId]);
      await client.query("UPDATE pipelines SET status = 'expired' WHERE user_id = $1 AND id = $2", [userId, expired.rows[0].pipeline_id]);
      await client.query("UPDATE pipeline_steps SET status = 'expired' WHERE user_id = $1 AND task_id = $2", [userId, taskId]);
      await audit(userId, "task.expired", null, taskId, { status: "expired" }, client);
    }
    const result = await client.query<TaskRow>(
      `SELECT id, root_task_id, parent_task_id, origin_device_id,
              orchestrator_device_id, target_device_id, hop_path, depth,
              turn_count, capability, body, input_refs, requires_confirmation,
              status, expires_at
         FROM tasks WHERE user_id = $1 AND id = $2`,
      [userId, taskId],
    );
    if (!result.rows[0]) throw new HttpError(404, "not_found", "Task not found");
    return taskEnvelope(result.rows[0]);
  });
}

export async function createTask(
  principal: { id: string; userId: string },
  input: {
    target_device_id: string;
    parent_task_id?: string;
    capability: string;
    body: Record<string, unknown>;
    input_refs: string[];
    requires_confirmation: boolean;
    expires_at: string;
  },
): Promise<TaskEnvelope> {
  assertMetadataOnlyBody(input.body);
  const expiryMs = Date.parse(input.expires_at);
  const now = Date.now();
  if (!Number.isFinite(expiryMs) || expiryMs <= now || expiryMs > now + 24 * 60 * 60 * 1000) {
    throw new HttpError(400, "invalid_expiry", "Task expiry must be within the next 24 hours");
  }

  function assertMetadataOnlyBody(body: Record<string, unknown>): void {
    const encoded = JSON.stringify(body);
    if (Buffer.byteLength(encoded, "utf8") > 16 * 1024) {
      throw new HttpError(413, "task_body_too_large", "Task metadata must not exceed 16 KiB");
    }
    if (!validateApiPayload("taskBody", body)) {
      throw new HttpError(400, "plaintext_not_allowed", "Task body must contain only typed metadata; content must be encrypted in artifacts");
    }
  }
  return transaction(async (client) => {
    const target = await client.query(
      `SELECT id FROM devices WHERE id = $1 AND user_id = $2 AND revoked_at IS NULL`,
      [input.target_device_id, principal.userId],
    );
    if (!target.rowCount) throw new HttpError(404, "not_found", "Target device not found");

    let rootTaskId: string;
    let pipelineId: string;
    let parent: TaskRow | undefined;
    let path: string[];
    let depth: number;
    let originDeviceId = principal.id;
    let orchestratorDeviceId = principal.id;
    const taskId = randomUUID();

    if (input.parent_task_id) {
      parent = await selectTask(client, principal.userId, input.parent_task_id, true);
      if (
        parent.target_device_id !== principal.id
        || !["claimed", "running"].includes(parent.status)
      ) {
        throw new HttpError(409, "parent_not_delegable", "Parent task cannot delegate work");
      }
      const delegatedPath = appendDelegation(parent.hop_path, parent.depth, input.target_device_id);
      if (!delegatedPath) {
        throw new HttpError(409, "delegation_limit", "Target is already in the task path or depth limit is reached");
      }
      path = delegatedPath.hopPath;
      depth = delegatedPath.depth;
      rootTaskId = parent.root_task_id;
      pipelineId = (await client.query<{ pipeline_id: string }>(
        "SELECT pipeline_id FROM tasks WHERE user_id = $1 AND id = $2",
        [principal.userId, parent.id],
      )).rows[0].pipeline_id;
      originDeviceId = parent.origin_device_id;
      orchestratorDeviceId = parent.orchestrator_device_id;
    } else {
      ({ hopPath: path, depth } = initialTaskPath(principal.id, input.target_device_id));
      rootTaskId = taskId;
      pipelineId = randomUUID();
      await client.query(
        `INSERT INTO pipelines
          (id, user_id, root_task_id, orchestrator_device_id, turn_count, max_turns, expires_at)
         VALUES ($1, $2, $3, $4, 0, 20, $5)`,
        [pipelineId, principal.userId, rootTaskId, principal.id, new Date(expiryMs)],
      );
    }

    if (input.input_refs.length) {
      const refs = await client.query(
        `SELECT id FROM artifacts
          WHERE user_id = $1 AND id = ANY($2::uuid[])
            AND deleted_at IS NULL AND expires_at > now()
            AND (intended_device_id IS NULL OR intended_device_id = $3)`,
        [principal.userId, input.input_refs, input.target_device_id],
      );
      if (refs.rowCount !== input.input_refs.length) {
        throw new HttpError(404, "not_found", "One or more input artifacts are unavailable");
      }
    }

    const pipeline = await client.query<{ turn_count: number; expires_at: Date }>(
      `UPDATE pipelines
          SET turn_count = turn_count + 1,
              status = CASE WHEN status = 'queued' THEN 'running'::pipeline_status ELSE status END
        WHERE id = $1 AND user_id = $2 AND turn_count < max_turns
          AND expires_at > now() AND status NOT IN ('done', 'failed', 'rejected', 'expired')
        RETURNING turn_count, expires_at`,
      [pipelineId, principal.userId],
    );
    if (!pipeline.rowCount) throw new HttpError(409, "turn_limit", "Pipeline is expired or reached its turn limit");
    const taskExpiry = new Date(Math.min(expiryMs, new Date(pipeline.rows[0].expires_at).getTime()));
    if (taskExpiry.getTime() <= Date.now()) {
      throw new HttpError(409, "pipeline_expired", "Pipeline expiry has passed");
    }

    await client.query(
      `INSERT INTO tasks
        (id, user_id, pipeline_id, root_task_id, parent_task_id, origin_device_id,
         orchestrator_device_id, target_device_id, hop_path, depth, turn_count,
         capability, body, input_refs, requires_confirmation, expires_at)
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9::uuid[], $10, $11,
               $12, $13::jsonb, $14::uuid[], $15, $16)`,
      [
        taskId,
        principal.userId,
        pipelineId,
        rootTaskId,
        parent?.id ?? null,
        originDeviceId,
        orchestratorDeviceId,
        input.target_device_id,
        path,
        depth,
        pipeline.rows[0].turn_count,
        input.capability,
        JSON.stringify(input.body),
        input.input_refs,
        input.requires_confirmation,
        taskExpiry,
      ],
    );
    await client.query(
      `INSERT INTO pipeline_steps (user_id, pipeline_id, step_index, task_id, target_device_id, status)
       VALUES ($1, $2, $3, $4, $5, 'queued')`,
      [
        principal.userId,
        pipelineId,
        pipeline.rows[0].turn_count - 1,
        taskId,
        input.target_device_id,
      ],
    );
    await audit(principal.userId, "task.created", principal.id, taskId, {
      target_device_id: input.target_device_id,
      turn_count: pipeline.rows[0].turn_count,
      status: "queued",
      expires_at: taskExpiry.toISOString(),
    }, client);
    const row = await selectTask(client, principal.userId, taskId);
    return taskEnvelope(row);
  });
}

export async function claimTask(
  principal: { id: string; userId: string },
  taskId: string,
): Promise<TaskEnvelope | null> {
  try {
    return await transaction(async (client) => {
      const result = await client.query<TaskRow>(
        `UPDATE tasks t
            SET status = 'claimed', claimed_at = now(), updated_at = now()
          WHERE t.id = $1 AND t.user_id = $2 AND t.target_device_id = $3
            AND t.status = 'queued' AND t.expires_at > now()
            AND NOT EXISTS (
              SELECT 1 FROM tasks active
               WHERE active.target_device_id = t.target_device_id
                 AND active.status IN ('claimed', 'awaiting_approval', 'running')
            )
          RETURNING t.id, t.root_task_id, t.parent_task_id, t.origin_device_id,
                    t.orchestrator_device_id, t.target_device_id, t.hop_path, t.depth,
                    t.turn_count, t.capability, t.body, t.input_refs, t.requires_confirmation,
                    t.status, t.expires_at`,
        [taskId, principal.userId, principal.id],
      );
      if (!result.rowCount) return null;
      await client.query(
        "UPDATE pipeline_steps SET status = 'claimed' WHERE user_id = $1 AND task_id = $2",
        [principal.userId, taskId],
      );
      await audit(principal.userId, "task.claimed", principal.id, taskId, { status: "claimed" }, client);
      return taskEnvelope(result.rows[0]);
    });
  } catch (error) {
    if ((error as { code?: string }).code === "23505") {
      throw new HttpError(409, "device_busy", "This device is already running a task");
    }
    throw error;
  }
}

export async function transitionTask(
  principal: { id: string; userId: string },
  taskId: string,
  input: {
    status: TaskStatus;
    outcome_code?: string;
    approval_id?: string;
    action_hash?: string;
    local_confirmation?: boolean;
  },
): Promise<TaskEnvelope> {
  return transaction(async (client) => {
    const task = await selectTask(client, principal.userId, taskId, true);
    if (task.target_device_id !== principal.id) throw new HttpError(404, "not_found", "Task not found");
    if (
      new Date(task.expires_at).getTime() <= Date.now()
      && ["queued", "claimed", "awaiting_approval", "running"].includes(task.status)
    ) {
      await client.query(
        `UPDATE tasks SET status = 'expired', updated_at = now()
          WHERE user_id = $1 AND id = $2`,
        [principal.userId, taskId],
      );
      await client.query(
        `UPDATE approvals SET status = 'expired'
          WHERE user_id = $1 AND task_id = $2 AND status IN ('pending', 'approved')`,
        [principal.userId, taskId],
      );
      await client.query(
        `UPDATE pipelines SET status = 'expired'
          WHERE user_id = $1 AND id = (SELECT pipeline_id FROM tasks WHERE user_id = $1 AND id = $2)`,
        [principal.userId, taskId],
      );
      await client.query(
        "UPDATE pipeline_steps SET status = 'expired' WHERE user_id = $1 AND task_id = $2",
        [principal.userId, taskId],
      );
      await audit(principal.userId, "task.expired", principal.id, taskId, { status: "expired" }, client);
      return taskEnvelope({ ...task, status: "expired" });
    }
    if (!canTransition(task.status, input.status)) {
      throw new HttpError(409, "invalid_transition", "Task status transition is not allowed");
    }
    if (input.status === "running" && (task.requires_confirmation || task.status === "awaiting_approval")) {
      if (!input.approval_id || !input.action_hash) {
        throw new HttpError(403, "approval_required", "A valid approval is required before execution");
      }
      const used = await client.query<{ tier: number }>(
        `UPDATE approvals
            SET status = 'used', used_at = now()
          WHERE id = $1 AND user_id = $2 AND task_id = $3
            AND action_hash = decode($4, 'hex') AND status = 'approved'
            AND expires_at > now()
          RETURNING tier`,
        [input.approval_id, principal.userId, taskId, input.action_hash],
      );
      if (!used.rowCount) throw new HttpError(403, "approval_invalid", "Approval is missing, expired, or already used");
      if (used.rows[0].tier === 5 && input.local_confirmation !== true) {
        throw new HttpError(403, "local_confirmation_required", "The executing device must confirm this action locally");
      }
    }
    const result = await client.query<TaskRow>(
      `UPDATE tasks SET status = $3, outcome_code = $4, updated_at = now()
        WHERE id = $1 AND user_id = $2
        RETURNING id, root_task_id, parent_task_id, origin_device_id,
                  orchestrator_device_id, target_device_id, hop_path, depth,
                  turn_count, capability, body, input_refs, requires_confirmation,
                  status, expires_at`,
      [taskId, principal.userId, input.status, input.outcome_code ?? null],
    );
    await client.query(
      "UPDATE pipeline_steps SET status = $3 WHERE user_id = $1 AND task_id = $2",
      [principal.userId, taskId, input.status],
    );
    if (["failed", "rejected", "expired"].includes(input.status) || (input.status === "done" && task.id === task.root_task_id)) {
      await client.query(
        `UPDATE pipelines SET status = $3::pipeline_status
          WHERE user_id = $1 AND id = (SELECT pipeline_id FROM tasks WHERE user_id = $1 AND id = $2)`,
        [principal.userId, taskId, input.status],
      );
    } else if (input.status === "running") {
      await client.query(
        `UPDATE pipelines SET status = 'running'
          WHERE user_id = $1
            AND id = (SELECT pipeline_id FROM tasks WHERE user_id = $1 AND id = $2)
            AND status = 'awaiting_approval'`,
        [principal.userId, taskId],
      );
    }
    await audit(principal.userId, "task.transitioned", principal.id, taskId, {
      status: input.status,
    }, client);
    return taskEnvelope(result.rows[0]);
  });
}

export async function createApproval(
  principal: { id: string; userId: string },
  taskId: string,
  input: { action_hash: string; tier: 4 | 5; preview_inbox_ids: string[] },
): Promise<{ approval_id: string; expires_at: string }> {
  return transaction(async (client) => {
    const task = await selectTask(client, principal.userId, taskId, true);
    if (task.target_device_id !== principal.id || !["claimed", "running", "awaiting_approval"].includes(task.status)) {
      throw new HttpError(409, "task_not_approvable", "Task is not eligible for approval");
    }
    await client.query(
      `UPDATE approvals SET status = 'expired'
        WHERE task_id = $1 AND user_id = $2 AND status IN ('pending', 'approved')`,
      [taskId, principal.userId],
    );
    const devices = await client.query<{ id: string }>(
      "SELECT id FROM devices WHERE user_id = $1 AND revoked_at IS NULL ORDER BY id",
      [principal.userId],
    );
    const packets = await client.query<{ id: string; target_device_id: string; expires_at: Date }>(
      `SELECT id, target_device_id, expires_at FROM inbox_items
        WHERE user_id = $1 AND id = ANY($2::uuid[])
          AND task_id = $3 AND source_device_id = $4
          AND acked_at IS NULL AND deleted_at IS NULL AND expires_at > now()`,
      [principal.userId, input.preview_inbox_ids, taskId, principal.id],
    );
    if (
      packets.rowCount !== devices.rowCount
      || devices.rows.some((device) => !packets.rows.some((packet) => packet.target_device_id === device.id))
    ) {
      throw new HttpError(400, "approval_preview_missing", "A matching encrypted preview is required for each active device");
    }
    const approvalId = randomUUID();
    const expiresAt = new Date(Math.min(
      Date.now() + 5 * 60_000,
      new Date(task.expires_at).getTime(),
      ...packets.rows.map((packet) => new Date(packet.expires_at).getTime()),
    ));
    if (expiresAt.getTime() <= Date.now()) throw new HttpError(409, "task_expired", "Task or preview has expired");
    await client.query(
      `INSERT INTO approvals
        (id, user_id, task_id, action_hash, tier, requested_by_device_id, expires_at)
       VALUES ($1, $2, $3, decode($4, 'hex'), $5, $6, $7)`,
      [approvalId, principal.userId, taskId, input.action_hash, input.tier, principal.id, expiresAt],
    );
    for (const packet of packets.rows) {
      await client.query(
        `INSERT INTO approval_packets (user_id, approval_id, approver_device_id, inbox_item_id)
         VALUES ($1, $2, $3, $4)`,
        [principal.userId, approvalId, packet.target_device_id, packet.id],
      );
    }
    await client.query(
      "UPDATE tasks SET status = 'awaiting_approval', updated_at = now() WHERE user_id = $1 AND id = $2",
      [principal.userId, taskId],
    );
    await client.query(
      `UPDATE pipelines SET status = 'awaiting_approval'
        WHERE user_id = $1 AND id = (SELECT pipeline_id FROM tasks WHERE user_id = $1 AND id = $2)`,
      [principal.userId, taskId],
    );
    await client.query(
      "UPDATE pipeline_steps SET status = 'awaiting_approval' WHERE user_id = $1 AND task_id = $2",
      [principal.userId, taskId],
    );
    await audit(principal.userId, "approval.requested", principal.id, taskId, {
      tier: input.tier,
      approval_id: approvalId,
      status: "pending",
      expires_at: expiresAt.toISOString(),
    }, client);
    return { approval_id: approvalId, expires_at: expiresAt.toISOString() };
  });
}

export async function decideApproval(
  principal: { id: string; userId: string },
  taskId: string,
  input: { approval_id: string; action_hash: string; decision: "approve" | "reject" },
): Promise<{ status: "approved" | "rejected" }> {
  return transaction(async (client) => {
    const task = await selectTask(client, principal.userId, taskId, true);
    if (task.status !== "awaiting_approval") {
      throw new HttpError(409, "approval_unavailable", "Task is no longer awaiting approval");
    }
    await client.query(
      `UPDATE approvals SET status = 'expired'
        WHERE task_id = $1 AND user_id = $2 AND status = 'pending' AND expires_at <= now()`,
      [taskId, principal.userId],
    );
    const result = await client.query<{ id: string }>(
      `UPDATE approvals a
          SET status = $5::approval_status,
              approved_by_device_id = $4,
              approved_at = CASE WHEN $5 = 'approved' THEN now() ELSE NULL END
        WHERE a.id = $1 AND a.user_id = $2 AND a.task_id = $3
          AND a.action_hash = decode($6, 'hex')
          AND a.status = 'pending' AND a.expires_at > now()
          AND EXISTS (
            SELECT 1 FROM devices d
             WHERE d.id = $4 AND d.user_id = a.user_id AND d.revoked_at IS NULL
          )
          AND EXISTS (
            SELECT 1 FROM approval_packets p
             WHERE p.approval_id = a.id AND p.approver_device_id = $4
          ) AND EXISTS (
            SELECT 1 FROM tasks t WHERE t.id = a.task_id AND t.user_id = a.user_id
              AND t.status = 'awaiting_approval'
          )
        RETURNING a.id`,
      [
        input.approval_id,
        principal.userId,
        taskId,
        principal.id,
        input.decision === "approve" ? "approved" : "rejected",
        input.action_hash,
      ],
    );
    if (!result.rowCount) throw new HttpError(409, "approval_unavailable", "Approval is expired, used, or not available to this device");
    if (input.decision === "reject") {
      await client.query(
        `UPDATE tasks SET status = 'rejected', updated_at = now()
          WHERE user_id = $1 AND id = $2 AND status = 'awaiting_approval'`,
        [principal.userId, taskId],
      );
      await client.query(
        `UPDATE pipelines SET status = 'rejected'
          WHERE user_id = $1 AND id = (SELECT pipeline_id FROM tasks WHERE user_id = $1 AND id = $2)`,
        [principal.userId, taskId],
      );
      await client.query(
        "UPDATE pipeline_steps SET status = 'rejected' WHERE user_id = $1 AND task_id = $2",
        [principal.userId, taskId],
      );
    }
    await audit(principal.userId, "approval.decided", principal.id, taskId, {
      approval_id: input.approval_id,
      status: input.decision === "approve" ? "approved" : "rejected",
    }, client);
    return { status: input.decision === "approve" ? "approved" : "rejected" };
  });
}
