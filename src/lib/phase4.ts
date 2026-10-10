import { createHash } from "node:crypto";
import { appendDelegation, initialTaskPath } from "./task-rules";

export type SimulatedDevice = {
  id: string;
  platform: "windows" | "android";
  name: string;
  isGaming?: boolean;
};

export type ArtifactRef = {
  id: string;
  created_by: string;
  intended_device_id: string;
  media_type: "text/plain" | "application/json";
  byte_length: number;
};

export type ApprovalPayload = {
  task_id: string;
  recipient: string;
  text: string;
  channel: "whatsapp" | "sms" | "email";
};

export function stableJsonStringify(value: unknown): string {
  return JSON.stringify(value, (_, entry) => {
    if (entry && typeof entry === "object" && !Array.isArray(entry)) {
      return Object.fromEntries(Object.entries(entry).sort(([left], [right]) => left.localeCompare(right)));
    }
    return entry;
  });
}

export function exactApprovalHash(payload: ApprovalPayload): string {
  return createHash("sha256").update(stableJsonStringify(payload), "utf8").digest("hex");
}

export function deviceActionAllowed(
  device: SimulatedDevice,
  capability: string,
  tier: number,
): boolean {
  const gamingRestricted = device.isGaming && capability === "read_message_content" && tier >= 2;
  if (gamingRestricted) {
    return false;
  }
  return true;
}

export function buildMessageReadTask(orchestratorDeviceId: string, targetDeviceId: string, messageId: string): {
  taskPath: string[];
  depth: number;
  messageId: string;
  artifact: ArtifactRef;
} {
  const { hopPath, depth } = initialTaskPath(orchestratorDeviceId, targetDeviceId);
  return {
    taskPath: hopPath,
    depth,
    messageId,
    artifact: {
      id: `artifact-${messageId}`,
      created_by: targetDeviceId,
      intended_device_id: orchestratorDeviceId,
      media_type: "text/plain",
      byte_length: 256,
    },
  };
}

export function buildDelegatedPipeline(
  orchestratorDeviceId: string,
  targetDeviceId: string,
  messageId: string,
): { taskPath: string[]; depth: number; inputRefs: string[]; artifact: ArtifactRef } {
  const { hopPath, depth } = initialTaskPath(orchestratorDeviceId, targetDeviceId);
  const delegated = appendDelegation(hopPath, depth, "device-c");
  if (!delegated) {
    throw new Error("Delegation path is invalid for the simulated test case");
  }
  const artifact: ArtifactRef = {
    id: `artifact-${messageId}-processed`,
    created_by: targetDeviceId,
    intended_device_id: "device-c",
    media_type: "application/json",
    byte_length: 512,
  };
  return {
    taskPath: delegated.hopPath,
    depth: delegated.depth,
    inputRefs: [artifact.id],
    artifact,
  };
}

export function verifyApproval(payload: ApprovalPayload, expectedHash: string): boolean {
  return exactApprovalHash(payload) === expectedHash;
}

export function simulateReadRequest(
  requestingDevice: SimulatedDevice,
  targetDevice: SimulatedDevice,
  messageId: string,
  capability: "read_message_metadata" | "read_message_content" = "read_message_content",
): { allowed: boolean; reason?: string; task: ReturnType<typeof buildMessageReadTask> } {
  const tier = capability === "read_message_metadata" ? 1 : 2;
  const allowed = deviceActionAllowed(requestingDevice, capability, tier) && deviceActionAllowed(targetDevice, capability, tier);
  if (!allowed) {
    return {
      allowed: false,
      reason: requestingDevice.isGaming ? "device is in active gaming mode and read content is blocked" : "target device is unavailable",
      task: buildMessageReadTask(requestingDevice.id, targetDevice.id, messageId),
    };
  }
  return {
    allowed: true,
    task: buildMessageReadTask(requestingDevice.id, targetDevice.id, messageId),
  };
}

export function simulateApprovalDecision(
  approvingDevice: SimulatedDevice,
  payload: ApprovalPayload,
  accepted: boolean,
): { approved: boolean; hash: string; approver: string } {
  const hash = exactApprovalHash(payload);
  return {
    approved: accepted && approvingDevice.platform === "android",
    hash,
    approver: approvingDevice.id,
  };
}
