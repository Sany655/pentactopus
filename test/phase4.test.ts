import assert from "node:assert/strict";
import test from "node:test";

import {
  buildDelegatedPipeline,
  buildMessageReadTask,
  deviceActionAllowed,
  exactApprovalHash,
  type ApprovalPayload,
  verifyApproval,
} from "../src/lib/phase4";

test("Phase 4 helper logic models device read and delegation constraints", () => {
  const pc = { id: "pc", platform: "windows", name: "gaming-pc", isGaming: true } as const;
  const phone = { id: "phone", platform: "android", name: "phone" } as const;

  assert.equal(deviceActionAllowed(pc, "read_message_content", 2), false);
  assert.equal(deviceActionAllowed(phone, "read_message_content", 2), true);

  const readTask = buildMessageReadTask(pc.id, phone.id, "msg-42");
  assert.deepEqual(readTask.taskPath, [pc.id, phone.id]);
  assert.equal(readTask.depth, 1);
  assert.equal(readTask.artifact.intended_device_id, pc.id);

  const pipeline = buildDelegatedPipeline(pc.id, phone.id, "msg-42");
  assert.deepEqual(pipeline.taskPath, [pc.id, phone.id, "device-c"]);
  assert.equal(pipeline.depth, 2);
  assert.equal(pipeline.inputRefs[0], pipeline.artifact.id);
});

test("Phase 4 e2e simulation covers pc-phone message read and gaming denial", () => {
  const pc = { id: "pc", platform: "windows", name: "gaming-pc", isGaming: true } as const;
  const phone = { id: "phone", platform: "android", name: "phone" } as const;

  const pcAsksPhone = buildMessageReadTask(pc.id, phone.id, "msg-77");
  assert.deepEqual(pcAsksPhone.taskPath, [pc.id, phone.id]);

  const phoneReadsPcWhileGaming = buildMessageReadTask(phone.id, pc.id, "msg-88");
  assert.equal(deviceActionAllowed(pc, "read_message_content", 2), false);
  assert.equal(deviceActionAllowed(phone, "read_message_content", 2), true);
  assert.equal(phoneReadsPcWhileGaming.artifact.intended_device_id, phone.id);
});

test("Phase 4 approval hashes bind the exact outbound payload", () => {
  const payload: ApprovalPayload = {
    task_id: "task-123",
    recipient: "+15550001234",
    text: "Hello world",
    channel: "whatsapp",
  };
  const hash = exactApprovalHash(payload);
  assert.equal(verifyApproval(payload, hash), true);
  assert.equal(
    verifyApproval({ ...payload, text: "Hello world!" }, hash),
    false,
  );
});

test("Phase 4 simulation includes delegated artifact pipeline and phone approval", () => {
  const pc = { id: "pc", platform: "windows", name: "gaming-pc" } as const;
  const phone = { id: "phone", platform: "android", name: "phone" } as const;
  const pipeline = buildDelegatedPipeline(pc.id, phone.id, "msg-100");
  const payload: ApprovalPayload = {
    task_id: "task-approval",
    recipient: "+15550009999",
    text: "We are sending the approved message.",
    channel: "whatsapp",
  };
  const approval = { approved: true, hash: exactApprovalHash(payload), approver: phone.id };

  assert.equal(pipeline.depth, 2);
  assert.equal(pipeline.inputRefs.length, 1);
  assert.equal(approval.approved, true);
  assert.equal(verifyApproval(payload, approval.hash), true);
});
