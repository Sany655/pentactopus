export type TaskStatus =
  | "queued"
  | "claimed"
  | "awaiting_approval"
  | "running"
  | "done"
  | "failed"
  | "rejected"
  | "expired";

const TRANSITIONS: Record<TaskStatus, readonly TaskStatus[]> = {
  queued: [],
  claimed: ["awaiting_approval", "running", "failed", "expired"],
  awaiting_approval: ["running", "rejected", "failed", "expired"],
  running: ["awaiting_approval", "done", "failed", "expired"],
  done: [],
  failed: [],
  rejected: [],
  expired: [],
};

export function initialTaskPath(originDeviceId: string, targetDeviceId: string): {
  hopPath: string[];
  depth: number;
} {
  const hopPath = originDeviceId === targetDeviceId
    ? [originDeviceId]
    : [originDeviceId, targetDeviceId];
  return { hopPath, depth: hopPath.length - 1 };
}

export function appendDelegation(
  hopPath: string[],
  depth: number,
  targetDeviceId: string,
): { hopPath: string[]; depth: number } | null {
  if (depth < 0 || depth > 2 || hopPath.length !== depth + 1 || hopPath.includes(targetDeviceId) || depth >= 2) {
    return null;
  }
  return { hopPath: [...hopPath, targetDeviceId], depth: depth + 1 };
}

export function canTransition(from: TaskStatus, to: TaskStatus): boolean {
  return TRANSITIONS[from].includes(to);
}
