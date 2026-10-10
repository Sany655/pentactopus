import assert from "node:assert/strict";
import { randomUUID, generateKeyPairSync, sign } from "node:crypto";
import { readFile } from "node:fs/promises";
import { resolve } from "node:path";
import test from "node:test";
import { Pool } from "@neondatabase/serverless";
import { canonicalDeviceMessage, safeEqualHex, verifyDeviceSignature } from "../src/lib/security";
import { appendDelegation, canTransition, initialTaskPath } from "../src/lib/task-rules";
import { calculateTtlExpiry } from "../src/lib/storage";
import { MAX_CIPHERTEXT_BYTES } from "../src/lib/redis";
import { validateApiPayload, validateTaskEnvelope } from "../src/lib/contracts";

test("device signature canonicalization covers method, path, nonce and exact body digest", () => {
  const { privateKey, publicKey } = generateKeyPairSync("ed25519");
  const encodedKey = Buffer.from(publicKey.export({ type: "spki", format: "der" })).subarray(-32);
  const body = Buffer.from('{"value":"metadata"}');
  const message = canonicalDeviceMessage("post", "/api/v1/tasks?x=1", "1770000000", "dGhpcy1ub25jZS1zaG91bGQtYmUtcmFuZG9t", body);
  const signature = sign(null, Buffer.from(message), privateKey);

  assert.equal(verifyDeviceSignature(encodedKey, message, signature), true);
  assert.equal(verifyDeviceSignature(encodedKey, `${message}\n`, signature), false);
  assert.notEqual(
    canonicalDeviceMessage("POST", "/api/v1/tasks?x=1", "1770000000", "different-random-nonce-1234", body),
    message,
  );
  assert.equal(safeEqualHex("a".repeat(64), "a".repeat(64)), true);
  assert.equal(safeEqualHex("a".repeat(64), "b".repeat(64)), false);
});

test("task path rules prevent revisits and delegation beyond depth two", () => {
  const root = initialTaskPath("device-a", "device-a");
  assert.deepEqual(root, { hopPath: ["device-a"], depth: 0 });
  const first = appendDelegation(root.hopPath, root.depth, "device-b");
  assert.deepEqual(first, { hopPath: ["device-a", "device-b"], depth: 1 });
  const second = appendDelegation(first!.hopPath, first!.depth, "device-c");
  assert.deepEqual(second, { hopPath: ["device-a", "device-b", "device-c"], depth: 2 });
  assert.equal(appendDelegation(second!.hopPath, second!.depth, "device-d"), null);
  assert.equal(appendDelegation(first!.hopPath, first!.depth, "device-a"), null);
  assert.equal(appendDelegation(["device-a", "device-b"], 0, "device-c"), null);

  assert.equal(canTransition("queued", "claimed"), false);
  assert.equal(canTransition("claimed", "running"), true);
  assert.equal(canTransition("done", "running"), false);
});

test("encrypted-object expiry is bounded by request, task and ten-minute cap", () => {
  const now = 1_770_000_000_000;
  const capped = calculateTtlExpiry(now + 30 * 60_000, now + 60 * 60_000, 10 * 60_000, now);
  assert.equal(capped.date.getTime(), now + 10 * 60_000);
  assert.equal(capped.ttl, 10 * 60_000);
  const taskCapped = calculateTtlExpiry(now + 30 * 60_000, now + 90_000, 10 * 60_000, now);
  assert.equal(taskCapped.date.getTime(), now + 90_000);
  assert.equal(taskCapped.ttl, 90_000);
  assert.throws(() => calculateTtlExpiry(now, now + 1000, 10_000, now));
  assert.equal(MAX_CIPHERTEXT_BYTES, 1_048_576);
});

test("shared API and task-envelope schemas accept valid wire payloads and reject malformed ones", () => {
  const taskCreate = {
    target_device_id: "123e4567-e89b-42d3-a456-426614174000",
    parent_task_id: "123e4567-e89b-42d3-a456-426614174001",
    capability: "metadata.read",
    body: { mode: "unread_count" },
    input_refs: [],
    requires_confirmation: false,
    expires_at: "2027-01-01T00:00:00.000Z",
  };
  assert.equal(validateApiPayload("taskCreate", taskCreate), true);
  assert.equal(validateApiPayload("taskCreate", { ...taskCreate, unexpected: "value" }), false);
  assert.equal(validateApiPayload("taskCreate", { ...taskCreate, body: { note: "private message" } }), false);
  assert.equal(validateApiPayload("taskCreate", { ...taskCreate, target_device_id: "invalid" }), false);

  const envelope = {
    schema_version: "1.0.3",
    task_id: taskCreate.target_device_id,
    root_task_id: taskCreate.target_device_id,
    parent_task_id: null,
    origin_device_id: taskCreate.target_device_id,
    orchestrator_device_id: taskCreate.target_device_id,
    target_device_id: taskCreate.target_device_id,
    hop_path: [taskCreate.target_device_id],
    depth: 0,
    turn_count: 1,
    capability: "metadata.read",
    body: { mode: "unread_count" },
    input_refs: [],
    requires_confirmation: false,
    status: "queued",
    expires_at: "2027-01-01T00:00:00.000Z",
  };
  assert.equal(validateTaskEnvelope(envelope), true);
  assert.equal(validateTaskEnvelope({ ...envelope, depth: 3 }), false);
});

const testDatabaseUrl = process.env.TEST_DATABASE_URL;

test("PostgreSQL enforces ownership, single claim, nonce replay, expiry, and approval hash", {
  skip: !testDatabaseUrl ? "Set TEST_DATABASE_URL to run isolated PostgreSQL integration tests" : false,
}, async () => {
  if (!testDatabaseUrl) return;
  const db = new Pool({ connectionString: testDatabaseUrl, max: 4 });
  const schema = `pt_test_${randomUUID().replaceAll("-", "")}`;
  await db.query(`CREATE SCHEMA "${schema}"`);
  const admin = await db.connect();
  try {
    await admin.query(`SET search_path TO "${schema}"`);
    const migration = await readFile(resolve(process.cwd(), "migrations", "0001_v1_core.sql"), "utf8");
    for (const statement of migration.split(";").map((item) => item.trim()).filter(Boolean)) {
      await admin.query(statement);
    }

    const userA = randomUUID();
    const userB = randomUUID();
    const deviceA = randomUUID();
    const deviceB = randomUUID();
    const now = new Date();
    await admin.query("INSERT INTO users (id, email) VALUES ($1, $2), ($3, $4)", [
      userA, `${userA}@integration.invalid`, userB, `${userB}@integration.invalid`,
    ]);
    await admin.query(
      `INSERT INTO devices (id, user_id, name, platform, public_key)
       VALUES ($1, $2, 'device-a', 'windows', $3), ($4, $5, 'device-b', 'android', $6)`,
      [deviceA, userA, Buffer.alloc(32, 1), deviceB, userB, Buffer.alloc(32, 2)],
    );

    const taskIds: string[] = [];
    for (let index = 0; index < 2; index += 1) {
      const taskId = randomUUID();
      const pipelineId = randomUUID();
      taskIds.push(taskId);
      await admin.query("BEGIN");
      await admin.query(
        `INSERT INTO pipelines (id, user_id, root_task_id, orchestrator_device_id, expires_at)
         VALUES ($1, $2, $3, $4, now() + interval '1 hour')`,
        [pipelineId, userA, taskId, deviceA],
      );
      await admin.query(
        `INSERT INTO tasks
          (id, user_id, pipeline_id, root_task_id, origin_device_id, orchestrator_device_id,
           target_device_id, hop_path, depth, turn_count, capability, body, expires_at)
         VALUES ($1, $2, $3, $1, $4, $4, $4, ARRAY[$4]::uuid[], 0, 1,
                 'metadata.read', '{}'::jsonb, now() + interval '1 hour')`,
        [taskId, userA, pipelineId, deviceA],
      );
      await admin.query("COMMIT");
    }
    const otherTask = randomUUID();
    const otherPipeline = randomUUID();
    await admin.query("BEGIN");
    await admin.query(
      `INSERT INTO pipelines (id, user_id, root_task_id, orchestrator_device_id, expires_at)
       VALUES ($1, $2, $3, $4, now() + interval '1 hour')`,
      [otherPipeline, userB, otherTask, deviceB],
    );
    await admin.query(
      `INSERT INTO tasks
        (id, user_id, pipeline_id, root_task_id, origin_device_id, orchestrator_device_id,
         target_device_id, hop_path, depth, turn_count, capability, body, expires_at)
       VALUES ($1, $2, $3, $1, $4, $4, $4, ARRAY[$4]::uuid[], 0, 1,
               'metadata.read', '{}'::jsonb, now() + interval '1 hour')`,
      [otherTask, userB, otherPipeline, deviceB],
    );
    await admin.query("COMMIT");

    const isolated = await admin.query(
      "SELECT id FROM tasks WHERE id = $1 AND user_id = $2",
      [taskIds[0], userB],
    );
    assert.equal(isolated.rowCount, 0);

    const claimSql = `UPDATE tasks t SET status = 'claimed', claimed_at = now()
      WHERE t.id = $1 AND t.user_id = $2 AND t.target_device_id = $3
        AND t.status = 'queued' AND t.expires_at > now()
        AND NOT EXISTS (SELECT 1 FROM tasks active
          WHERE active.target_device_id = t.target_device_id
            AND active.status IN ('claimed', 'awaiting_approval', 'running'))
      RETURNING t.id`;
    const claimOne = await db.connect();
    const claimTwo = await db.connect();
    try {
      await Promise.all([
        claimOne.query(`SET search_path TO "${schema}"`),
        claimTwo.query(`SET search_path TO "${schema}"`),
      ]);
      const claims = await Promise.allSettled([
        claimOne.query(claimSql, [taskIds[0], userA, deviceA]),
        claimTwo.query(claimSql, [taskIds[1], userA, deviceA]),
      ]);
      const successes = claims.filter((claim) => claim.status === "fulfilled" && claim.value.rowCount === 1);
      const conflicts = claims.filter((claim) => claim.status === "rejected" && (claim.reason as { code?: string }).code === "23505");
      assert.equal(successes.length, 1);
      assert.ok(conflicts.length <= 1);
    } finally {
      claimOne.release();
      claimTwo.release();
    }

    const nonce = "integration-nonce-value-123456";
    const insertNonce = () => admin.query(
      `INSERT INTO device_nonces (device_id, nonce, request_timestamp, expires_at)
       VALUES ($1, $2, now(), now() + interval '10 minutes')
       ON CONFLICT (device_id, nonce) DO NOTHING RETURNING nonce`,
      [deviceA, nonce],
    );
    assert.equal((await insertNonce()).rowCount, 1);
    assert.equal((await insertNonce()).rowCount, 0);

    const claimedTask = await admin.query<{ id: string }>(
      "SELECT id FROM tasks WHERE user_id = $1 AND target_device_id = $2 AND status = 'claimed' LIMIT 1",
      [userA, deviceA],
    );
    const approvalId = randomUUID();
    const expectedHash = "11".repeat(32);
    await admin.query(
      `INSERT INTO approvals
        (id, user_id, task_id, action_hash, tier, requested_by_device_id, expires_at, status)
       VALUES ($1, $2, $3, decode($4, 'hex'), 4, $5, now() + interval '5 minutes', 'approved')`,
      [approvalId, userA, claimedTask.rows[0].id, expectedHash, deviceA],
    );
    const wrongHash = await admin.query(
      `UPDATE approvals SET status = 'used', used_at = now()
        WHERE id = $1 AND action_hash = decode($2, 'hex') AND status = 'approved'
        RETURNING id`,
      [approvalId, "22".repeat(32)],
    );
    assert.equal(wrongHash.rowCount, 0);
    const exactHash = await admin.query(
      `UPDATE approvals SET status = 'used', used_at = now()
        WHERE id = $1 AND action_hash = decode($2, 'hex') AND status = 'approved'
        RETURNING id`,
      [approvalId, expectedHash],
    );
    assert.equal(exactHash.rowCount, 1);

    const expiredInbox = randomUUID();
    await admin.query(
      `INSERT INTO inbox_items
        (id, user_id, source_device_id, target_device_id, task_id, redis_key,
         ciphertext_sha256, byte_length, expires_at)
       VALUES ($1, $2, $3, $3, $4, $5, $6, 1, now() + interval '1 millisecond')`,
      [expiredInbox, userA, deviceA, claimedTask.rows[0].id, `test:${expiredInbox}`, Buffer.alloc(32, 0)],
    );
    await new Promise((resolveDelay) => setTimeout(resolveDelay, 20));
    const unavailable = await admin.query(
      "SELECT id FROM inbox_items WHERE id = $1 AND expires_at > now() AND deleted_at IS NULL",
      [expiredInbox],
    );
    assert.equal(unavailable.rowCount, 0);
  } finally {
    admin.release();
    await db.query(`DROP SCHEMA "${schema}" CASCADE`);
    await db.end();
  }
});
