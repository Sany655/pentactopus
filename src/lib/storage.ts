import { randomUUID, timingSafeEqual } from "node:crypto";
import { audit } from "./audit";
import { query, transaction } from "./db";
import { HttpError } from "./http";
import { MAX_CIPHERTEXT_BYTES, MAX_INBOX_TTL_MS, redis } from "./redis";
import { sha256 } from "./security";

type Principal = { id: string; userId: string };

function decodeCiphertext(value: string): Buffer {
  if (!/^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$/.test(value)) {
    throw new HttpError(400, "invalid_ciphertext", "Ciphertext must be canonical base64");
  }
  const bytes = Buffer.from(value, "base64");
  if (bytes.byteLength < 1 || bytes.byteLength > MAX_CIPHERTEXT_BYTES || bytes.toString("base64") !== value) {
    throw new HttpError(413, "invalid_ciphertext_size", "Ciphertext must be between 1 byte and 1 MiB");
  }
  return bytes;
}

export function calculateTtlExpiry(
  requestedMs: number,
  taskExpiryMs: number,
  maximumMs: number,
  nowMs = Date.now(),
): { date: Date; ttl: number } {
  if (!Number.isFinite(requestedMs) || requestedMs <= nowMs) {
    throw new HttpError(400, "invalid_expiry", "Expiry must be in the future");
  }
  const time = Math.min(requestedMs, taskExpiryMs, nowMs + maximumMs);
  if (time <= nowMs) throw new HttpError(400, "invalid_expiry", "Resource expiry has passed");
  return { date: new Date(time), ttl: Math.max(1, Math.floor(time - nowMs)) };
}

function boundedExpiry(requested: string, taskExpiry: Date, maximumMs: number): { date: Date; ttl: number } {
  return calculateTtlExpiry(Date.parse(requested), taskExpiry.getTime(), maximumMs);
}

async function ensureTaskAccess(
  principal: Principal,
  taskId: string,
  targetDeviceId: string,
): Promise<{ expires_at: Date }> {
  const result = await query<{ expires_at: Date }>(
    `SELECT expires_at FROM tasks
      WHERE user_id = $1 AND id = $2
        AND $3::uuid IN (origin_device_id, orchestrator_device_id, target_device_id)`,
    [principal.userId, taskId, principal.id],
  );
  if (!result.rows[0]) throw new HttpError(404, "not_found", "Task not found");
  const target = await query(
    "SELECT id FROM devices WHERE id = $1 AND user_id = $2 AND revoked_at IS NULL",
    [targetDeviceId, principal.userId],
  );
  if (!target.rowCount) throw new HttpError(404, "not_found", "Target device not found");
  return result.rows[0];
}

export async function createInbox(
  principal: Principal,
  input: {
    task_id: string;
    target_device_id: string;
    ciphertext_b64: string;
    expires_at: string;
  },
): Promise<{ inbox_id: string; sha256: string; expires_at: string }> {
  const bytes = decodeCiphertext(input.ciphertext_b64);
  const task = await ensureTaskAccess(principal, input.task_id, input.target_device_id);
  const expiry = boundedExpiry(input.expires_at, task.expires_at, MAX_INBOX_TTL_MS);
  const id = randomUUID();
  const key = `inbox:${id}`;
  const digest = sha256(bytes);
  await redis().set(key, input.ciphertext_b64, { px: expiry.ttl });
  try {
    await transaction(async (client) => {
      await client.query(
        `INSERT INTO inbox_items
          (id, user_id, source_device_id, target_device_id, task_id, redis_key,
           ciphertext_sha256, byte_length, expires_at)
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)`,
        [id, principal.userId, principal.id, input.target_device_id, input.task_id, key, digest, bytes.byteLength, expiry.date],
      );
      await audit(principal.userId, "inbox.created", principal.id, input.task_id, {
        inbox_id: id,
        target_device_id: input.target_device_id,
        byte_length: bytes.byteLength,
        expires_at: expiry.date.toISOString(),
      }, client);
    });
  } catch (error) {
    await redis().del(key);
    throw error;
  }
  return { inbox_id: id, sha256: digest.toString("hex"), expires_at: expiry.date.toISOString() };
}

export async function readInbox(
  principal: Principal,
  inboxId: string,
): Promise<{ ciphertext_b64: string; sha256: string; expires_at: string }> {
  const result = await query<{
    redis_key: string;
    ciphertext_sha256: Buffer;
    byte_length: number;
    expires_at: Date;
    task_id: string;
  }>(
    `SELECT redis_key, ciphertext_sha256, byte_length, expires_at, task_id
       FROM inbox_items
      WHERE id = $1 AND user_id = $2 AND target_device_id = $3
        AND acked_at IS NULL AND deleted_at IS NULL AND expires_at > now()`,
    [inboxId, principal.userId, principal.id],
  );
  const item = result.rows[0];
  if (!item) throw new HttpError(404, "not_found", "Inbox item not found");
  const ciphertext = await redis().get<string>(item.redis_key);
  if (typeof ciphertext !== "string") {
    await query("UPDATE inbox_items SET deleted_at = now() WHERE id = $1 AND deleted_at IS NULL", [inboxId]);
    throw new HttpError(404, "not_found", "Inbox item not found");
  }
  const bytes = decodeCiphertext(ciphertext);
  const digest = sha256(bytes);
  if (
    bytes.byteLength !== Number(item.byte_length)
    || digest.byteLength !== item.ciphertext_sha256.byteLength
    || !timingSafeEqual(digest, item.ciphertext_sha256)
  ) {
    await redis().del(item.redis_key);
    await query("UPDATE inbox_items SET deleted_at = now() WHERE id = $1 AND deleted_at IS NULL", [inboxId]);
    throw new HttpError(500, "ciphertext_integrity_error", "Encrypted content is unavailable");
  }
  return {
    ciphertext_b64: ciphertext,
    sha256: digest.toString("hex"),
    expires_at: new Date(item.expires_at).toISOString(),
  };
}

export async function acknowledgeInbox(principal: Principal, inboxId: string): Promise<void> {
  const item = await query<{ redis_key: string; task_id: string }>(
    `SELECT redis_key, task_id FROM inbox_items
      WHERE id = $1 AND user_id = $2 AND target_device_id = $3
        AND acked_at IS NULL AND deleted_at IS NULL`,
    [inboxId, principal.userId, principal.id],
  );
  if (!item.rows[0]) throw new HttpError(404, "not_found", "Inbox item not found");
  await redis().del(item.rows[0].redis_key);
  await transaction(async (client) => {
    await client.query(
      `UPDATE inbox_items SET acked_at = now(), deleted_at = now()
        WHERE id = $1 AND user_id = $2 AND target_device_id = $3
          AND acked_at IS NULL AND deleted_at IS NULL`,
      [inboxId, principal.userId, principal.id],
    );
    await audit(principal.userId, "inbox.acknowledged", principal.id, item.rows[0].task_id, {
      inbox_id: inboxId,
    }, client);
  });
}

export async function createArtifact(
  principal: Principal,
  input: {
    task_id: string;
    intended_device_id: string;
    ciphertext_b64: string;
    media_type: string;
    expires_at: string;
  },
): Promise<{ artifact_id: string; sha256: string; expires_at: string }> {
  const bytes = decodeCiphertext(input.ciphertext_b64);
  const task = await ensureTaskAccess(principal, input.task_id, input.intended_device_id);
  const expiry = boundedExpiry(input.expires_at, task.expires_at, 24 * 60 * 60 * 1000);
  const id = randomUUID();
  const key = `artifact:${id}`;
  const digest = sha256(bytes);
  await redis().set(key, input.ciphertext_b64, { px: expiry.ttl });
  try {
    await transaction(async (client) => {
      await client.query(
        `INSERT INTO artifacts
          (id, user_id, task_id, created_by_device_id, intended_device_id, redis_key,
           ciphertext_sha256, byte_length, media_type, expires_at)
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)`,
        [
          id, principal.userId, input.task_id, principal.id, input.intended_device_id,
          key, digest, bytes.byteLength, input.media_type, expiry.date,
        ],
      );
      await client.query(
        `UPDATE pipeline_steps SET output_artifact_id = $3
          WHERE user_id = $1 AND task_id = $2`,
        [principal.userId, input.task_id, id],
      );
      await audit(principal.userId, "artifact.created", principal.id, input.task_id, {
        artifact_id: id,
        target_device_id: input.intended_device_id,
        byte_length: bytes.byteLength,
        expires_at: expiry.date.toISOString(),
      }, client);
    });
  } catch (error) {
    await redis().del(key);
    throw error;
  }
  return { artifact_id: id, sha256: digest.toString("hex"), expires_at: expiry.date.toISOString() };
}

export async function readArtifact(
  principal: Principal,
  artifactId: string,
): Promise<{ ciphertext_b64: string; media_type: string; sha256: string; expires_at: string }> {
  const result = await query<{
    redis_key: string;
    ciphertext_sha256: Buffer;
    byte_length: number;
    media_type: string;
    expires_at: Date;
  }>(
    `SELECT redis_key, ciphertext_sha256, byte_length, media_type, expires_at
       FROM artifacts
      WHERE id = $1 AND user_id = $2 AND intended_device_id = $3
        AND deleted_at IS NULL AND expires_at > now()`,
    [artifactId, principal.userId, principal.id],
  );
  const artifact = result.rows[0];
  if (!artifact) throw new HttpError(404, "not_found", "Artifact not found");
  const ciphertext = await redis().get<string>(artifact.redis_key);
  if (typeof ciphertext !== "string") {
    await query("UPDATE artifacts SET deleted_at = now() WHERE id = $1 AND deleted_at IS NULL", [artifactId]);
    throw new HttpError(404, "not_found", "Artifact not found");
  }
  const bytes = decodeCiphertext(ciphertext);
  const digest = sha256(bytes);
  if (
    bytes.byteLength !== Number(artifact.byte_length)
    || !timingSafeEqual(digest, artifact.ciphertext_sha256)
  ) {
    await redis().del(artifact.redis_key);
    await query("UPDATE artifacts SET deleted_at = now() WHERE id = $1 AND deleted_at IS NULL", [artifactId]);
    throw new HttpError(500, "ciphertext_integrity_error", "Encrypted content is unavailable");
  }
  return {
    ciphertext_b64: ciphertext,
    media_type: artifact.media_type,
    sha256: digest.toString("hex"),
    expires_at: new Date(artifact.expires_at).toISOString(),
  };
}
